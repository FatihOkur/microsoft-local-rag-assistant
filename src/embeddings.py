import numpy as np
from foundry_local_sdk import FoundryLocalManager
from src.config import EMBEDDING_MODEL_ID

def get_embedding(text):
    ''' Instantiates the manager and fetches the specific model to generate
    a numerical vector representation of the text, enabling mathematical
    comparison of semantic similarity during the retrieval phase. '''
    manager = FoundryLocalManager.instance
    model = manager.catalog.get_model(EMBEDDING_MODEL_ID)
    
    if not model.is_cached:
        print(f"Downloading {EMBEDDING_MODEL_ID}...")
        model.download()
    if not model.is_loaded:
        print(f"Loading {EMBEDDING_MODEL_ID}...")
        model.load()
    
    client = model.get_embedding_client()
    response = client.generate_embedding(text)
    embedding = response.data[0].embedding
    
    # Casts the result to a standardized float32 array to maintain numerical
    # stability and consistency in downstream cosine similarity calculations.
    return np.array(embedding, dtype=np.float32)
