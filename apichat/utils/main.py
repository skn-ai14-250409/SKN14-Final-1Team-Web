from .rag import basic_chain_setting
from .retriever import retriever_setting
from .langgraph_setting import graph_setting


basic_chain = basic_chain_setting()
retriever = retriever_setting()


# langchain 기반으로 테스트
def run_rag(message):
    docs = retriever.invoke(message)
    print(docs)

    response = basic_chain.invoke({"context": docs, "question": message})
    return response


graph = graph_setting()


# langgraph 기반으로 테스트
def run_graph(message):
    result = graph.invoke({"question": message})

    # result는 그래프 실행 후 state를 반환함

    # state값에 담아진 answer를 꺼내서 response에 담아서 반환
    response = result["answer"]
    return response
