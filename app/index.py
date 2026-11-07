import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBED_MODEL

# loaded once when this file is first imported (takes a few seconds)
model = SentenceTransformer(EMBED_MODEL)


def embed(texts):
    """Turn a list of strings into a (len(texts), 384) array of unit-length vectors."""
    # normalize_embeddings=True scales every vector to length 1,
    # so later a plain dot product equals cosine similarity
    vecs = model.encode(texts, normalize_embeddings=True)
    # FAISS needs float32
    return np.asarray(vecs, dtype="float32")