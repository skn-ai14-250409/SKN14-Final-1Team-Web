from collections import defaultdict
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from .retriever import retriever_setting
from .retriever_qa import retriever_setting2

import os
import pickle

# BM25 인덱스 파일 경로 설정
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE_PATH = os.path.join(HERE, "bm25_index.pkl")
QA_INDEX_FILE_PATH = os.path.join(HERE, "bm25_qa_index.pkl")


def bm25_retrievers_by_tag(k=5):
    """
    원문 Chroma DB 문서를 태그별로 분리하여 BM25 retrievers 생성
    또는 저장된 파일에서 로드
    """
    if os.path.exists(INDEX_FILE_PATH):
        print("bm25_index.pkl 파일에서 BM25 retriever 로드 중...")
        with open(INDEX_FILE_PATH, "rb") as f:
            retrievers = pickle.load(f)
            for r in retrievers.values():
                r.k = k
            return retrievers
    
    print("bm25_index.pkl 파일이 없어 새로 생성합니다.")
    vs = retriever_setting()
    data = vs.get(include=["documents", "metadatas"])
    docs = data["documents"]
    metas = data["metadatas"]

    tag_docs = defaultdict(list)
    for doc, meta in zip(docs, metas):
        tag = meta.get("tags")
        if tag:
            tag_docs[tag].append(Document(page_content=doc, metadata=meta))

    bm25_dict = {}
    for tag, dlist in tag_docs.items():
        r = BM25Retriever.from_documents(dlist)
        r.k = k
        bm25_dict[tag] = r
    
    with open(INDEX_FILE_PATH, "wb") as f:
        pickle.dump(bm25_dict, f)
        
    return bm25_dict


def bm25_retrievers_by_tag_qa(k=10):
    """
    QA Chroma DB 문서를 태그별로 분리하여 BM25 retrievers 생성
    또는 저장된 파일에서 로드
    """
    if os.path.exists(QA_INDEX_FILE_PATH):
        print("bm25_qa_index.pkl 파일에서 BM25 QA retriever 로드 중...")
        with open(QA_INDEX_FILE_PATH, "rb") as f:
            retrievers = pickle.load(f)
            for r in retrievers.values():
                r.k = k
            return retrievers
    
    print("bm25_qa_index.pkl 파일이 없어 새로 생성합니다.")
    vs_qa = retriever_setting2()
    data = vs_qa.get(include=["documents", "metadatas"])
    docs = data["documents"]
    metas = data["metadatas"]

    tag_docs = defaultdict(list)
    for doc, meta in zip(docs, metas):
        tag = meta.get("tags")
        if tag:
            tag_docs[tag].append(Document(page_content=doc, metadata=meta))

    bm25_dict = {}
    for tag, dlist in tag_docs.items():
        r = BM25Retriever.from_documents(dlist)
        r.k = k
        bm25_dict[tag] = r
        
    with open(QA_INDEX_FILE_PATH, "wb") as f:
        pickle.dump(bm25_dict, f)
        
    return bm25_dict