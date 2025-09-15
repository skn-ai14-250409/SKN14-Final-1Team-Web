from typing import TypedDict, List, Dict, Any
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from .rag2 import (
    basic_chain_setting,
    query_setting,
    classify_chain_setting,
    simple_chain_setting,
    impossable_chain_setting,
)
from .retriever import retriever_setting

import openai
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


basic_chain = basic_chain_setting()
vs = retriever_setting()
query_chain = query_setting()
classification_chain = classify_chain_setting()
simple_chain = simple_chain_setting()
imp_chain = impossable_chain_setting()


class ChatState(TypedDict, total=False):
    question: str  # 유저 질문
    answer: str  # 모델 답변
    rewritten: str  # 통합된 질문
    queries: List[str]  # 쿼리(질문들)
    search_results: List[str]  # 벡터 DB 검색 결과들
    messages: List[Dict[str, str]]  # 사용자 및 모델의 대화 히스토리
    image: str  # 원본 이미지 데이터
    image_analysis: str  # 이미지 분석 결과
    classify: str  # 질문 분류
    tool_calls: List[Dict[str, Any]]  # 도구 호출 기록


# Google API 선택 옵션 정의
GOOGLE_API_OPTIONS = {
    "map": "Google Maps API (구글 맵 API)",
    "firebase_firestore_crawled": "Google Firestore API (구글 파이어스토어 API)",
    "drive": "Google Drive API (구글 드라이브 API)",
    "firebase_auth_crawled": "Google Firebase Authentication API (구글 파이어베이스 인증 API)",
    "gmail": "Gmail API (구글 메일 API)",
    "google_identity": "Google Identity API (구글 인증 API)",
    "calendar": "Google Calendar API (구글 캘린더 API)",
    "bigquery": "Google BigQuery API (구글 빅쿼리 API)",
    "sheets": "Google Sheets API (구글 시트 API)",
    "people": "Google People API (구글 피플 API)",
    "youtube": "YouTube API (구글 유튜브 API)",
}


# 분류 노드
def classify(state: ChatState):
    image_text = state.get("image_analysis")
    question = state["question"]
    chat_history = state.get("messages", [])
    chat_history = chat_history[:4]

    # 이미지 분석 결과가 있으면 질문에 포함시킴
    if state.get("image_analysis"):
        question = (
            f"사용자의 이번 질문:{question}"
            + "\n"
            + f'사용자가 이번에 혹은 이전에 첨부한 이미지에 대한 설명: {state.get("image_analysis")}'
        )

    result = classification_chain.invoke(
        {"question": question, "context": chat_history}
    ).strip()

    state["classify"] = result

    return state


def route_from_classify(state):
    route = state.get("classify").strip()
    # classification_chain이 실제로 뭘 반환하는지에 따라 매핑
    return route


def analyze_image(state: ChatState) -> ChatState:
    """ChatState의 이미지를 분석하는 함수"""
    print(f"analyze_image 호출됨 - 이미지 존재: {bool(state.get('image'))}")
    if state.get("image"):
        try:
            # GPT-4 Vision API 호출
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "이 이미지에 대해 자세히 설명해주세요.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": state["image"]  # URL이면 그대로 사용
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            answer = response.choices[0].message.content
            state["image_analysis"] = (
                answer  # 원본 이미지는 유지하고 분석 결과를 별도 필드에 저장
            )
            return state
        except Exception as e:
            print(f"이미지 분석 에러: {str(e)}")
            state["image_analysis"] = f"이미지 분석 중 오류가 발생했습니다: {str(e)}"
            return state
    else:
        return state


# (1) 사용자 질문 + 히스토리 통합 → 통합된 질문과 쿼리 추출
def extract_queries(state: ChatState) -> ChatState:
    user_text = state["question"]
    image_text = state.get(
        "image_analysis"
    )  # 이미지 설명 (이 부분은 이미 전달된 이미지 설명이어야 함)

    # 히스토리에서 최근 몇 개의 메시지를 가져와서 통합 질문을 생성
    messages = state.get("messages", [])

    # 최근 4개 메시지만 사용
    history_tail = messages[-4:] if messages else []
    context = history_tail.copy()

    # 이미지 설명이 없으면 그냥 넘어가기
    if image_text:
        # 이미지 설명이 있을 때만 결합
        integrated_text = f"질문: {user_text}\n이미지 설명: {image_text}"
    else:
        # 이미지 설명이 없으면 질문만 결합
        integrated_text = user_text

    # 통합된 텍스트를 context에 추가
    context.append({"role": "user", "content": integrated_text})

    # 통합된 질문을 state["rewritten"]에 저장
    state["rewritten"] = context

    return state


# (2) LLM에게 질문 분리를 시킨다
def split_queries(state: ChatState) -> ChatState:
    rewritten = state.get("rewritten")

    response = query_chain.invoke({"rewritten": rewritten})
    state["queries"] = response["questions"]  # questions 리스트만 저장

    return state


