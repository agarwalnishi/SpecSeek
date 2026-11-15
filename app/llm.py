import re

import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, SIMILARITY_THRESHOLD

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

REFUSAL = "Not found in the datasheet."


def build_prompt(question, results):
    """Put the retrieved chunks into the prompt, each tagged with its page number."""
    context = "\n\n".join(f"[Page {chunk['page']}] {chunk['text']}" for chunk, score in results)
    return PROMPT_TEMPLATE.format(context=context, question=question)


class LLMUnavailable(Exception):
    """Raised when Ollama can't be reached or doesn't answer in time."""


def generate(prompt):
    """Send a prompt to the local Llama model and return its reply as text."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                # temperature 0 = (almost) no randomness, same question gives the same answer
                "options": {"temperature": 0},
            },
            # give up instead of waiting forever if the model hangs
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise LLMUnavailable("Can't reach Ollama. Is it running? Start it with: ollama serve") from None
    except requests.exceptions.Timeout:
        raise LLMUnavailable(f"Ollama didn't answer within {OLLAMA_TIMEOUT} s") from None
    except requests.exceptions.HTTPError as e:
        raise LLMUnavailable(f"Ollama returned an error: {e}") from None
    # Ollama replies with JSON; the generated text is in the "response" field
    return response.json()["response"]


def cited_pages(text):
    """Page numbers the model cited, e.g. '(Page 12)' -> {12}."""
    return {int(n) for n in re.findall(r"[Pp]age\s+(\d+)", text)}


def answer(question, results):
    """Full answer step: refuse early if nothing relevant was retrieved, otherwise ask the LLM."""
    # results are sorted best first, so results[0] is the closest chunk
    top_score = results[0][1] if results else 0.0
    if top_score < SIMILARITY_THRESHOLD:
        # skip the LLM entirely: nothing relevant, nothing to hallucinate from
        return {
            "answer": REFUSAL,
            "pages": [],
            "unverified_citations": [],
            "refused": True,
            "top_score": round(top_score, 3),
        }
    text = generate(build_prompt(question, results))
    retrieved = {chunk["page"] for chunk, score in results}
    return {
        "answer": text,
        "pages": sorted(retrieved),
        # pages the model cited that we never gave it: likely made up
        "unverified_citations": sorted(cited_pages(text) - retrieved),
        "refused": False,
        "top_score": round(top_score, 3),
    }