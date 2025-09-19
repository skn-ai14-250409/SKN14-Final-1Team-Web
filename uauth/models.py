from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

# from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import boto3
from urllib.parse import urlparse
# User = get_user_model()


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Rank(models.TextChoices):
    GENERAL = "general", "일반"
    CTO = "cto", "CTO"


class Department(models.TextChoices):
    FRONTEND = "frontend", "프론트엔드팀"
    BACKEND = "backend", "백엔드팀"
    DATA_AI = "data_ai", "데이터/AI팀"


class Gender(models.TextChoices):
    FEMALE = "female", "여성"
    MALE = "male", "남성"


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
    gender = models.CharField(max_length=20, choices=Gender.choices)
    birthday = models.DateField()
    rank = models.CharField(max_length=50, choices=Rank.choices)
    department = models.CharField(
        max_length=20,
        choices=Department.choices,
        null=True,
        blank=True,
    )
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

    profile_image = models.URLField(
        max_length=500,
        default="https://skn14-codenova-profile.s3.ap-northeast-2.amazonaws.com/profile_image/default2.png",
    )

    # 로그인 ID 필드 = id
    USERNAME_FIELD = "id"
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


@receiver(post_save, sender=ApprovalLog)
def sync_user_active_on_approval(sender, instance, created, **kwargs):
    user = instance.user

    # ✅ is_active는 더 이상 변경하지 않음 (로그인 가능 유지)
    if instance.action == Status.APPROVED and user.status != Status.APPROVED:
        user.status = Status.APPROVED
        user.save(update_fields=["status"])
    elif instance.action == Status.REJECTED and user.status != Status.REJECTED:
        user.status = Status.REJECTED
        user.save(update_fields=["status"])
    elif instance.action == Status.PENDING and user.status != Status.PENDING:
        user.status = Status.PENDING
        user.save(update_fields=["status"])



# 👇 추가된 부분 (맨 아래에 붙이세요)

@receiver(pre_save, sender=User)
def delete_old_profile_image(sender, instance, **kwargs):
    """프로필 이미지 변경 시, 기존 S3 이미지 삭제"""
    if not instance.pk:
        return  # 새 유저 생성 시는 무시

    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    old_url = old_user.profile_image
    new_url = instance.profile_image

    # 기본 이미지거나 같은 URL이면 삭제 안 함
    default_url = "https://skn14-codenova-profile.s3.ap-northeast-2.amazonaws.com/profile_image/default2.png"
    if old_url != new_url and old_url != default_url:
        parsed = urlparse(old_url)
        key = parsed.path.lstrip("/")  # ex) profile_image/20250101_120000_img.png

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME2  # ✅ 업로드 버킷과 동일하게 맞춤

        try:
            s3.delete_object(Bucket=bucket_name, Key=key)
            print(f"[S3] Deleted old profile image: {key}")
        except Exception as e:
            print(f"[S3] Failed to delete old profile image: {e}")
