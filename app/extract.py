import pymupdf


def extract_pages(pdf_path):
    """Read a PDF and return a list of {"page": number, "text": text}, one per page."""
    doc = pymupdf.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        # page numbers start at 1 so they match what a PDF viewer shows
        pages.append({"page": i + 1, "text": page.get_text()})
    doc.close()
    return pages