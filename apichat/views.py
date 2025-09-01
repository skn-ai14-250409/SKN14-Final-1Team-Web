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

from main.models import *
from uauth.models import *
from .utils.main import run_rag, run_graph


# Create your views here.

@csrf_exempt
# @login_required # 이후 로그인 기능 구현되면 주석 풀고 구현 필요
def chat(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        print(user_message)

        response = run_graph(user_message)

        response_data = {
            'success': True,
            'bot_message': response
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': f'서버 오류가 발생했습니다: {str(e)}'
        }, status=500)



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
@login_required
def create_session(request):
    """새 채팅 세션 생성"""
    pass




