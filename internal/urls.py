from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("sessions/", views.session_list, name="session_list"),
    path("session_create/", views.create_session, name="session_create"),
    path("session_info/<int:session_id>/", views.session_info, name="session_info"),
    path(
        "chat_history/<int:session_id>/",
        views.get_chat_history,
        name="get_chat_history",
    ),
    path(
        "delete_session/<int:session_id>/", views.delete_session, name="delete_session"
    ),
]
