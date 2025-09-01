from .rag import basic_chain_setting
from .retriever import retriever_setting


basic_chain = basic_chain_setting()
retriever = retriever_setting()

def run_rag(message):
    docs = retriever.invoke(message)
    print(docs)

    response = basic_chain.invoke({
        'context': docs,
        'question': message
    })
    return response