import os
from dotenv import load_dotenv

import torch
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from .vector_db import create_chroma_db

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.schema import AttributeInfo

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

    # 메타데이터 필드 정보 정의
    metadata_field_info = [
        AttributeInfo(
            name="tags",
            type="string",
            description="구글 API 주제명 (11개 중에서 선택: map, firestore, drive, firebase, gmail, google_identity, calendar, bigquery, sheets, people, youtube)",
        ),
        AttributeInfo(
            name="chroma:document", type="string", description="문서 본문 내용"
        ),
    ]

    # SelfQueryRetriever 객체생성

    self_query_retriever = SelfQueryRetriever.from_llm(
        llm=ChatOpenAI(model="gpt-4o", temperature=0),
        vectorstore=vs,
        document_contents="chroma:document",  # 문서 내용을 가리키는 메타데이터 필드명
        metadata_field_info=metadata_field_info,
        search_kwargs={"k": TOP_K},
    )

    return self_query_retriever
