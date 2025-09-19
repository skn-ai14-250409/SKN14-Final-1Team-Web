# uauth/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError, transaction
from .models import User
import json
import re
from datetime import date
from .models import User
from .models import User, ApprovalLog, Status

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ApprovalLog
from .models import Status
from .models import User, Status
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .aws_s3_service import S3Client


from .models import User, Rank, Department, Gender


# -----------------------------
# 유틸
# -----------------------------
def _wants_json(request):
    accept = request.headers.get("Accept", "")
    xrw = request.headers.get("X-Requested-With", "")
    return "application/json" in accept or xrw == "XMLHttpRequest"


# 서버측 검증용(선택)
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{4,20}$")
PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
PHONE_RE = re.compile(r"^010-\d{4}-\d{4}$")
MIN_BIRTH = date(1900, 1, 1)


# -----------------------------
# 로그아웃
# -----------------------------
@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("uauth:login")


# -----------------------------
# 로그인
# -----------------------------
@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    user = request.user
    if user.is_authenticated and user.status == "approved":
        return redirect("main:home")
    if request.method == "GET":
        return render(request, "uauth/login.html")

    # --- POST ---
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    # 필드 유효성(프런트와 동일 규칙)
    field_errors = {}
    if not username:
        field_errors["username"] = ["아이디를 입력해주세요."]
    elif len(username) < 3:
        field_errors["username"] = ["아이디는 3자 이상이어야 합니다."]
    if not password:
        field_errors["password"] = ["비밀번호를 입력해주세요."]
    elif len(password) < 4:
        field_errors["password"] = ["비밀번호는 4자 이상이어야 합니다."]

    if field_errors:
        if _wants_json(request):
            return JsonResponse(
                {"success": False, "field_errors": field_errors}, status=400
            )
        for _, msgs in field_errors.items():
            messages.error(request, msgs[0])
        return render(request, "uauth/login.html", {"username": username})

    user = authenticate(request, username=username, password=password)

    # ▼▼▼ 여기부터 교체 ▼▼▼
    if user is None:
        # 아이디/비밀번호 오류
        msg = "아이디 또는 비밀번호가 올바르지 않습니다."
        if _wants_json(request):
            return JsonResponse({"success": False, "message": msg}, status=400)
        return render(request, "uauth/login.html", {"username": username, "error": msg})

    # 인증 성공: 세션 로그인 후 승인 상태에 따라 라우팅
    login(request, user)

    # 최신 승인 상태(로그가 있으면 로그, 없으면 유저.status)
    latest_log = ApprovalLog.objects.filter(user=user).order_by("-created_at").first()
    current_status = latest_log.action if latest_log else user.status

    if current_status == Status.PENDING:
        if _wants_json(request):
            return JsonResponse(
                {
                    "success": True,
                    "state": "pending",
                    "redirect_url": reverse("uauth:pending"),
                }
            )
        return redirect("uauth:pending")

    if current_status == Status.REJECTED:
        if _wants_json(request):
            return JsonResponse(
                {
                    "success": True,
                    "state": "rejected",
                    "redirect_url": reverse("uauth:reject"),
                }
            )
        return redirect("uauth:reject")

    # APPROVED (기본)
    if _wants_json(request):
        return JsonResponse(
            {"success": True, "state": "approved", "redirect_url": reverse("main:home")}
        )
    return redirect("main:home")
    # ▲▲▲ 여기까지 교체 ▲▲▲


# -----------------------------
# 회원가입
# -----------------------------
from django import forms


class SignUpEchoForm(forms.Form):
    # 템플릿에서 form.userId.value 같은 접근을 위해 필드 선언
    userId = forms.CharField(required=True)
    name = forms.CharField(required=True)
    password = forms.CharField(required=True)
    confirmPassword = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    team = forms.CharField(required=False)
    role = forms.CharField(required=True)
    birthDate = forms.DateField(required=True)
    gender = forms.CharField(required=True)
    phoneNumber = forms.CharField(required=True)
    profile_image = forms.ImageField(required=False)


def signup_context(form=None):
    return {
        "form": form or SignUpEchoForm(),
        "departments": Department.choices,
        "ranks": Rank.choices,
        "genders": Gender.choices,
    }


