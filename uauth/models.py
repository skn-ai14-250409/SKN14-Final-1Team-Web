from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


# 관리자
class UserManager(BaseUserManager):
    def create_user(self, id, email, password=None, **extra_fields):
        if not id:
            raise ValueError("로그인 ID는 필수입니다.")
        if not email:
            raise ValueError("이메일은 필수입니다.")

        user = self.model(id=id, email=self.normalize_email(email), **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, id, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", Status.APPROVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser는 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser는 is_superuser=True 여야 합니다.")
        if not password:
            raise ValueError("Superuser는 비밀번호가 필요합니다.")

        return self.create_user(id, email, password, **extra_fields)


# User 회원가입
class User(AbstractBaseUser, PermissionsMixin):
    # id = 로그인 ID (문자열 PK)
    id = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    gender = models.CharField(max_length=20)
    birthday = models.DateField()
    rank = models.CharField(max_length=50)
    department = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # AbstractBaseUser 제공: password, last_login

    # Django 관리용 (Django Admin/인증과 호환)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 로그인 ID 필드 = id
    USERNAME_FIELD = "id"
    # 입력 필드 확인 필 (UI 참고함)
    REQUIRED_FIELDS = ["email", "name", "phone", "gender", "birthday", "rank"]

    objects = UserManager()

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.id} ({self.name})"


# ApprovalLog
class ApprovalLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_logs",
    )
    action = models.CharField(max_length=20, choices=Status.choices)
    reason = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}, {self.action}, {self.created_at:%Y-%m-%d %H:%M}"


# ApiKey
class ApiKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_key"
        unique_together = [("user", "name")]  # 중복 방지
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}, {self.name}"
