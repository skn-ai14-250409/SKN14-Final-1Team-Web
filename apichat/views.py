from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json
import uuid
import requests
import os
import re, textwrap # 정규식(re), 프롬프트 들여쓰기 정리(textwrap)
from datetime import datetime, timedelta, timezone

from main.models import ChatMessage, ChatSession, ChatMode
from uauth.models import *
from .utils.main import run_rag, run_graph


# 제목 요약 #
# PRODUCTS = r"(Google Sheets|Sheets|Gmail|Drive|Calendar|Maps|Docs|Slides)"
# KEYWORDS  = r"(batchUpdate|insert|list|update|auth|quota|range|scope|error|permission)"

OPENAI_TITLE_MODEL = os.getenv("OPENAI_TITLE_MODEL", "gpt-4o-mini")

# def extract_meta(text: str):
#     def _m(p):
#         m = re.search(p, text, re.IGNORECASE)
#         return m.group(0) if m else None
#     product = _m(PRODUCTS)
#     api = _m(r"\b\w+\s?API\b") or (f"{product} API" if product else None)
#     error = _m(r"\b(4\d{2}|5\d{2}|invalid[A-Za-z]+|PERMISSION_DENIED|NOT_FOUND)\b")
#     keyword = _m(KEYWORDS)
#     return {"product": product, "api": api, "error": error, "keyword": keyword}

def rule_title_fallback(text: str) -> str:
    """
    LLM 미사용/실패 시 간단 요약 폴백
    """
    s = re.split(r"[.\n!?]", text.strip())[0] or text.strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\sㄱ-ㅎ가-힣A-Za-z0-9]", "", s)
    return (s[:24]).strip() or "새 대화"

def sanitize_title(s: str) -> str:
    """
    이모지/제어문자 제거 + 길이 제한
    """
    s = re.sub(r"[^\w\s\-\:\.\,\[\]\(\)ㄱ-ㅎ가-힣A-Za-z0-9/]", "", s)
    return s.strip()[:60] or "General"

# ---------- 에코 가드 ---------- #
from difflib import SequenceMatcher

def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"[^\wㄱ-ㅎ가-힣]", "", s)

def tokens(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9가-힣]+", s.lower())

def is_echo_like(title: str, source: str,
                  *, hard_ratio: float = 0.9, token_ratio: float = 0.8) -> bool:  # NEW
    """질문 원문을 거의 그대로 베낀 제목인지 판정"""
    t, s = norm(title), norm(source)
    if not t or not s:
        return False
    if t in s:  # 부분 복붙
        return True
    if SequenceMatcher(None, t, s).ratio() >= hard_ratio:  # 문자 유사도
        return True
    # 토큰 자카드
    A, B = set(tokens(title)), set(tokens(source))
    if A and B and len(A & B) / len(A | B) >= token_ratio:
        return True
    return False
# --------------------------------------- #

