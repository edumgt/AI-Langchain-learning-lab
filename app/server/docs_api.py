from __future__ import annotations
import os, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from app.core import settings
from app.core.rag_utils import save_meta_index, load_meta_index, infer_metadata_from_filename, ingest_dir_meta

router = APIRouter(prefix="/docs", tags=["docs"])

class UploadResult(BaseModel):
    saved: list[dict]
    indexed_chunks: int

@router.get("")
def list_docs():
    files = []
    for fn in sorted(os.listdir(settings.DOCS_DIR)):
        if fn.startswith("."):
            continue
        files.append(fn)
    return {"docs": files, "meta_index": load_meta_index(settings.DOCS_DIR)}

@router.post("/upload", response_model=UploadResult)
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    meta_idx = load_meta_index(settings.DOCS_DIR)

    saved = []
    for f in files:
        name = os.path.basename(f.filename or "upload.bin")
        ext = os.path.splitext(name)[1].lower()
        if ext not in [".pdf", ".md", ".txt"]:
            raise HTTPException(400, f"unsupported file type: {ext} (pdf/md/txt only)")

        safe_name = f"{uuid.uuid4().hex}_{name}"
        path = os.path.join(settings.DOCS_DIR, safe_name)
        data = await f.read()
        with open(path, "wb") as out:
            out.write(data)

        meta = infer_metadata_from_filename(name)
        meta_idx[safe_name] = meta
        saved.append({"filename": safe_name, "meta": meta})

    save_meta_index(settings.DOCS_DIR, meta_idx)

    # re-index with metadata (small datasets ok)
    chunks = ingest_dir_meta(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    return UploadResult(saved=saved, indexed_chunks=chunks)
