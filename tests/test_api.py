import pymupdf
import pytest
from fastapi.testclient import TestClient

from app import cache, llm, main
from app.llm import LLMUnavailable

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    # temp folders for cache and uploads, and an empty in-memory store for every test
    monkeypatch.setattr(cache, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path / "uploads"))
    main.documents.clear()


@pytest.fixture
def fake_llm(monkeypatch):
    """Replace the real Llama call with an instant fake. Returns the list of prompts it received."""
    calls = []

    def fake_generate(prompt):
        calls.append(prompt)
        # page 99 is never retrieved, so it should be flagged as unverified
        return "1.8V to 5.5V (Page 1). See also (Page 99)."

    monkeypatch.setattr(llm, "generate", fake_generate)
    return calls


def upload(path, name="sample.pdf"):
    with open(path, "rb") as f:
        return client.post("/upload", files={"file": (name, f, "application/pdf")})


def upload_and_get_id(sample_pdf):
    return upload(sample_pdf).json()["doc_id"]


# ---------- health ----------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ---------- upload ----------

def test_upload_builds_then_second_upload_hits_cache(sample_pdf):
    first = upload(sample_pdf)
    second = upload(sample_pdf)
    assert first.status_code == 200
    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert first.json()["doc_id"] == second.json()["doc_id"]


def test_upload_rejects_non_pdf_name():
    r = client.post("/upload", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_upload_rejects_fake_pdf():
    # right extension, wrong contents
    r = client.post("/upload", files={"file": ("fake.pdf", b"not really a pdf", "application/pdf")})
    assert r.status_code == 400


def test_upload_rejects_pdf_without_text(tmp_path):
    path = tmp_path / "scan.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()
    r = upload(str(path), "scan.pdf")
    assert r.status_code == 400
    assert "No text" in r.json()["detail"]


# ---------- ask ----------

def test_ask_returns_answer_pages_and_flags_made_up_citation(sample_pdf, fake_llm):
    doc_id = upload_and_get_id(sample_pdf)
    r = client.post("/ask", json={"doc_id": doc_id, "question": "What is the operating voltage range?"})
    body = r.json()
    assert r.status_code == 200
    assert body["refused"] is False
    assert 1 in body["pages"]
    assert body["unverified_citations"] == [99]
    assert len(fake_llm) == 1


def test_off_topic_question_is_refused_without_calling_llm(sample_pdf, fake_llm):
    doc_id = upload_and_get_id(sample_pdf)
    r = client.post("/ask", json={"doc_id": doc_id, "question": "Who won the cricket world cup?"})
    assert r.json()["refused"] is True
    # the threshold check stopped it before the LLM
    assert fake_llm == []


def test_ask_unknown_doc_is_404(fake_llm):
    r = client.post("/ask", json={"doc_id": "0" * 64, "question": "What is the voltage?"})
    assert r.status_code == 404


def test_ask_badly_formatted_doc_id_is_422(fake_llm):
    r = client.post("/ask", json={"doc_id": "../../secrets", "question": "What is the voltage?"})
    assert r.status_code == 422


def test_ask_too_short_question_is_422(sample_pdf, fake_llm):
    doc_id = upload_and_get_id(sample_pdf)
    r = client.post("/ask", json={"doc_id": doc_id, "question": "hi"})
    assert r.status_code == 422


def test_ask_when_ollama_is_down_is_503(sample_pdf, monkeypatch):
    doc_id = upload_and_get_id(sample_pdf)

    def ollama_down(prompt):
        raise LLMUnavailable("Can't reach Ollama")

    monkeypatch.setattr(llm, "generate", ollama_down)
    r = client.post("/ask", json={"doc_id": doc_id, "question": "What is the operating voltage range?"})
    assert r.status_code == 503


def test_ask_still_works_after_server_restart(sample_pdf, fake_llm):
    doc_id = upload_and_get_id(sample_pdf)
    # a restart wipes the in-memory store; the index should come back from the disk cache
    main.documents.clear()
    r = client.post("/ask", json={"doc_id": doc_id, "question": "What is the operating voltage range?"})
    assert r.status_code == 200