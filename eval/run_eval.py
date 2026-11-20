"""Measure retrieval hit rate@k on the evaluation question set.

Usage: python -m eval.run_eval
"""
import json

from app.chunk import chunk_pages
from app.config import TOP_K
from app.extract import extract_pages
from app.index import build_index, search


def hit_rate(index, chunks, questions, k=TOP_K):
    """A question is a hit if any of the top-k chunks comes from one of its correct pages."""
    hits, misses = 0, []
    for q in questions:
        retrieved = {chunk["page"] for chunk, score in search(index, chunks, q["question"], k=k)}
        if retrieved & set(q["pages"]):
            hits += 1
        else:
            misses.append((q["question"], q["pages"], sorted(retrieved)))
    return hits, misses


CHUNK_SIZES = [400, 800, 1200]

if __name__ == "__main__":
    data = json.load(open("eval/questions.json", encoding="utf-8"))
    questions = data["in_scope"]
    n = len(questions)
    # extract once, re-chunk and re-index for each size
    pages = extract_pages(data["datasheet"])

    for size in CHUNK_SIZES:
        chunks = chunk_pages(pages, size=size)
        index = build_index(chunks)
        hits, misses = hit_rate(index, chunks, questions)
        print(f"\nchunk size {size:>4}: {len(chunks):>4} chunks | hit rate@{TOP_K}: {hits}/{n} = {hits / n:.0%}")
        for question, wanted, got in misses:
            print(f"   MISS: {question} | expected {wanted} | got {got}")