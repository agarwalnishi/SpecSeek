import pytest

from app.config import SIMILARITY_THRESHOLD
from app.index import build_index, embed, search

CHUNKS = [
    {"page": 1, "text": "Operating voltage range is 1.8V to 5.5V."},
    {"page": 2, "text": "Timer1 supports 8-bit, 9-bit and 10-bit fast PWM."},
    {"page": 3, "text": "The USART can run at baud rates up to 2 Mbps."},
]


@pytest.fixture(scope="module")
def index():
    # built once for every test in this file, embedding is slow
    return build_index(CHUNKS)


def test_embeddings_are_384_numbers_with_length_1():
    vecs = embed(["hello", "world"])
    assert vecs.shape == (2, 384)
    lengths = (vecs ** 2).sum(axis=1) ** 0.5
    assert all(abs(length - 1) < 1e-4 for length in lengths)


def test_index_holds_one_vector_per_chunk(index):
    assert index.ntotal == len(CHUNKS)


def test_search_puts_the_relevant_chunk_first(index):
    # different wording from the chunk on purpose: meaning search, not keyword match
    results = search(index, CHUNKS, "What supply voltage does the chip need?", k=3)
    assert results[0][0]["page"] == 1


def test_results_are_sorted_best_first(index):
    scores = [score for chunk, score in search(index, CHUNKS, "PWM resolution", k=3)]
    assert scores == sorted(scores, reverse=True)


def test_asking_for_more_results_than_chunks_does_not_crash(index):
    # FAISS pads missing results with -1; search() must skip those
    results = search(index, CHUNKS, "voltage", k=10)
    assert len(results) == len(CHUNKS)


def test_off_topic_question_scores_below_threshold(index):
    results = search(index, CHUNKS, "Who won the cricket world cup?", k=1)
    assert results[0][1] < SIMILARITY_THRESHOLD