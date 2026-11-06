# all project settings in one place

# chunking: characters per chunk, and how many characters neighbouring chunks share
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# chunks shorter than this are dropped (leftover bits at the end of a page)
MIN_CHUNK_LEN = 50

# embedding model: small, fast, gives 384-number vectors
EMBED_MODEL = "all-MiniLM-L6-v2"

# how many chunks to retrieve for each question
TOP_K = 4

# if the best chunk scores below this, refuse instead of asking the LLM
SIMILARITY_THRESHOLD = 0.35

# local LLM served by Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"
OLLAMA_TIMEOUT = 120  # seconds

# folders created at runtime (both are in .gitignore)
CACHE_DIR = "cache"
UPLOAD_DIR = "uploads"