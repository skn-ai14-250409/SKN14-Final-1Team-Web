import os
from dotenv import load_dotenv

import torch
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .vector_db import create_chroma_db

# .env 로드
load_dotenv()

# 경로/모델 설정
HERE = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(HERE, "chroma_db")
COLLECTION_NAME = "qna_collection"
EMBED_MODEL = "BAAI/bge-m3"
TOP_K = 5

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    encode_kwargs={"normalize_embeddings": True},  # DB 생성 시 설정과 일치해야 함
)


def retriever_setting():
    # (선택) 디렉토리 존재 확인
    if not os.path.isdir(DB_DIR):
        create_chroma_db()

    # 기존 크로마 벡터스토어 로드
    vs = Chroma(
        collection_name=COLLECTION_NAME,  # DB 생성 시 컬렉션명과 동일해야 함
        persist_directory=DB_DIR,
        embedding_function=embeddings,
    )

    # 기본은 similarity. 필요하면 search_type='mmr' 등 옵션 조정
    retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    return retriever
