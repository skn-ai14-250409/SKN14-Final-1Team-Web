from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from uauth.models import ApiKey, User
from django.core.exceptions import ObjectDoesNotExist
from main.models import Card

# Create your views here.
# @login_required
# def mypage(request):
#     # 임시로 로긴..
#     user = get_object_or_404(User, id='uu001')
#     if request.method == 'POST':
#         key_name = request.POST.get('api_key_name')
#         key_value = request.POST.get('api_key_value')

#         if key_name and key_value:
#             ApiKey.objects.create(user=user, name=key_name, secret_key=key_value)

#         return redirect('main:mypage')

#     # [GET] 요청 처리: 페이지 로딩
#     api_keys = user.api_keys.all()
#     my_cards = user.cards.all()

#     context = {
#         'user': user,
#         'api_keys': api_keys,
#         'cards': my_cards,
#     }
#     return render(request, 'my_app/mypage.html', context)


@login_required
def mypage(request):
    # [POST] API 키 저장
    if request.method == "POST":
        key_name = request.POST.get("api_key_name")
        key_value = request.POST.get("api_key_value")

        if key_name and key_value:
            ApiKey.objects.create(
                user=request.user, name=key_name, secret_key=key_value
            )

        # return redirect('mypage') # my_app:mypage

    # [GET] 페이지 로딩
    api_keys = request.user.api_keys.all().order_by("-created_at")
    my_cards = request.user.cards.all().order_by("-created_at")

    context = {
        "user": request.user,
        "api_keys": api_keys,
        "cards": my_cards,
    }
    return render(request, "my_app/mypage.html", context)


@login_required
def card_detail(request, card_id):
    try:
        card = Card.objects.get(id=card_id)
        messages = [card_message.message for card_message in card.card_messages.all()]
    except ObjectDoesNotExist:
        card = None
        messages = []

    context = {
        "card": card,
        "messages": messages,
    }

    return render(request, "my_app/card_detail.html", context)
