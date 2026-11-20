import pymupdf
import pytest


@pytest.fixture
def sample_pdf(tmp_path):
    """A tiny 3-page PDF with known text, so tests don't depend on a vendor datasheet.
    Page 1: voltage and frequency. Page 2: blank. Page 3: PWM."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Operating voltage: 1.8V to 5.5V. Maximum frequency: 20 MHz.")
    doc.new_page()  # left blank on purpose, extraction should skip it
    page = doc.new_page()
    page.insert_text((72, 72), "Timer1 supports 8-bit, 9-bit and 10-bit fast PWM modes.")
    path = tmp_path / "sample.pdf"
    doc.save(str(path))
    doc.close()
    return str(path)