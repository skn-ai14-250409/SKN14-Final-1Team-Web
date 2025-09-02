from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib import messages

from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date


from django.contrib.auth.forms import UserCreationForm
import json

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
# from django.contrib.auth import get_user_model, login
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
import re
from datetime import date
from .models import User

from django.contrib.auth import authenticate, login


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(getattr(settings, 'LOGOUT_REDIRECT_URL', '/'))








# login page
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

def _wants_json(request):
    accept = request.headers.get("Accept", "")
    xrw = request.headers.get("X-Requested-With", "")
    return "application/json" in accept or xrw == "XMLHttpRequest"

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
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
            return JsonResponse({"success": False, "field_errors": field_errors}, status=400)
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
    else:
        if _wants_json(request):
            return JsonResponse(
                {"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."},
                status=401,
            )
        messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
        return render(request, "uauth/login.html", {"username": username})



USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
PASSWORD_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
PHONE_RE = re.compile(r'^010-\d{4}-\d{4}$')
MIN_BIRTH = date(1900, 1, 1)

@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "GET":
        return render(request, "uauth/register2.html")

    # --- POST ---
    print("✅ POST 요청 도착")
    print("➡ request.POST:", request.POST)
    
    userId = request.POST.get("userId", "").strip()
    name = request.POST.get("name", "").strip()
    password = request.POST.get("password", "")
    confirm = request.POST.get("confirmPassword", "")
    email = request.POST.get("email", "").strip()
    team = request.POST.get("team", "").strip()
    role = request.POST.get("role", "").strip()
    birth_date_raw = request.POST.get("birthDate") or ""
    birth_date = parse_date(birth_date_raw)
    gender = request.POST.get("gender", "").strip()
    phone = request.POST.get("phoneNumber", "").strip()

   
    print(userId)
    user = User(
    id=userId,
    email=email,
    name=name,
    # department=department,
    # rank=rank,
    birthday=birth_date,
    gender=gender,
    phone=phone
)
    user.set_password(password)
    user.save()

    # (선택) 별도 Profile 모델이 정말 필요할 때만 사용하세요.
    # from .models import Profile
    # Profile.objects.create(...)

    # login(request, user)
    messages.success(request, "회원가입이 완료되었습니다.")
    return redirect("home")

# -------------------------------------------------------------------
# (옵션) JSON API 회원가입 엔드포인트
#  - 프론트가 fetch/axios로 JSON POST 할 때 사용
#  - CSRF 토큰을 헤더나 쿠키로 포함하는 것을 권장
# -------------------------------------------------------------------
@csrf_protect
@require_http_methods(["POST"])
def signup_api(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body.decode() or "{}")
    except Exception:
        return JsonResponse({'ok': False, 'msg': 'Invalid JSON'}, status=400)

    form = UserCreationForm({
        'username': data.get('username', ''),
        'password1': data.get('password1', ''),
        'password2': data.get('password2', ''),
    })

    if form.is_valid():
        user = form.save()
        return JsonResponse({'ok': True, 'username': user.username}, status=201)
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