def initial_title_with_llm(first_question: str) -> str:
    """
    첫 user 질문만으로 LLM이 임시 제목 생성
    OPENAI_API_KEY 없거나 실패하면 규칙 기반으로 폴백
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return rule_title_fallback(first_question)

    prompt = textwrap.dedent(f"""
      다음 문장을 바탕으로 한국어로 **짧고 간결한 대화 제목**을 하나만 만들어라.
      절대 원문 문장을 그대로 복사하지 말고, 핵심 주제를 명사 중심으로 추출하라.

      규칙:                      
      - 글자 수: 12자 이상, 24자 이하
      - 반드시 명사/주제어 위주 (불필요한 수식어 제거)
      - 이모지, 따옴표, 마침표, 물음표, 느낌표, 특수문자 금지
      - 접두사·접미사, 괄호, 콜론 금지
      - 문장 그대로 복사 후 붙여넣기 하지 말고, 핵심 키워드만 뽑아서 제목화
      - 질문 원문을 절대 그대로 베끼지 말 것 (핵심 개념만 압축)
      - 답변은 오직 제목 텍스트만 출력 (불필요한 설명·접두어 금지)
                             
      예시:
      - 입력: "구글 시트에서 권한 오류가 자꾸 나요"
        출력: 구글 시트 권한 오류
      - 입력: "Drive API에서 파일 리스트 가져오는 법"
        출력: Drive API 파일 목록 조회
      - 입력: "gpt 호출쿼터 초과되면 어떻게 해야함?"
        출력: OpenAI 쿼터 초과 대응
                             
      사용자 첫 질문: {first_question}
    """).strip()

    try:
        print("[title] initial via LLM")
        import requests
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": OPENAI_TITLE_MODEL,
            "messages": [
                {"role": "system", "content": "Return only the title text. No punctuation at the end."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 30,
        }
        r = requests.post(url, headers=headers, json=body, timeout=12)
        if not r.ok:
            print("[title] status:", r.status_code, "body:", r.text[:300])
            r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        title = sanitize_title(raw)

        if is_echo_like(title, first_question) or len(tokens(title)) < 2:
            return rule_title_fallback(first_question)
        return title
    except Exception as e:
        print("[title] fallback used:", e)
        return rule_title_fallback(first_question)

def refine_title_with_llm(draft_title: str, transcript: str) -> str:
    """
    최근 2~4개 Q/A 문맥으로 최종 제목 리라이트
    OPENAI_API_KEY 없거나 실패하면 draft 그대로
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return draft_title
    try:
        import requests
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = textwrap.dedent(f"""
          아래 대화 맥락과 기존 제목을 참고하여 **짧고 간결한 한국어 대화 제목**을 최종 확정하라.
          - 글자 수: 12자 이상, 24자 이하
          - 반드시 명사/주제어 위주 (불필요한 수식어 제거)
          - 이모지, 따옴표, 마침표, 물음표, 느낌표, 특수문자 금지
          - 접두사/접미사/콜론/괄호 금지
          - 기존 제목(draft_title)이 이미 간결하고 적절하면 그대로 유지
          - 문장을 그대로 복붙하지 말고, 맥락에서 핵심 주제만 뽑아 제목화
          - 답변은 오직 제목 텍스트만 출력 (설명, 접두어, 여분 텍스트 금지)
          기존 제목(draft_title): {draft_title}
          최근 대화(context):
          {transcript}
        """).strip()
        body = {
            "model": OPENAI_TITLE_MODEL,
            "messages": [
                {"role": "system", "content": "Return only the title text. No punctuation at the end."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 30,
        }
        r = requests.post(url, headers=headers, json=body, timeout=12)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        title = sanitize_title(raw)

        user_lines = [ln[3:].strip() for ln in transcript.splitlines() if ln.startswith("Q:")]
        for q in user_lines:
            if is_echo_like(title, q):
                return draft_title
            
            if is_echo_like(title, draft_title, hard_ratio=0.95, token_ratio=0.9):
                return draft_title
            if len(tokens(title)) < 2:
                return draft_title
        return title or draft_title
    except Exception:
        return draft_title

def update_session_title_inline(session, all_messages):
    """
    - (처음) 첫 질문으로 LLM 임시 제목 생성 (폴백: 규칙)
    - (이후) user 메시지 2개 이상이면 최근 2~4개 Q/A로 LLM 리라이트
    """
    # 1) 초기 임시 제목
    first_user = next((m for m in all_messages if m.role == "user"), None)
    if first_user and (not session.title or session.title == "새로운 대화"):
        session.title = initial_title_with_llm(first_user.content)
        session.save(update_fields=["title"])

    # 2) 최종 제목(2턴 이상)
    user_msgs = [m for m in all_messages if m.role == "user"]
    if len(user_msgs) == 3:
        tail = all_messages[-4:]  # 최근 2세트(user+assistant)만 반영
        transcript = "\n".join(["Q: " + m.content if m.role == "user" else "A: " + m.content for m in tail])
        final_title = refine_title_with_llm(session.title, transcript)
        if final_title and final_title != session.title:
            session.title = final_title
            session.save(update_fields=["title"])
# 제목 요약 #


@csrf_exempt
@login_required
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            session_id = data.get("session_id")
            print(f"User message: {user_message}, Session ID: {session_id}")

            # 세션 확인
            if not session_id:
                return JsonResponse({"error": "세션 ID가 필요합니다."}, status=400)

            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return JsonResponse({"error": "세션을 찾을 수 없습니다."}, status=404)

            # RAG 봇 호출
            response = run_graph(user_message)

            # 사용자 메시지 저장
            ChatMessage.objects.create(
                session=session, role="user", content=user_message
            )

            # 봇 응답 저장
            ChatMessage.objects.create(
                session=session, role="assistant", content=response
            )

            # 제목 갱신
            all_msgs = list(ChatMessage.objects.filter(session=session).order_by("created_at"))
            update_session_title_inline(session, all_msgs)

            # 갱신된 제목을 응답에 포함
            return JsonResponse({"success": True, "bot_message": response, "title": session.title})

        except Exception as e:
            return JsonResponse(
                {"error": f"서버 오류가 발생했습니다: {str(e)}"}, status=500
            )


@csrf_exempt
@login_required
def get_chat_history(request, session_id):
    try:
        # 세션 확인
        session = ChatSession.objects.get(id=session_id, user=request.user)

        # 해당 세션의 모든 메시지 조회
        messages = ChatMessage.objects.filter(session=session).order_by("created_at")

        # JSON 형태로 변환
        data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

        return JsonResponse({"messages": data})

    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "세션을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def delete_session(request, session_id):
    if request.method == "DELETE":
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            return JsonResponse({"success": True})
        except ChatSession.DoesNotExist:
            return JsonResponse({"error": "세션을 찾을 수 없습니다."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "DELETE 요청만 허용됩니다."}, status=405)


@csrf_exempt
# @login_required
def create_session(request):
    """새 채팅 세션 생성"""
    if request.method == "POST":
        try:
            session = ChatSession.objects.create(
                user=request.user, mode="api", title="새로운 대화"
            )

            return JsonResponse(
                {
                    "session": {
                        "id": session.id,
                        "session_id": session.id,
                        "title": session.title,
                        "created_at": session.created_at.isoformat(),
                    }
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)


@login_required
def session_list(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
    data = [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]
    print(data)
    return JsonResponse({"results": data})

from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from main.models import Card, CardMessage, ChatSession, ChatMessage
import json

@csrf_exempt
@login_required
@require_POST
def save_card(request):
    """
    payload:
    {
      "session_id": 123,                // 현재 대화 세션
      "title": "원하는 카드 제목",         // 없으면 session.title
      "message_ids": [11,15,22, ...]    // 선택한 말풍선 id들(순서대로)
    }
    """
    data = json.loads(request.body or "{}")
    session_id = data.get("session_id")
    message_ids = data.get("message_ids") or []
    title = (data.get("title") or "").strip()

    # 1) 소유권/세션 확인
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)

    # 2) 메시지 유효성(모두 이 세션 소속?)
    msgs = list(ChatMessage.objects.filter(session=session, id__in=message_ids).order_by("created_at"))
    if len(msgs) != len(message_ids):
        return JsonResponse({"error": "메시지 목록이 유효하지 않습니다."}, status=400)

    with transaction.atomic():
        card = Card.objects.create(
            user=request.user,
            session=session,
            title=title or (session.title or "제목 없음"),
        )
        # 선택한 순서를 position 으로 저장
        pos_map = {mid: i for i, mid in enumerate(message_ids)}
        for m in msgs:
            CardMessage.objects.create(card=card, message=m, position=pos_map[m.id])

    return JsonResponse({"ok": True, "card_id": card.id, "title": card.title})


@login_required
def my_cards(request):
    rows = Card.objects.filter(user=request.user).order_by("-created_at")
    results = [{
        "id": c.id,
        "title": c.title,
        "created_at": c.created_at.isoformat(),
        "session_id": c.session_id,
        "count": c.card_messages.count(),
    } for c in rows]
    return JsonResponse({"results": results})


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    items = [{
        "message_id": cm.message.id,
        "role": cm.message.role,
        "content": cm.message.content,
        "created_at": cm.message.created_at.isoformat(),
        "position": cm.position
    } for cm in card.card_messages.select_related("message").all()]
    return JsonResponse({
        "id": card.id,
        "title": card.title,
        "created_at": card.created_at.isoformat(),
        "session_id": card.session_id,
        "items": items,
    })


@csrf_exempt
@login_required
@require_POST
def delete_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    card.delete()
    return JsonResponse({"ok": True})
