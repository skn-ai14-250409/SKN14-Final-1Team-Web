from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, START, END

from .rag import basic_chain_setting
from .retriever import retriever_setting
from langgraph.checkpoint.memory import MemorySaver
from .langgraph_node import (
    ChatState,
    extract_queries,
    split_queries,
    langgraph_node,
)


basic_chain = basic_chain_setting()
retriever = retriever_setting()


# basic_langgraph_node는 langgraph_node.py에서 import


class ChatState_basic(TypedDict, total=False):
    question: str  # 유저 질문
    answer: str  # 모델 답변


def basic_node(state: ChatState):
    """질문에 대한 기본 답변 생성"""
    question = state["question"]

    docs = retriever.invoke(question)

    # 검색된 결과를 바탕으로 답변 생성
    answer = basic_chain.invoke(
        {
            "question": question,
            "context": docs,
        }
    ).strip()

    state["answer"] = answer

    return state  # 답변을 반환


def graph_setting():
    # LangGraph 정의
    graph = StateGraph(ChatState_basic)

    # 노드 등록
    graph.add_node("basic", basic_node)  # 기본 답변 노드

    # 시작 노드 정의
    graph.set_entry_point("basic")

    graph.add_edge("basic", END)  # basic에서 바로 end로 보내기

    compiled_graph = graph.compile()

    return compiled_graph


# 그래프 설정
def graph_setting_edit():
    # LangGraph 정의
    graph = StateGraph(ChatState)

    # 노드 등록
    graph.add_node("extract_queries", extract_queries)  # 질문 통합 + 쿼리 추출 노드
    graph.add_node("split_queries", split_queries)  # 질문 분리 툴
    graph.add_node("basic", langgraph_node)  # 기본 답변 노드

    # 시작 노드 정의
    graph.set_entry_point("extract_queries")

    # 흐름 설정
    graph.add_edge("extract_queries", "split_queries")  # 질문 추출 후 분리
    graph.add_edge("split_queries", "basic")  # 쿼리 분리 후 기본 답변 노드로 넘어감
    graph.add_edge("basic", END)  # 기본 답변 후 종료

    # 그래프 컴파일
    memory = MemorySaver()
    compiled_graph = graph.compile(checkpointer=memory)

    return compiled_graph
