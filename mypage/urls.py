from django.urls import path
from . import views

app_name = "mypage"

urlpatterns = [
    path("", views.mypage, name="mypage"),  # 마이페이지
    path(
        "card_detail/<int:card_id>/", views.card_detail, name="card_detail"
    ),  # 카드 팝업창
    path(
        "mypage/api_key_delete/<int:key_id>/",
        views.api_key_delete,
        name="api_key_delete",
    ),  # 카드 삭제
    path("mypage/mypage_edit", views.mypage_edit, name="mypage_edit"),  # 정보 수정
]
