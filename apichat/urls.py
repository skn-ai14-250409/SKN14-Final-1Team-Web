from django.urls import path, include
from . import views

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("api-chat/sessions/", views.session_list, name="session_list"),
    path("session_create/", views.create_session, name="session_create"),
]
