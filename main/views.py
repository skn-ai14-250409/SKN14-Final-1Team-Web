from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required
def home_view(request):
    return render(request, "my_app/home.html")


@login_required
def main_chatbot_view(request):
    chat_sessions = request.user.chat_sessions.filter(mode="api")

    return render(request, "my_app/main_chatbot.html", {"chat_sessions": chat_sessions})


def internal_docs_view(request):
    return render(request, "my_app/internal_docs.html")


def community_board_view(request):
    # 좋아요(likes)가 5개 이상인 글을 베스트 게시글로, 나머지를 일반 게시글로 가정합니다.
    best_posts = Post.objects.filter(likes__gte=5).order_by("-created_at")[:5]
    regular_posts = Post.objects.filter(likes__lt=5).order_by("-created_at")[:4]

    context = {
        "best_posts": best_posts,
        "regular_posts": regular_posts,
    }
    return render(request, "my_app/community_board.html", context)


def post_detail_view(request, post_id):
    post = Post.objects.get(id=post_id)
    # user_is_author 로직은 실제 로그인 기능 구현 후 수정이 필요합니다.
    context = {
        "post": post,
        "user_is_author": True,
    }
    return render(request, "my_app/post_detail.html", context)
