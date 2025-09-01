from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('main-chatbot/', views.main_chatbot_view, name='main-chatbot'),
    path('internal-docs/', views.internal_docs_view, name='internal-docs'),

    path('api-chat/', include('apichat.urls')),
    path('community/', views.community_board_view, name='community-board'),
    path('community/post/<int:post_id>/', views.post_detail_view, name='post-detail'),
]