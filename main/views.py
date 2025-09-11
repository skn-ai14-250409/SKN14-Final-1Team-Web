from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from .models import Post, Comment
from .forms import CommentForm, PostForm
import json
import os
from django.conf import settings
from django.core.paginator import Paginator



@login_required
def home_view(request):
    return render(request, "my_app/home.html")


@login_required
def main_chatbot_view(request):
    chat_sessions = request.user.chat_sessions.filter(mode="api")

    return render(request, "my_app/main_chatbot.html", {"chat_sessions": chat_sessions})


@login_required
def internal_docs_view(request):
    chat_sessions = request.user.chat_sessions.filter(mode="internal")

    return render(
        request, "my_app/internal_docs.html", {"chat_sessions": chat_sessions}
    )


def community_board_view(request):
    best_posts = (
        Post.objects.select_related("author")
        .filter(likes__gte=5)
        .order_by("-created_at")[:5]
    )

    best_post_ids = [post.id for post in best_posts]

    # 정렬 순서를 '-likes', '-created_at'으로 변경합니다.
    regular_posts_list = (
        Post.objects.select_related("author")
        .exclude(id__in=best_post_ids)
        .order_by("-likes", "-created_at")
    )

    paginator = Paginator(regular_posts_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "best_posts": best_posts,
        "page_obj": page_obj,
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
    return redirect("main:post-detail", post_id=post.id)


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likers.all():
        post.likers.remove(request.user)
        post.likes -= 1
    else:
        post.likers.add(request.user)
        post.likes += 1
    post.save()
    return JsonResponse({"new_likes": post.likes})


@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likers.all():
        comment.likers.remove(request.user)
        comment.likes -= 1
    else:
        comment.likers.add(request.user)
        comment.likes += 1
    comment.save()
    return JsonResponse({"new_likes": comment.likes})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author or request.user.is_superuser:
        post_id = comment.post.id
        comment.delete()
        return redirect("main:post-detail", post_id=post_id)
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
            return redirect("main:post-detail", post_id=comment.post.id)
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
            return redirect("main:post-detail", post_id=post.id)
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
            return redirect("main:post-detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "my_app/edit_post.html", {"form": form, "post": post})


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author or request.user.is_superuser:
        post.delete()
        return redirect("main:community-board")
    return HttpResponseForbidden()


# Chroma 설정
BASE_DIR = getattr(settings, "BASE_DIR", os.getcwd())
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "apichat", "utils", "chroma_db")

CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", CHROMA_PERSIST_DIR)
COLLECTION_NAME = "qna_collection"
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "BAAI/bge-m3")

# 초기화
try:
    import chromadb
    from chromadb.utils import embedding_functions

    CHROMA_OK = True
except Exception as e:
    CHROMA_OK = False
    CHROMA_ERR = f"import error: {e}"

client = None
collection = None
existing = []
TOTAL_COUNT = 0

if CHROMA_OK:
    try:
        emb = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL_NAME
        )
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        existing = [c.name for c in client.list_collections()]

        # 컬렉션 이름이 지정되지 않았다면 자동 선택
        #  - 1개뿐이면 그걸 선택
        #  - 여러개면 'docs' 포함 → 'apichat' 포함 → 첫 번째 순으로 선택
        name = COLLECTION_NAME
        if not name:
            if len(existing) == 1:
                name = existing[0]
            else:
                candidates = [n for n in existing if "docs" in n.lower()] or [
                    n for n in existing if "apichat" in n.lower()
                ]
                name = (
                    candidates[0]
                    if candidates
                    else (existing[0] if existing else "docs")
                )
        collection = client.get_collection(name=name, embedding_function=emb)
        TOTAL_COUNT = collection.count()
        COLLECTION_NAME = name
    except Exception as e:
        CHROMA_OK = False
        CHROMA_ERR = f"init error: {e}"


def pick_source(meta: dict) -> str:
    v = (meta or {}).get("source") or (meta or {}).get("url")
    if not v:
        return ""
    if isinstance(v, list):
        return (v[0] or "").strip()
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("[") or s.startswith("{"):
            try:
                data = json.loads(s)
                if isinstance(data, list) and data:
                    return str(data[0]).strip()
                if isinstance(data, dict) and "url" in data:
                    return str(data["url"]).strip()
            except Exception:
                pass
        return s
    return str(v).strip()


def to_similarity(dist):
    # distance → similarity 보수 변환
    try:
        d = float(dist)
    except Exception:
        return None
    if 0.0 <= d <= 1.0:  # 이미 0~1 코사인 distance인 경우
        return 1.0 - d
    if 0.0 <= d <= 2.0:  # 0~2 범위로 나오는 구현에 대한 완화 변환
        return 1.0 - (d / 2.0)
    return 1.0 / (1.0 + d)


@require_GET
def docsearch(request):
    q = (request.GET.get("q") or "").strip()
    threshold = float(request.GET.get("threshold") or 0.6)
    k = int(request.GET.get("k") or 10)

    if not q:
        return JsonResponse(
            {
                "results": [],
                "meta": {
                    "persist_dir": CHROMA_PERSIST_DIR,
                    "collection": COLLECTION_NAME,
                    "existing": existing,
                    "count": TOTAL_COUNT,
                },
            }
        )

    if not CHROMA_OK or collection is None:
        return JsonResponse(
            {
                "results": [],
                "warning": f"vector backend unavailable: {CHROMA_ERR}",
                "meta": {
                    "persist_dir": CHROMA_PERSIST_DIR,
                    "existing": existing,
                    "collection": COLLECTION_NAME,
                },
            }
        )

    try:
        res = collection.query(
            query_texts=[q],
            n_results=max(k, 10),
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        return JsonResponse(
            {
                "results": [],
                "warning": f"query error: {e}",
                "collection": COLLECTION_NAME,
            }
        )

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]

    rows = []
    for doc, meta, dist in zip(docs, metas, dists):
        sim = to_similarity(dist)
        rows.append(
            {
                "source": pick_source(meta or {}),
                "title": (meta or {}).get("title")
                or (meta or {}).get("source_file")
                or "",
                "score": round(sim, 4) if sim is not None else None,
                "snippet": (doc or "")[:220],
            }
        )

    # 임계값 필터
    filtered = [r for r in rows if (r["score"] is None or r["score"] >= threshold)]
    out = filtered
    warning = None
    if not out:
        warning = f"임계값 {threshold:.2f} 이상 결과가 없습니다. 값을 낮춰보세요!"

    # URL 중복 제거 + 상위 k
    seen, dedup = set(), []
    for r in out:
        key = r["source"] or (r["title"], r["snippet"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
        if len(dedup) >= k:
            break

    return JsonResponse(
        {
            "results": dedup,
            "meta": {
                "persist_dir": CHROMA_PERSIST_DIR,
                "collection": COLLECTION_NAME,
                "existing": existing,
                "count": TOTAL_COUNT,
                "returned": len(dedup),
                "threshold": threshold,
            },
            "warning": warning,
        }
    )
