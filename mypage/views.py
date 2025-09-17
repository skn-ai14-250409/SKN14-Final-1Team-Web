from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from uauth.models import ApiKey, User, Department, Rank, Gender
from django.core.exceptions import ObjectDoesNotExist
from main.models import Card, ChatImage, ChatMode
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from django.core.paginator import Paginator
from uauth.aws_s3_service import S3Client


@login_required
def mypage(request):
    # [GET] 페이지 로딩
    all_cards = request.user.cards.select_related("session").order_by("-created_at")
    api_cards = all_cards.filter(session__mode="api")
    internal_cards = all_cards.filter(session__mode="internal")
    api_keys_qs = request.user.api_keys.order_by("-created_at")

    key_page = request.GET.get("key_page", 1)
    api_keys = Paginator(api_keys_qs, 3).get_page(key_page)

    context = {
        "user": request.user,
        "api_cards": api_cards,
        "internal_cards": internal_cards,
        "api_keys": api_keys,
        "departments": Department.choices,
        "ranks": Rank.choices,
        "genders": Gender.choices,
    }

    return render(request, "my_app/mypage.html", context)


@login_required
def create_api_key(request):
    # [POST] API 키 저장
    if request.method == "POST":
        key_name = request.POST.get("api_key_name")
        key_value = request.POST.get("api_key_value")

        if key_name and key_value:
            if not ApiKey.objects.filter(user=request.user, name=key_name).exists():
                ApiKey.objects.create(
                    user=request.user, name=key_name, secret_key=key_value
                )
    return redirect("mypage:mypage")


@csrf_exempt
@login_required
def mypage_edit(request):
    if request.method == "POST":
        print("POST 데이터:", request.POST)
        try:
            name = request.POST.get("name")
            email = request.POST.get("email")
            gender = request.POST.get("gender")
            phone = request.POST.get("phone")
            birthday = request.POST.get("birthday")
            profile_image = request.FILES.get("profile_image")
            print(type(profile_image))

            if name:
                request.user.name = name
            if email:
                request.user.email = email
            if gender:
                request.user.gender = gender
            if phone:
                request.user.phone = phone
            if birthday:
                request.user.birthday = birthday
            if profile_image:
                s3_client = S3Client()
                image_url = s3_client.upload(profile_image)
                request.user.profile_image = image_url

            request.user.save()

        except Exception as e:
            messages.error(request, f"프로필 수정 중 오류가 발생했습니다: {e}")

        return redirect("mypage:mypage")


@login_required
def api_key_delete(request, key_id):
    if request.method == "POST":
        try:
            api_key = ApiKey.objects.get(pk=key_id, user=request.user)
            api_key.delete()
        except ObjectDoesNotExist:
            pass
    return redirect("mypage:mypage")


@login_required
def card_detail(request, card_id):
    try:
        card = Card.objects.prefetch_related(
            Prefetch(
                "card_messages__message__images",
                queryset=ChatImage.objects.all(),
                to_attr="prefetched_images",
            )
        ).get(id=card_id, user=request.user)

        card_messages = [cm.message for cm in card.card_messages.all()]

    except ObjectDoesNotExist:
        card = None
        card_messages = []

    context = {
        "card": card,
        "messages": card_messages,
    }

    return render(request, "my_app/card_detail.html", context)


@login_required
def check_api_key_name(request):  # API 키 이름의 중복 여부 - ajax
    if request.method == "GET":
        key_name = request.GET.get("name", None)
        is_taken = ApiKey.objects.filter(user=request.user, name=key_name).exists()

        return JsonResponse({"is_taken": is_taken})
