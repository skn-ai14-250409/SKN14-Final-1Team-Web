from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api-chatbot/', views.api_chatbot_view, name='api-chatbot'),
    path('internal-docs/', views.internal_docs_view, name='internal-docs'),

    path('api-chat/', include('apichat.urls')),
]