import hashlib
import json
import os

import faiss

from app.config import CACHE_DIR

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