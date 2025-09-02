from django.shortcuts import render


def home_view(request):
    return render(request, "my_app/home.html")


def main_chatbot_view(request):
    return render(request, "my_app/main_chatbot.html")


def internal_docs_view(request):
    return render(request, "my_app/internal_docs.html")


def community_board_view(request):
    # 나중에 실제 데이터베이스에서 데이터 가져와야 함!!
    best_posts = [
        {"title": "코드노바 근황..."},
        {"title": "Docker, 초보자를 위한 완벽 가이드"},
        {"title": "PyCharm 디버깅, 이렇게 하면 쉬워져요"},
        {"title": "Git 충돌 해결의 모든 것"},
        {"title": "REST API 설계 원칙 정리"},
    ]
    regular_posts = [
        {"title": "오늘의 개발 일지"},
        {"title": "새로운 사이드 프로젝트 멤버 구합니다"},
        {"title": "CSS Flexbox 질문 있습니다!"},
    ]
    context = {
        "best_posts": best_posts,
        "regular_posts": regular_posts,
    }
    return render(request, "my_app/community_board.html", context)


def post_detail_view(request, post_id):
    # 나중에 post_id를 사용해 실제 데이터베이스에서 게시글을 조회합니다.
    post = {
        "id": post_id,
        "title": "코드노바 근황...",
        "author": "마르르카",
        "created_at": "2025.08.31. 12:20",
        "updated_at": "2025.08.31. 12:20",
        "content": "얼마 전, 코드노바 사옥을 탐방할 때 충격적인 것을 보았습니다... \n회사 직원들이 다 미남 미녀더라구요.\n\n아이돌 회사인줄 알았어요 ㅋㅋ",
        "likes": 120,
    }
    comments = [
        {
            "author": "alsdlswm72",
            "text": "코드노바? 처음 들어본 회사인데용...",
            "created_at": "2025.08.31. 12:20",
            "is_own_comment": False,
        },
        {
            "author": "통통통",
            "text": "비밀 댓글입니다.",
            "created_at": "2025.08.31. 12:22",
            "is_own_comment": True,
        },
        {
            "author": "제레미프림퐁",
            "text": "궁금하네여.",
            "created_at": "2025.08.31. 12:24",
            "is_own_comment": False,
        },
    ]
    context = {
        "post": post,
        "comments": comments,
        "user_is_author": True,  # 현재 사용자가 글 작성자라고 가정
    }
    return render(request, "my_app/post_detail.html", context)
