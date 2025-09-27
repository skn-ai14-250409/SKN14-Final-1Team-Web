# retriever_bm25.py
from collections import defaultdict
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from .retriever import retriever_setting
from .retriever_qa import retriever_setting2
import os, pickle

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE_PATH = os.path.join(HERE, "bm25_index.pkl")
QA_INDEX_FILE_PATH = os.path.join(HERE, "bm25_qa_index.pkl")

BM25_INDEX = None
BM25_QA_INDEX = None

# 전역에서 한 번만 로드
def _load_bm25_index(path, retriever_func):
    if os.path.exists(path):
        print(f"BM25 인덱스 로드: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        print(f"BM25 인덱스 없음 → 새로 생성: {path}")
        vs = retriever_func()
        data = vs.get(include=["documents", "metadatas"])
        docs, metas = data["documents"], data["metadatas"]

        tag_docs = defaultdict(list)
        for doc, meta in zip(docs, metas):
            tag = meta.get("tags")
            if tag:
                tag_docs[tag].append(Document(page_content=doc, metadata=meta))

        bm25_dict = {tag: BM25Retriever.from_documents(dlist) for tag, dlist in tag_docs.items()}

        with open(path, "wb") as f:
            pickle.dump(bm25_dict, f)

        return bm25_dict

# 시작 시 로드
BM25_INDEX = _load_bm25_index(INDEX_FILE_PATH, retriever_setting)
BM25_QA_INDEX = _load_bm25_index(QA_INDEX_FILE_PATH, retriever_setting2)

def bm25_retrievers_by_tag(k=5):
    for r in BM25_INDEX.values():
        r.k = k
    return BM25_INDEX

def bm25_retrievers_by_tag_qa(k=20):
    for r in BM25_QA_INDEX.values():
        r.k = k
    return BM25_QA_INDEX