from django.urls import path
from . import views

app_name = "mypage"

urlpatterns = [
    path("", views.mypage, name="mypage"),  # 마이페이지
    path(
        "card_detail/<int:card_id>/", views.card_detail, name="card_detail"
    ),  # 카드 팝업창
]
