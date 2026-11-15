import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL

PROMPT_TEMPLATE = """Use the datasheet excerpts below to answer the question.
Rules:
- Answer in 1 to 3 sentences, using only facts from the excerpts.
- After each fact, cite its page like (Page 12).
- Only if none of the excerpts relate to the question, reply: Not found in the datasheet.

Question: {question}

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