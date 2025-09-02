from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json
import uuid
import requests
import os
from datetime import datetime, timedelta, timezone

from main.models import ChatMessage, ChatSession, ChatMode
from uauth.models import *
from .utils.main import run_rag, run_graph


# Create your views here.


@csrf_exempt
# @login_required # 이후 로그인 기능 구현되면 주석 풀고 구현 필요
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            print(user_message)

            response = run_graph(user_message)

            response_data = {"success": True, "bot_message": response}

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse(
                {"error": f"서버 오류가 발생했습니다: {str(e)}"}, status=500
            )


@csrf_exempt
@login_required
def get_chat_history(request, session_id):
    pass


@csrf_exempt
@login_required
def delete_session(request, session_id):
    pass


@csrf_exempt
@login_required
def chat_sessions(request):
    pass


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
    sessions = ChatSession.objects.filter(owner=request.user).order_by("-created_at")
    data = [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]
    print(data)
    return JsonResponse({"results": data})
