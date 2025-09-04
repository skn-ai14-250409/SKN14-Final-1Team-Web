from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from .models import Post, Comment
from .forms import CommentForm, PostForm


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
    all_posts = (
        Post.objects.select_related("author")
        .annotate(num_likes=Count("likers"))
        .order_by("-created_at")
    )

    best_posts = [p for p in all_posts if p.num_likes >= 5][:5]
    regular_posts = [p for p in all_posts if p.num_likes < 5][:4]

    context = {
        "best_posts": best_posts,
        "regular_posts": regular_posts,
    }
    return render(request, "my_app/community_board.html", context)


@login_required
def post_detail_view(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related("comments__author"),
        id=post_id,
    )
    comment_form = CommentForm()

    if request.user.is_authenticated and request.user != post.author:
        post.views += 1
        post.save(update_fields=["views"])

    context = {
        "post": post,
        "comment_form": comment_form,
    }
    return render(request, "my_app/post_detail.html", context)


@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("post-detail", post_id=post.id)


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likers.all():
        post.likers.remove(request.user)
    else:
        post.likers.add(request.user)
    return JsonResponse({"new_likes": post.total_likes})


@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likers.all():
        comment.likers.remove(request.user)
    else:
        comment.likers.add(request.user)
    return JsonResponse({"new_likes": comment.total_likes})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author or request.user.is_superuser:
        post_id = comment.post.id
        comment.delete()
        return redirect("post-detail", post_id=post_id)
    return HttpResponseForbidden()


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(
        request, "my_app/edit_comment.html", {"form": form, "comment": comment}
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post-detail", post_id=post.id)
    else:
        form = PostForm()
    return render(request, "my_app/create_post.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "my_app/edit_post.html", {"form": form, "post": post})


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author or request.user.is_superuser:
        post.delete()
        return redirect("community-board")
    return HttpResponseForbidden()
