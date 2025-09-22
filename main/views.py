from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from .models import Post, Comment
from .models import Post, Comment, Card, ChatMessage
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

    regular_posts_list = (
        Post.objects.select_related("author")
        .exclude(id__in=best_post_ids)
        .order_by("-created_at")
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


# apichat/utils/docsearch_view.py (현재 파일 대체해도 되고, 내용만 반영)

import os, json, threading, re
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings

# -------- 설정 --------
BASE_DIR = getattr(settings, "BASE_DIR", os.getcwd())
CHROMA_PERSIST_DIR = os.environ.get(
    "CHROMA_PERSIST_DIR",
    os.path.join(BASE_DIR, "apichat", "utils", "chroma_db"),
)
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "google_api_docs")
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "BAAI/bge-m3")
EMBED_DEVICE = os.environ.get("EMBED_DEVICE", "cpu")

os.environ.setdefault("CHROMA_TELEMETRY_DISABLED", "1")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# -------- Lazy state --------
_client = None
_collection = None
_existing = []
_lock = threading.Lock()
_init_err = None
_UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


def _open_collection(client, maybe_name_or_id, emb):
    """name 우선 → id 보조 → 목록 매칭 → 없으면 생성"""
    # 1) 이름으로 우선 시도
    try:
        return client.get_collection(name=maybe_name_or_id, embedding_function=emb)
    except Exception:
        pass
    # 2) UUID처럼 보이면 id로 시도
    if _UUID_RE.match(maybe_name_or_id or ""):
        try:
            return client.get_collection(id=maybe_name_or_id, embedding_function=emb)
        except Exception:
            pass
    # 3) 목록에서 id 일치 찾기 → 해당 name으로 열기
    for c in client.list_collections():
        if getattr(c, "id", None) == maybe_name_or_id:
            return client.get_collection(name=c.name, embedding_function=emb)
    # 4) 최종: 없으면 생성
    return client.get_or_create_collection(
        name=(maybe_name_or_id or "docs"), embedding_function=emb
    )


def _ensure_chroma():
    """최초 요청 때 한 번만 초기화(헬스 방해 X)"""
    global _client, _collection, _existing, _init_err
    if _collection is not None or _init_err is not None:
        return
    with _lock:
        if _collection is not None or _init_err is not None:
            return
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            emb = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBED_MODEL_NAME,
                device=EMBED_DEVICE,  # ★ CPU/GPU 명시
            )
            _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            _existing = [c.name for c in _client.list_collections()]
            name = COLLECTION_NAME
            # 이름이 비어있다면 자동 선택 규칙
            if not name:
                if len(_existing) == 1:
                    name = _existing[0]
                else:
                    prefer = [n for n in _existing if "docs" in n.lower()] or [
                        n for n in _existing if "apichat" in n.lower()
                    ]
                    name = (
                        prefer[0] if prefer else (_existing[0] if _existing else "docs")
                    )
            # name/id 모두 수용
            col = _open_collection(_client, name, emb)
            _collection = col
        except Exception as e:
            _init_err = f"{type(e).__name__}: {e}"


def _pick_source(meta: dict) -> str:
    v = (meta or {}).get("source") or (meta or {}).get("url")
    if not v:
        return ""
    if isinstance(v, list):
        return (v[0] or "").strip()
    if isinstance(v, str):
        s = v.strip()
        if s[:1] in "[{":
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


def _to_similarity(dist):
    try:
        d = float(dist)
    except Exception:
        return None
    if 0.0 <= d <= 1.0:
        return 1.0 - d
    if 0.0 <= d <= 2.0:
        return 1.0 - (d / 2.0)
    return 1.0 / (1.0 + d)


@require_GET
def docsearch(request):
    # ★ 여기서야 초기화 (임포트 시점 로딩 제거)
    _ensure_chroma()

    q = (request.GET.get("q") or "").strip()
    threshold = float(request.GET.get("threshold") or 0.6)
    k = int(request.GET.get("k") or 10)

    if not q:
        return JsonResponse(
            {
                "results": [],
                "meta": {
                    "persist_dir": CHROMA_PERSIST_DIR,
                    "collection": getattr(_collection, "name", COLLECTION_NAME),
                    "existing": _existing,
                },
            }
        )

    if _init_err or _collection is None:
        return JsonResponse(
            {
                "results": [],
                "warning": f"vector backend unavailable: {_init_err or 'not initialized'}",
                "meta": {"persist_dir": CHROMA_PERSIST_DIR, "existing": _existing},
            }
        )

    try:
        res = _collection.query(
            # 임베딩을 외부에서 계산한다면: query_embeddings=[vectors]
            query_texts=[q],
            n_results=max(k, 10),
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        return JsonResponse(
            {
                "results": [],
                "warning": f"query error: {e}",
                "collection": getattr(_collection, "name", COLLECTION_NAME),
            }
        )

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]

    rows = []
    for doc, meta, dist in zip(docs, metas, dists):
        sim = _to_similarity(dist)
        rows.append(
            {
                "source": _pick_source(meta or {}),
                "title": (meta or {}).get("title")
                or (meta or {}).get("source_file")
                or "",
                "score": round(sim, 4) if sim is not None else None,
                "snippet": (doc or "")[:220],
            }
        )

    filtered = [r for r in rows if (r["score"] is None or r["score"] >= threshold)]
    seen, dedup = set(), []
    for r in filtered:
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
                "collection": getattr(_collection, "name", COLLECTION_NAME),
                "existing": _existing,
                "returned": len(dedup),
                "threshold": threshold,
            },
            "warning": (
                None
                if dedup
                else f"임계값 {threshold:.2f} 이상 결과가 없습니다. 값을 낮춰보세요!"
            ),
        }
    )


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    messages = ChatMessage.objects.filter(session_id=card.session_id).order_by(
        "created_at"
    )

    context = {
        "card": card,
        "messages": messages,
    }
    return render(request, "my_app/card_detail.html", context)
