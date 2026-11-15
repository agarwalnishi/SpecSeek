import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL

PROMPT_TEMPLATE = """You are a datasheet assistant. Answer the question using ONLY the datasheet excerpts below.
Cite the page for every fact, like (Page 12).
If the excerpts do not contain the answer, reply exactly: Not found in the datasheet.

Excerpts:
{context}

Question: {question}
Answer:"""


def build_prompt(question, results):
    """Put the retrieved chunks into the prompt, each tagged with its page number."""
    context = "\n\n".join(f"[Page {chunk['page']}] {chunk['text']}" for chunk, score in results)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate(prompt):
    """Send a prompt to the local Llama model and return its reply as text."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            # temperature 0 = no randomness, so the same question gives the same answer
            "options": {"temperature": 0},
        },
    )
    # Ollama replies with JSON; the generated text is in the "response" field
    return response.json()["response"]