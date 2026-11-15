import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL


def generate(prompt):
    """Send a prompt to the local Llama 3 model and return its reply as text."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
    )
    # Ollama replies with JSON; the generated text is in the "response" field
    return response.json()["response"]