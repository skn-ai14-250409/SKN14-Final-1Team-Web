from typing import TypedDict, List, Dict, Any

from .rag2 import basic_chain_setting
from .rag import query_setting
from .retriever import retriever_setting

import openai
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


basic_chain = basic_chain_setting()
retriever = retriever_setting()
query_chain = query_setting()


class ChatState(TypedDict, total=False):
    question: str  # 유저 질문
    answer: str  # 모델 답변
    rewritten: str  # 통합된 질문
    queries: List[str]  # 쿼리(질문들)
    search_results: List[str]  # 벡터 DB 검색 결과들
    messages: List[Dict[str, str]]  # 사용자 및 모델의 대화 히스토리
    image: str  # 원본 이미지 데이터
    image_analysis: str  # 이미지 분석 결과


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


# (3) 벡터 DB 툴 호출
def search_tool(query: str):
    """질문을 바탕으로 벡터 DB에서 결과 검색"""
    return retriever.invoke(query)  # retriever는 DB 검색 로직을 호출


# (4) 기본 답변 생성 노드
def langgraph_node(state: ChatState) -> Dict[str, Any]:
    history = state.get("messages", [])
    """질문에 대한 기본 답변 생성"""
    queries = state["queries"]
    print(f"생성된 질문 리스트 {queries}")
    search_results = []

    # 각 쿼리마다 벡터 DB 검색
    for query in queries:
        print(f"{query} 검색중...")
        results = search_tool(query)
        search_results.append(results)  # 검색된 결과들을 모아서 저장

    # 이미지 분석 결과가 있으면 컨텍스트에 포함
    context_parts = [str(res) for res in search_results]
    if state.get("image_analysis"):
        context_parts.insert(
            0, f"사용자가 올린 이미지 분석 결과: {state['image_analysis']}"
        )

    # 검색된 결과를 바탕으로 답변 생성
    answer = basic_chain.invoke(
        {
            "question": state["question"],
            "history": history,
            "context": "\n".join(context_parts),
        }
    ).strip()

    state["search_results"] = search_results
    state["answer"] = answer

    return state  # 답변을 반환
