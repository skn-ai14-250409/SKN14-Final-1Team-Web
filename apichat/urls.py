from django.urls import path, include
from . import views
from .views import save_card, my_cards, card_detail, delete_card

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("transcribe/", views.transcribe_audio, name="transcribe_audio"),
    path("sessions/", views.session_list, name="session_list"),
    path("session_create/", views.create_session, name="session_create"),
    path(
        "chat_history/<int:session_id>/",
        views.get_chat_history,
        name="get_chat_history",
    ),
    path(
        "delete_session/<int:session_id>/", views.delete_session, name="delete_session"
    ),
    path("cards/save/", save_card, name="save_card"),
    path("cards/mine/", my_cards, name="my_cards"),
    path("cards/<int:card_id>/", card_detail, name="card_detail"),
    path("cards/<int:card_id>/delete/", delete_card, name="delete_card"),
]
