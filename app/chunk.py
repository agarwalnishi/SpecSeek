from app.config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_LEN


def chunk_pages(pages, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split each page's text into overlapping chunks. Each chunk keeps its page number."""
    chunks = []
    # each new chunk starts this many characters after the previous one
    step = size - overlap
    for p in pages:
        text = p["text"]
        for start in range(0, len(text), step):
            piece = text[start:start + size]
            # skip tiny scraps like page footers and part numbers
            if len(piece) >= MIN_CHUNK_LEN:
                chunks.append({"page": p["page"], "text": piece})
            # this chunk already reached the end of the page,
            # so the next one would only repeat its tail
            if start + size >= len(text):
                break
    return chunks