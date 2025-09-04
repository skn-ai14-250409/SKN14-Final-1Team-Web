# uauth/views.py
from django.conf import settings
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
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "GET":
        return render(request, "uauth/login.html")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

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
    if user is not None:
        login(request, user)
        if _wants_json(request):
            return JsonResponse({"success": True, "redirect_url": reverse("home")})
        messages.success(request, f"{user.username}님, 환영합니다!")
        return redirect("home")

    if _wants_json(request):
        return JsonResponse(
            {"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."},
            status=401,
        )
    messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    return render(request, "uauth/login.html", {"username": username})


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
    team = form.data.get("team", "").strip()
    role = form.data.get("role", "").strip()
    birth_raw = form.data.get("birthDate") or ""
    birth_dt = parse_date(birth_raw)
    gender = form.data.get("gender", "").strip()
    phone = form.data.get("phoneNumber", "").strip()

    # if form.errors:
    #     # 폼 에러 그대로 템플릿에 출력
    #     return render(request, "uauth/register2.html", {"form": form})

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
            )
            user.set_password(password)  # 해시 저장
            user.save()
    except IntegrityError:
        form.add_error("userId", "이미 사용 중인 아이디입니다.")
        return render(request, "uauth/register2.html", signup_context(form))

    login(request, user)
    messages.success(request, "회원가입이 완료되었습니다.")
    return redirect("home")


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
