from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, START, END

from .rag import basic_chain_setting
from .retriever import retriever_setting
from langgraph.checkpoint.memory import MemorySaver
from .langgraph_node import (
    ChatState,
    extract_queries,
    split_queries,
    basic_langgraph_node,
)


basic_chain = basic_chain_setting()
retriever = retriever_setting()


# basic_langgraph_node는 langgraph_node.py에서 import


def graph_setting():
    # LangGraph 정의
    graph = StateGraph(ChatState)

    # 노드 등록
    graph.add_node("basic", basic_langgraph_node)  # 기본 답변 노드

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
    graph.add_node("basic", basic_langgraph_node)  # 기본 답변 노드

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
