import os

APP_NAME = "local_rag_project"

# Identifiers for the specific models downloaded in Foundry Local
EMBEDDING_MODEL_ID = "qwen3-embedding-0.6b"
CHAT_MODEL_ID = "phi-3.5-mini"

# Database paths are resolved relative to this configuration file
# to guarantee the vector store is consistently found regardless of the execution directory.
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "vector_store.db")

# Chunking sizes govern the granularity of the information retrieved,
# with overlap preventing the loss of context at chunk boundaries.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Limits the amount of context injected into the prompt to adhere to the model's token limits.
TOP_K_RESULTS = 3
