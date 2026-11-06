import pymupdf


def clean_text(text):
    """Collapse newlines, tabs and repeated spaces into single spaces."""
    return " ".join(text.split())


def extract_pages(pdf_path):
    """Read a PDF and return a list of {"page": number, "text": text}, one per page."""
    doc = pymupdf.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = clean_text(page.get_text())
        # skip pages with no text (blank pages, or scanned images with no text layer)
        if not text:
            continue
        # page numbers start at 1 so they match what a PDF viewer shows
        pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages