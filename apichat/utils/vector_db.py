# utils/vectordb.py
from pathlib import Path
import os, shutil, tempfile
import gdown

# 구글 드라이브 링크 들어가서 그 안에 있는거를 통째로 가져와서, 그거를 utils/chroma_db 폴더에 넣기
def download_drive_folder_to_chroma_db(folder_url: str, target_dir: Path):
    target_dir = Path(target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        gdown.download_folder(url=folder_url, output=td, quiet=False, use_cookies=False)
        entries = [Path(td) / name for name in os.listdir(td)]
        src_root = entries[0] if len(entries) == 1 and entries[0].is_dir() else Path(td)

        for p in src_root.iterdir():
            dst = target_dir / p.name
            if dst.exists():
                shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
            shutil.move(str(p), str(dst))

    if not (target_dir / "chroma.sqlite3").exists():
        raise RuntimeError(f"'chroma.sqlite3'가 없습니다: {target_dir}")

def create_chroma_db():
    HERE = Path(__file__).resolve().parent
    FOLDER_URL = "https://drive.google.com/drive/folders/1_paLIqOIeOyozE-wsKuMO4wIiOpaLio9"
    download_drive_folder_to_chroma_db(FOLDER_URL, HERE / "chroma_db")
