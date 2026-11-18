from fastapi import FastAPI

from app.config import OLLAMA_MODEL, EMBED_MODEL

app = FastAPI(
    title="SpecSeek",
    description="Ask questions about electronic component datasheets and get answers with page citations.",
)


@app.get("/health")
def health():
    """Quick check that the server is up, and which models it's configured with."""
    return {"status": "ok", "llm": OLLAMA_MODEL, "embedding_model": EMBED_MODEL}