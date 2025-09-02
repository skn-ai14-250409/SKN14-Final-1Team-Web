from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, START, END

from .rag import basic_chain_setting
from .retriever import retriever_setting

basic_chain = basic_chain_setting()
retriever = retriever_setting()


class ChatState(TypedDict, total=False):
    question: str  # 질문
    answer: str  # 답변


# 기본 답변 노드
def basic_langgraph_node(state: ChatState):
    question = state["question"]
    context = retriever.invoke(question)

    result = basic_chain.invoke({"question": question, "context": context}).strip()

    return {"answer": result}  # 변경된 거 없기 때문에 빈 딕트 반환


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
