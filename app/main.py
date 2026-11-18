import os
import shutil
import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.cache import get_or_build, load
from app.config import EMBED_MODEL, OLLAMA_MODEL, UPLOAD_DIR
from app.index import search
from app.llm import LLMUnavailable, answer

app = FastAPI(
    title="SpecSeek",
    description="Ask questions about electronic component datasheets and get answers with page citations.",
)

# documents loaded in memory: doc_id (file hash) -> (index, chunks)
documents = {}


@app.get("/health")
def health():
    """Quick check that the server is up, and which models it's configured with."""
    return {"status": "ok", "llm": OLLAMA_MODEL, "embedding_model": EMBED_MODEL}


# plain def (not async): FastAPI runs it in a thread pool, so slow indexing doesn't block other requests
@app.post("/upload")
def upload(file: UploadFile = File(...)):
    """Upload a datasheet PDF. Returns a doc_id to use with /ask."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # basename stops path traversal like "../../app/main.py"
    path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    start = time.time()
    doc_id, index, chunks, was_cached = get_or_build(path)
    documents[doc_id] = (index, chunks)
    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "cached": was_cached,
        "seconds": round(time.time() - start, 2),
    }

class AskRequest(BaseModel):
    doc_id: str
    # pydantic rejects empty or huge questions with a 422 before our code runs
    question: str = Field(..., min_length=3, max_length=500)


@app.post("/ask")
def ask(req: AskRequest):
    """Ask a question about an uploaded datasheet. Returns an answer with page citations."""
    if req.doc_id not in documents:
        cached = load(req.doc_id)
        if cached is None:
            raise HTTPException(status_code=404, detail="Unknown doc_id. Upload the datasheet first.")
        documents[req.doc_id] = cached
    index, chunks = documents[req.doc_id]

    start = time.time()
    results = search(index, chunks, req.question)
    try:
        result = answer(req.question, results)
    except LLMUnavailable as e:
        # 503 = the service we depend on (Ollama) is down
        raise HTTPException(status_code=503, detail=str(e))
    result["seconds"] = round(time.time() - start, 2)
    return result