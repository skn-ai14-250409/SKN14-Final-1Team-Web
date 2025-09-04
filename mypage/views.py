from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from uauth.models import ApiKey, User, Department, Rank, Gender
from django.core.exceptions import ObjectDoesNotExist
from main.models import Card
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
    # [GET] 페이지 로딩
    api_keys = request.user.api_keys.all().order_by("-created_at")
    my_cards = request.user.cards.all().order_by("-created_at")

    context = {
        "user": request.user,
        "api_keys": api_keys,
        "cards": my_cards,
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
                    user=request.user,
                    name=key_name,
                    secret_key=key_value
                )
    return redirect("mypage:mypage")

@csrf_exempt
@login_required
def mypage_edit(request):
    if request.method == 'POST':
        print("POST 데이터:", request.POST)
        try:
            name = request.POST.get('name')
            rank = request.POST.get('rank')
            department = request.POST.get('department')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            birthday = request.POST.get('birthday')

            if name:
                request.user.name = name
            if rank:
                request.user.rank = rank
            if department:
                request.user.department = department
            if email:
                request.user.email = email
            if gender:
                request.user.gender = gender
            if phone:
                request.user.phone = phone
            if birthday:
                request.user.birthday = birthday

            request.user.save()
            messages.success(request, '프로필 정보가 성공적으로 수정되었습니다.')

        except Exception as e:
            messages.error(request, f'프로필 수정 중 오류가 발생했습니다: {e}')
        
        return redirect('mypage:mypage')

@login_required
def api_key_delete(request, key_id):
    if request.method == 'POST':
        try:
            api_key = ApiKey.objects.get(pk=key_id, user=request.user)
            api_key.delete()
        except ObjectDoesNotExist:
            pass
    return redirect('mypage:mypage')

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

@login_required
def check_api_key_name(request): # API 키 이름의 중복 여부 - ajax
    if request.method == 'GET':
        key_name = request.GET.get('name', None)
        is_taken = ApiKey.objects.filter(user=request.user, name=key_name).exists()
        
        return JsonResponse({'is_taken': is_taken})