from django.urls import path, include
from . import views

app_name = "main"

urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("api/docsearch/", views.docsearch, name="docsearch"),
    path("main-chatbot/", views.main_chatbot_view, name="main-chatbot"),
    path("internal-docs/", views.internal_docs_view, name="internal-docs"),
    path("api-chat/", include("apichat.urls")),
    path("community/", views.community_board_view, name="community-board"),
    path("community/create/", views.create_post, name="create-post"),
    path("community/post/<int:post_id>/", views.post_detail_view, name="post-detail"),
    path("community/post/<int:post_id>/edit/", views.edit_post, name="edit-post"),
    path("community/post/<int:post_id>/delete/", views.delete_post, name="delete-post"),
    path(
        "community/post/<int:post_id>/comment/",
        views.create_comment,
        name="create-comment",
    ),
    path("community/post/<int:post_id>/like/", views.like_post, name="like-post"),
    path(
        "community/comment/<int:comment_id>/like/",
        views.like_comment,
        name="like-comment",
    ),
    path(
        "community/comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit-comment",
    ),
    path(
        "community/comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete-comment",
    ),
]
