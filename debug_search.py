"""Print the top chunks for one or more questions.

Usage: python debug_search.py datasheets/atmega328p.pdf "question 1" "question 2"
"""
import sys

from app.extract import extract_pages
from app.chunk import chunk_pages
from app.index import build_index, search

pdf_path = sys.argv[1]
questions = sys.argv[2:]


chunks = chunk_pages(extract_pages(pdf_path))
# build once, reuse for every question
index = build_index(chunks)

for q in questions:
    print(f"\n=== {q}")
    for chunk, score in search(index, chunks, q):
        print(f"page {chunk['page']:>3} | score {score:.3f} | {chunk['text'][:100]}")