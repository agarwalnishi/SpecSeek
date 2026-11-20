import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.config import EMBED_MODEL, TOP_K

# loaded once when this file is first imported (takes a few seconds)
def load_model():
    """Load the embedding model from the local cache if it's there.
    Skips HuggingFace's online update checks, which took ~30 s per startup on a slow connection."""
    try:
        return SentenceTransformer(EMBED_MODEL, local_files_only=True)
    except Exception:
        # first run on a new machine: not downloaded yet, so fetch it
        return SentenceTransformer(EMBED_MODEL)


model = load_model()


def embed(texts):
    """Turn a list of strings into a (len(texts), 384) array of unit-length vectors."""
    # normalize_embeddings=True scales every vector to length 1,
    # so later a plain dot product equals cosine similarity
    vecs = model.encode(texts, normalize_embeddings=True)
    # FAISS needs float32
    return np.asarray(vecs, dtype="float32")

def build_index(chunks):
    """Embed every chunk and put the vectors into a FAISS inner-product index."""
    vecs = embed([c["text"] for c in chunks])
    # vecs.shape[1] is 384, the size of each vector
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index

def search(index, chunks, question, k=TOP_K):
    """Return the k chunks most similar to the question, as (chunk, score) pairs, best first."""
    scores, ids = index.search(embed([question]), k)
    results = []
    for score, i in zip(scores[0], ids[0]):
        # FAISS uses -1 when the index has fewer than k vectors
        if i == -1:
            continue
        results.append((chunks[i], float(score)))
    return results