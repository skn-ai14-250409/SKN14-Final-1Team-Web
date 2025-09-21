# app/embedding_store.py  (기존 파일 대체/수정)

import os, threading
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

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
                        "device": device,          # ★ 여기가 핵심: 평평하게 전달
                    },
                    encode_kwargs={"normalize_embeddings": True},
                )
    return _embeddings


def retriever_setting(force_download: bool = False):
    """
    벡터 DB 로더. health 체크에서는 호출 금지!
    """
    need_download = force_download
    if not os.path.isdir(DB_DIR):
        need_download = True
    else:
        chroma_file = os.path.join(DB_DIR, "chroma.sqlite3")
        folder_dir = os.path.join(DB_DIR, "8013b0ca-2294-4f8f-9494-65628bc6fc3f")
        if not (os.path.exists(chroma_file) and os.path.exists(folder_dir)):
            need_download = True
        else:
            try:
                if len(os.listdir(folder_dir)) == 0:
                    need_download = True
            except Exception:
                need_download = True

    if need_download:
        from .vector_db import create_chroma_db
        create_chroma_db()

    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIR,
        embedding_function=get_embeddings(),  # ★ 여기서 최초 1회만 로드
    )
    return vs

vs = retriever_setting()

