import os
import shutil

import pymupdf
import pytest

from app import cache
from app.cache import EmptyDocument, file_hash, get_or_build, load


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    # point the cache at a temp folder so tests never touch the real cache/
    monkeypatch.setattr(cache, "CACHE_DIR", str(tmp_path / "cache"))


def test_hash_is_64_hex_chars_and_stable(sample_pdf):
    h = file_hash(sample_pdf)
    assert len(h) == 64
    assert h == file_hash(sample_pdf)


def test_hash_depends_on_content_not_filename(sample_pdf, tmp_path):
    renamed = tmp_path / "totally_different_name.pdf"
    shutil.copy(sample_pdf, renamed)
    assert file_hash(str(renamed)) == file_hash(sample_pdf)


def test_first_call_builds_second_call_hits_cache(sample_pdf):
    _, _, chunks_first, cached_first = get_or_build(sample_pdf)
    _, _, chunks_second, cached_second = get_or_build(sample_pdf)
    assert cached_first is False
    assert cached_second is True
    # chunks survive the trip to disk and back unchanged
    assert chunks_first == chunks_second


def test_unknown_id_is_a_cache_miss():
    assert load("0" * 64) is None


def test_half_written_cache_folder_counts_as_miss(sample_pdf):
    doc_id, _, _, _ = get_or_build(sample_pdf)
    os.remove(os.path.join(cache.CACHE_DIR, doc_id, "chunks.json"))
    assert load(doc_id) is None


def test_pdf_with_no_text_raises_empty_document(tmp_path):
    # a page with nothing on it, like a scanned image with no text layer
    path = tmp_path / "scan.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()
    with pytest.raises(EmptyDocument):
        get_or_build(str(path))