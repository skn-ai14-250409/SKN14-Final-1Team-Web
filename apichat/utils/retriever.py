import os, threading
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .vector_db import create_chroma_db

# .env 로드
load_dotenv()

# 경로/모델 설정
HERE = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(HERE, "chroma_db")
COLLECTION_NAME = "google_api_docs"
EMBED_MODEL = "BAAI/bge-m3"

# 싱글톤 캐시
_embeddings = None
_lock = threading.Lock()


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        with _lock:
            if _embeddings is None:
                device = "cpu"  # "cpu" or "cuda"
                _embeddings = HuggingFaceEmbeddings(
                    model_name=EMBED_MODEL,
                    model_kwargs={
                        "device": device,  # ★ 여기가 핵심: 평평하게 전달
                    },
                    encode_kwargs={"normalize_embeddings": True},
                )
    return _embeddings


def retriever_setting(force_download=False):
    # 디렉토리 존재 및 내용 확인
    need_download = force_download

    if not os.path.isdir(DB_DIR):
        need_download = True
    else:
        # 디렉토리는 있지만 내용이 불완전한지 확인
        chroma_file = os.path.join(DB_DIR, "chroma.sqlite3")
        folder_dir = os.path.join(DB_DIR, "8013b0ca-2294-4f8f-9494-65628bc6fc3f")
        if not os.path.exists(chroma_file) or not os.path.exists(folder_dir):
            need_download = True
        else:
            try:
                folder_contents = os.listdir(folder_dir)
                if len(folder_contents) == 0:
                    need_download = True
            except Exception:
                need_download = True

    if need_download:
        create_chroma_db()

    # 기존 크로마 벡터스토어 로드
    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIR,
        embedding_function=get_embeddings(),  # 임베딩 최초 1회만 로드
    )
    return vs
