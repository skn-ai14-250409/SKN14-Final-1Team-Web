from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json

from main.models import ChatMessage, ChatSession
from uauth.models import *
from .utils.sllm import run_sllm

# Create your views here.


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

            messages = ChatMessage.objects.filter(session=session).order_by(
                "-created_at"
            )[:6]
            db_chat_history = []

            for msg in messages:
                if msg.role == "user":
                    db_chat_history.append({"role": "user", "content": msg.content})
                else:
                    db_chat_history.append(
                        {"role": "assistant", "content": msg.content}
                    )

            # 현재 사용자 메시지를 대화 기록에 추가
            db_chat_history.append({"role": "user", "content": user_message})

            # RAG 봇 호출
            response = run_sllm(db_chat_history)

            # 사용자 메시지 저장
            ChatMessage.objects.create(
                session=session, role="user", content=user_message
            )

            # 봇 응답 저장
            ChatMessage.objects.create(
                session=session, role="assistant", content=response
            )

            # 갱신된 제목을 응답에 포함
            return JsonResponse({"success": True, "bot_message": response})

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
                user=request.user, mode="internal", title="새로운 대화"
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
