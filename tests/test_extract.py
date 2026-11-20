import pymupdf
from app.extract import extract_pages

def test_sample_pdf_is_generated(sample_pdf):
    # sanity check on the fixture itself: 3 pages, page 1 has our text
    doc = pymupdf.open(sample_pdf)
    assert doc.page_count == 3
    assert "Operating voltage" in doc[0].get_text()
    doc.close()

def test_blank_pages_skipped_but_page_numbers_stay_true(sample_pdf):
    pages = extract_pages(sample_pdf)
    # page 2 is blank, so only 1 and 3 come back, and page 3 is still called 3
    assert [p["page"] for p in pages] == [1, 3]


def test_whitespace_is_normalized(sample_pdf):
    for p in extract_pages(sample_pdf):
        assert "\n" not in p["text"]
        assert "  " not in p["text"]