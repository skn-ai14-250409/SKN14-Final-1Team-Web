# uauth/urls.py
from django.urls import path
from . import views

app_name = "uauth"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),  # HTML 폼 회원가입
    path("signup/api/", views.signup_api, name="signup_api"),  # JSON API 회원가입(옵션)
    path("logout/", views.logout_view, name="logout"),
    path("pending/", views.pending_view, name="pending"),
    path("reject/", views.reject_view, name="reject"),
]