@tool
def vector_search_tool(query: str, api_tags: List[str] = None) -> List[str]:
    """
    벡터 DB에서 쿼리를 검색합니다.

    Args:
        query: 검색할 질문/쿼리
        api_tags: Google API 태그 필터

    Returns:
        검색 결과 리스트 (page_content만 포함)
    """
    # API 태그를 필터로 사용
    filters = {}
    if api_tags:
        filters["tags"] = {"$in": api_tags}

    print(f"검색 중: '{query}' with filters: {filters}")
    results = vs.similarity_search(query, k=8, filter=filters)

    # 각 결과에서 page_content만 추출하여 반환
    return [result.page_content for result in results]


llm = ChatOpenAI(model="gpt-4.1", temperature=0)


def tool_based_search_node(state: ChatState) -> ChatState:
    """LLM이 툴을 사용해서 벡터 DB 검색을 수행하는 노드"""
    queries = state.get("queries", [])
    llm_with_tools = llm.bind_tools([vector_search_tool])
    options_str = "\n".join([f"- {k}: {v}" for k, v in GOOGLE_API_OPTIONS.items()])

    # LLM에게 명시적으로 "각 질문마다 툴 호출"을 요구
    search_instruction = f"""
    다음의 Google API 관련 질문들에 대해, 각 질문마다 반드시 한 번씩
    `vector_search_tool`을 호출해 주세요.
    - 질문들: {queries}
    - 선택 가능한 Google API 태그(1개 이상): 
    {options_str}

    규칙:
    1) 각 질문마다 적절한 api_tags(1개 이상)를 선택하세요.
    2) 선택 가능한 api_tags만 메타 필터로 사용하세요
    툴 인자 예:
    {{"query": "<하나의 질문>", "api_tags": ["gmail","calendar"]}}
    """

    response = llm_with_tools.invoke(search_instruction)

    # 툴 호출 결과 추출
    search_results = []
    tool_calls = []

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "vector_search_tool":
                # 툴 실행
                result = vector_search_tool.invoke(tool_call["args"])
                search_results.extend(result)
                tool_calls.append(
                    {
                        "tool": "vector_search_tool",
                        "args": tool_call["args"],
                        "result": result,
                    }
                )

    state["search_results"] = search_results
    state["tool_calls"] = tool_calls

    return state


# (4) 기본 답변 생성 노드
def basic_langgraph_node(state: ChatState) -> Dict[str, Any]:
    """질문에 대한 기본 답변 생성"""
    search_results = state["search_results"]
    history = state["messages"]
    question = state["question"]

    # 이미지 분석 결과가 있으면 질문에 포함시킴
    if state.get("image_analysis"):
        question = (
            f"사용자의 이번 질문:{question}"
            + "\n"
            + f'사용자가 이번에 혹은 이전에 첨부한 이미지에 대한 설명: {state.get("image_analysis")}'
        )

    # 검색된 결과를 바탕으로 답변 생성
    answer = basic_chain.invoke(
        {
            "question": question,
            "context": "\n".join([str(res) for res in search_results]),
            "history": history,
        }
    ).strip()

    state["answer"] = answer

    return state  # 답변을 반환


# (5) 일상 질문 답변 노득
def simple(state: ChatState):
    print("일상 질문 답변 노드 시작")
    image_text = state.get("image_analysis")
    question = state["question"]
    chat_history = state.get("messages", [])
    chat_history = chat_history[:4]

    # 이미지 분석 결과가 있으면 질문에 포함시킴
    if state.get("image_analysis"):
        question = (
            f"사용자의 이번 질문:{question}"
            + "\n"
            + f'사용자가 이번에 혹은 이전에 첨부한 이미지에 대한 설명: {state.get("image_analysis")}'
        )

    # 검색된 결과를 바탕으로 답변 생성
    answer = simple_chain.invoke(
        {
            "question": question,
            "context": chat_history,
        }
    ).strip()

    state["answer"] = answer

    return state  # 답변을 반환


# (5) 답변할 수 없는 질문(구글 api 혹은 일상 질문 아닌 경우)
def impossible(state: ChatState):
    print("답변 불가 노드 시작")
    image_text = state.get("image_analysis")
    question = state["question"]
    chat_history = state.get("messages", [])
    chat_history = chat_history[:4]

    # 이미지 분석 결과가 있으면 질문에 포함시킴
    if state.get("image_analysis"):
        question = (
            f"사용자의 이번 질문:{question}"
            + "\n"
            + f'사용자가 이번에 혹은 이전에 첨부한 이미지에 대한 설명: {state.get("image_analysis")}'
        )

    # 검색된 결과를 바탕으로 답변 생성
    answer = imp_chain.invoke(
        {
            "question": question,
            "context": chat_history,
        }
    ).strip()

    state["answer"] = answer

    return state  # 답변을 반환
