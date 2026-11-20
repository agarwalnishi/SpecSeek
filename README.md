# SpecSeek

Ask questions about electronic component datasheets and get answers with page citations.

Upload a datasheet PDF, ask something like "What PWM resolutions does Timer1 support?", and get a short answer that cites the pages it came from. Everything runs locally: a small embedding model for search and Llama 3.2 3B through Ollama for answers. No API keys, nothing leaves your machine.

## Setup

Requirements: Python 3.11+ and [Ollama](https://ollama.com/download).

```bash
# 1. get the local LLM (about 2 GB)
ollama pull llama3.2:3b

# 2. install the project
git clone https://github.com/agarwalnishi/SpecSeek.git
cd SpecSeek
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3. run the API
uvicorn app.main:app --reload
```

The first start downloads the embedding model (about 90 MB). After that it loads from the local cache.

## Usage

Open http://localhost:8000/docs for an interactive page where you can try every endpoint.

**1. Upload a datasheet**
```bash
curl -F "file=@datasheets/atmega328p.pdf" http://localhost:8000/upload
```
```json
{"doc_id": "fb84858d...", "filename": "atmega328p.pdf", "chunks": 1084, "cached": false, "seconds": 41.3}
```
The `doc_id` is the file's SHA-256 hash. Uploading the same file again (even renamed) loads the saved index instantly.

**2. Ask a question**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "fb84858d...", "question": "What is the PWM resolution in phase correct PWM mode?"}'
```
```json
{
  "answer": "The PWM resolution in phase correct PWM mode can be fixed to 8-, 9-, or 10-bit, or defined by either ICR1 or OCR1A ... (Page 103)",
  "pages": [103, 104],
  "unverified_citations": [],
  "refused": false,
  "top_score": 0.716,
  "seconds": 40.13
}
```

| Endpoint | What it does |
|---|---|
| `GET /health` | Status and configured models |
| `POST /upload` | Index a PDF (or load it from cache), returns `doc_id` |
| `POST /ask` | Answer a question about an uploaded PDF |

Errors: `400` not a PDF or no text in it, `404` unknown document, `422` invalid input, `503` Ollama not running.

## Tests and evaluation

```bash
pytest -q                  # 35 tests, ~13 s, no Ollama needed (the LLM is mocked)
python -m eval.run_eval    # retrieval hit rate and refusal check on the ATmega328P datasheet
```