@csrf_protect
@require_http_methods(["GET", "POST"])
def signup_view(request: HttpRequest):
    # GET
    if request.method == "GET":
        return render(request, "uauth/register2.html", signup_context())

    # POST
    form = SignUpEchoForm(request.POST)
    if form.errors:
        return render(request, "uauth/register2.html", signup_context(form))

    # 값 추출
    userId = form.data.get("userId", "").strip()
    name = form.data.get("name", "").strip()
    password = form.data.get("password", "")
    confirm = form.data.get("confirmPassword", "")
    email = form.data.get("email", "").strip()
    role = form.data.get("role", "").strip()

    team_raw = request.POST.get("team")
    team = team_raw.strip() if team_raw else None
    if role.lower() == "cto":
        team = None

    birth_raw = form.data.get("birthDate") or ""
    birth_dt = parse_date(birth_raw)
    gender = form.data.get("gender", "").strip()
    phone = form.data.get("phoneNumber", "").strip()
    profile_image = request.FILES.get("profile_image")

    DEFAULT_IMAGE_URL = "https://skn14-codenova-profile.s3.ap-northeast-2.amazonaws.com/profile_image/default2.png"
    image_url = DEFAULT_IMAGE_URL

    if profile_image:
        s3_client = S3Client()
        uploaded_url = s3_client.upload(profile_image)
        if uploaded_url:
            image_url = uploaded_url
        else:
            # 업로드 실패 시 기본 이미지 유지 + 로깅
            print("image url 생성 오류, 기본 이미지로 대체")

    # DB 저장 (중복 아이디 방어)
    try:
        with transaction.atomic():
            user = User(
                id=userId,
                email=email,
                name=name,
                department=team,
                rank=role,
                birthday=birth_dt,
                gender=gender,
                phone=phone,
                status=Status.PENDING,
                is_active=True,
                profile_image=image_url,
            )
            user.set_password(password)  # 해시 저장
            # user.is_active = False

            user.save()
            ApprovalLog.objects.get_or_create(
                user=user,
                action=Status.PENDING,
            )

    except IntegrityError:
        form.add_error("userId", "이미 사용 중인 아이디입니다.")
        return render(request, "uauth/register2.html", signup_context(form))

    return redirect("uauth:login")


# -----------------------------
# (옵션) JSON API - 필요 시 사용
# -----------------------------
@csrf_protect
@require_http_methods(["POST"])
def signup_api(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body.decode() or "{}")
    except Exception:
        return JsonResponse({"ok": False, "msg": "Invalid JSON"}, status=400)

    # 실사용 시 폼/검증 추가 후 저장 로직 구현
    return JsonResponse({"ok": False, "msg": "Not implemented"}, status=400)


# --- pending페이지---


@login_required
def pending_view(request):
    # 내 최신 상태를 확인해서 승인/거부되었으면 바로 분기
    latest_log = (
        ApprovalLog.objects.filter(user=request.user).order_by("-created_at").first()
    )
    current_status = latest_log.action if latest_log else request.user.status

    if current_status == Status.APPROVED:
        return redirect("main:home")
    if current_status == Status.REJECTED:
        return redirect("uauth:reject")

    # 여전히 PENDING이면 대기 페이지
    return render(request, "uauth/pending.html")


@login_required
def reject_view(request):
    latest_log = (
        ApprovalLog.objects.filter(user=request.user).order_by("-created_at").first()
    )
    current_status = latest_log.action if latest_log else request.user.status

    if current_status == Status.APPROVED:
        return redirect("main:home")
    if current_status == Status.PENDING:
        return redirect("uauth:pending")

    # 1) action 값 대소문자/라벨 오차까지 허용
    approval_log = (
        ApprovalLog.objects.filter(user=request.user, action__iexact="rejected")
        .order_by("-created_at")
        .first()
    )

    # 2) 거부 로그가 없을 경우 대비(상태는 Rejected인데 로그가 없을 수 있음)
    if not approval_log:
        approval_log = (
            ApprovalLog.objects.filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

    # ✅ 템플릿에 넘겨야 화면에 보임
    return render(request, "uauth/reject.html", {"approval_log": approval_log})
