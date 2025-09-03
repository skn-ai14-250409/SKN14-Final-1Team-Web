from django.shortcuts import render


def home_view(request):
    return render(request, "my_app/home.html")


def main_chatbot_view(request):
    return render(request, "my_app/main_chatbot.html")


def internal_docs_view(request):
    return render(request, "my_app/internal_docs.html")


def community_board_view(request):
    # 각 게시물 데이터에 'id' 값을 다시 추가합니다.
    best_posts = [
        {
            "id": 1,
            "number": 7768,
            "title": "즐거운 식사 되세요",
            "comment_count": 1,
            "author": "흑마렁",
            "date": "10:32",
            "views": 2,
            "likes": 0,
        },
        {
            "id": 2,
            "number": 7726,
            "title": "즐거운 일요일 되세요!",
            "comment_count": 0,
            "author": "흑마렁",
            "date": "2025.08.31",
            "views": 8,
            "likes": 0,
        },
        {
            "id": 3,
            "number": 7724,
            "title": "8월의 마지막 날",
            "comment_count": 0,
            "author": "레드9",
            "date": "2025.08.31",
            "views": 34,
            "likes": 0,
        },
        {
            "id": 4,
            "number": 7722,
            "title": "촬영회 초보도 참석되나요",
            "comment_count": 3,
            "author": "초필",
            "date": "2025.08.31",
            "views": 64,
            "likes": 0,
        },
        {
            "id": 5,
            "number": 7706,
            "title": "오늘 하루 즐거운 시간 되시길",
            "comment_count": 1,
            "author": "흑마렁",
            "date": "2025.08.30",
            "views": 17,
            "likes": 0,
        },
    ]
    regular_posts = [
        {
            "id": 6,
            "number": 7691,
            "title": "맛점하세요!",
            "comment_count": 2,
            "author": "흑마렁",
            "date": "2025.08.29",
            "views": 15,
            "likes": 0,
        },
        {
            "id": 7,
            "number": 7667,
            "title": "초보 사진입니다",
            "comment_count": 0,
            "author": "우헤히히호",
            "date": "2025.08.27",
            "views": 48,
            "likes": 0,
        },
        {
            "id": 8,
            "number": 7666,
            "title": "오늘 하루 마무리 잘보내세요",
            "comment_count": 0,
            "author": "우헤히히호",
            "date": "2025.08.27",
            "views": 13,
            "likes": 1,
        },
        {
            "id": 9,
            "number": 7657,
            "title": "이제 가을이 오려고 하네요",
            "comment_count": 0,
            "author": "우헤히히호",
            "date": "2025.08.27",
            "views": 25,
            "likes": 1,
        },
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
