from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split each page's text into overlapping chunks. Each chunk keeps its page number."""
    chunks = []
    # each new chunk starts this many characters after the previous one
    step = size - overlap
    for p in pages:
        text = p["text"]
        for start in range(0, len(text), step):
            chunks.append({"page": p["page"], "text": text[start:start + size]})
    return chunks