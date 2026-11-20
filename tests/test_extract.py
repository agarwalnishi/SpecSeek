import pymupdf


def test_sample_pdf_is_generated(sample_pdf):
    # sanity check on the fixture itself: 3 pages, page 1 has our text
    doc = pymupdf.open(sample_pdf)
    assert doc.page_count == 3
    assert "Operating voltage" in doc[0].get_text()
    doc.close()