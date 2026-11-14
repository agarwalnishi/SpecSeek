import hashlib
import json
import os

import faiss

from app.config import CACHE_DIR
from app.extract import extract_pages
from app.chunk import chunk_pages
from app.index import build_index

def file_hash(path):
    """SHA-256 fingerprint of a file. Same bytes always give the same hash."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        # read in 8 KB blocks so big PDFs don't have to fit in memory at once
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def save(file_id, index, chunks):
    """Store a document's FAISS index and its chunks under cache/<file_id>/."""
    folder = os.path.join(CACHE_DIR, file_id)
    os.makedirs(folder, exist_ok=True)
    faiss.write_index(index, os.path.join(folder, "index.faiss"))
    # utf-8 matters on Windows: datasheets are full of symbols like µ, Ω and °C
    with open(os.path.join(folder, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def load(file_id):
    """Return (index, chunks) from cache/<file_id>/, or None if it isn't cached."""
    folder = os.path.join(CACHE_DIR, file_id)
    index_path = os.path.join(folder, "index.faiss")
    chunks_path = os.path.join(folder, "chunks.json")
    # both files must exist; a half-written folder counts as a miss
    if not (os.path.exists(index_path) and os.path.exists(chunks_path)):
        return None
    index = faiss.read_index(index_path)
    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


def get_or_build(pdf_path):
    """Load a PDF's index from cache, or build and cache it.
    Returns (file_id, index, chunks, was_cached)."""
    file_id = file_hash(pdf_path)
    cached = load(file_id)
    if cached:
        index, chunks = cached
        return file_id, index, chunks, True
    chunks = chunk_pages(extract_pages(pdf_path))
    index = build_index(chunks)
    save(file_id, index, chunks)
    return file_id, index, chunks, False