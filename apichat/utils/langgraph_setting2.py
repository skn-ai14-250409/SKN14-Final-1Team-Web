from langgraph.graph import StateGraph, END
from .rag2 import basic_chain_setting
from .retriever import retriever_setting
from langgraph.checkpoint.memory import MemorySaver
from .langgraph_node2 import *


basic_chain = basic_chain_setting()
retriever = retriever_setting()


# 그래프 설정
def graph_setting():
    # LangGraph 정의
    graph = StateGraph(ChatState)

    # 노드 등록
    graph.add_node("analyze_image", analyze_image)
    graph.add_node("classify", classify)

    # classify 후 route와 level에 따라 분기
    graph.add_conditional_edges(
        "classify",
        route_from_classify,  # classify 함수에서 route를 분류
        {
            "api": "extract_queries",
            "basic": "simple",
            "none": "impossible",
        },
    )

    graph.add_node("extract_queries", extract_queries)  # 질문 통합 + 쿼리 추출 노드
    graph.add_node("split_queries", split_queries)  # 질문 분리 툴
    graph.add_node("basic", langgraph_node)  # 기본 답변 노드
    graph.add_node("simple", simple)
    graph.add_node("impossible", impossible)

    # 시작 노드 정의
    graph.set_entry_point("analyze_image")

    # 흐름 설정
    graph.add_edge("analyze_image", "classify")
    graph.add_edge("extract_queries", "split_queries")  # 질문 추출 후 분리
    graph.add_edge("split_queries", "basic")  # 쿼리 분리 후 기본 답변 노드로 넘어감
    graph.add_edge("basic", END)  # 기본 답변 후 종료

    graph.add_edge("simple", END)  # 일상 질문 시 답변 후 종료
    graph.add_edge("impossible", END)

    # 그래프 컴파일
    memory = MemorySaver()
    compiled_graph = graph.compile(checkpointer=memory)

    return compiled_graph
