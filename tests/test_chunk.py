from app.chunk import chunk_pages, is_toc_chunk


def page(text, number=1):
    """Helper: one fake extracted page."""
    return {"page": number, "text": text}


def test_chunks_keep_their_page_number():
    chunks = chunk_pages([page("a" * 300, 7)])
    assert all(c["page"] == 7 for c in chunks)


def test_neighbouring_chunks_overlap():
    # 2000 chars with size 800 and overlap 150: chunks start at 0, 650, 1300
    chunks = chunk_pages([page("abcdefghij" * 200)], size=800, overlap=150)
    assert len(chunks) == 3
    assert chunks[0]["text"][-150:] == chunks[1]["text"][:150]


def test_short_page_is_one_chunk_without_repeated_tail():
    # 700 chars fits in one chunk; the old code made a second chunk of the last 50 chars
    chunks = chunk_pages([page("x" * 700)], size=800, overlap=150)
    assert len(chunks) == 1


def test_tiny_scraps_are_dropped():
    # page footers like "7810D-AVR-01/15" are shorter than MIN_CHUNK_LEN
    assert chunk_pages([page("7810D-AVR-01/15")]) == []


def test_table_of_contents_is_detected_and_skipped():
    toc = "10.7 Internal Voltage Reference " + ". " * 100 + "43"
    assert is_toc_chunk(toc)
    assert chunk_pages([page(toc)]) == []


def test_normal_text_is_not_mistaken_for_toc():
    text = "Notes: 1. Values with the Power Reduction Register enabled. 2. Typical values at 25C. " * 5
    assert not is_toc_chunk(text)