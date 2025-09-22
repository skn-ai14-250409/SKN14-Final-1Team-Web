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
            rank = request.user.rank
            department = request.user.department
            print(f"User message: {user_message}, Session ID: {session_id}")

            # 세션 확인
            if not session_id:
                return JsonResponse({"error": "세션 ID가 필요합니다."}, status=400)

            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return JsonResponse({"error": "세션을 찾을 수 없습니다."}, status=404)

            # 세션의 말투를 자동으로 사용
            tone = session.text_mode or "formal"  # 기본값은 formal

            messages = ChatMessage.objects.filter(session=session).order_by(
                "-created_at"
            )[:4]
            messages = reversed(messages)  # 최신 메시지부터 가져와서 시간순으로 정렬
            db_chat_history = []

            for msg in messages:
                # 모든 메시지 타입을 채팅 히스토리에 포함
                if msg.role == "user":
                    db_chat_history.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    db_chat_history.append(
                        {"role": "assistant", "content": msg.content}
                    )
                elif msg.role == "tool_calls":
                    db_chat_history.append(
                        {"role": "assistant", "content": msg.content}
                    )
                elif msg.role == "tool_responses":
                    db_chat_history.append({"role": "user", "content": msg.content})

            # 현재 사용자 메시지를 대화 기록에 추가
            db_chat_history.append({"role": "user", "content": user_message})

            if rank == "cto":
                permission = "cto"
            else:
                permission = department

            # RAG 봇 호출
            response, title, tool_calls, tool_responses = run_sllm(
                db_chat_history, permission=permission, tone=tone
            )

            # 사용자 메시지 저장
            ChatMessage.objects.create(
                session=session, role="user", content=user_message
            )

            # tool_calls 저장 (있는 경우)
            if tool_calls:
                ChatMessage.objects.create(
                    session=session, role="tool_calls", content=tool_calls
                )

            # tool_responses 저장 (있는 경우)
            if tool_responses:
                ChatMessage.objects.create(
                    session=session, role="tool_responses", content=tool_responses
                )

            # 봇 응답 저장
            ChatMessage.objects.create(
                session=session, role="assistant", content=response
            )

            # title이 없거나 초기 "새로운 대화" 메시지로 존재할 때
            if not session.title or session.title == "새로운 대화":
                session.title = title
                session.save(update_fields=["title"])

            # 갱신된 제목을 응답에 포함
            return JsonResponse(
                {"success": True, "bot_message": response, "title": session.title}
            )

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

        # JSON 형태로 변환 (tool_calls, tool_responses 제외)
        data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
            if msg.role in ["user", "assistant"]  # tool_calls, tool_responses 제외
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
            data = json.loads(request.body)
            text_mode = data.get("text_mode", "formal")  # 기본값은 formal

            session = ChatSession.objects.create(
                user=request.user,
                mode="internal",
                title="새로운 대화",
                text_mode=text_mode,
            )

            return JsonResponse(
                {
                    "session": {
                        "id": session.id,
                        "session_id": session.id,
                        "title": session.title,
                        "text_mode": session.text_mode,
                        "created_at": session.created_at.isoformat(),
                    }
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)


@login_required
def session_info(request, session_id):
    """세션 정보 조회 (말투 정보 포함)"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        return JsonResponse(
            {
                "id": session.id,
                "title": session.title,
                "text_mode": session.text_mode,
                "created_at": session.created_at.isoformat(),
            }
        )
    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "세션을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def session_list(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
    data = [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]
    print(data)
    return JsonResponse({"results": data})
