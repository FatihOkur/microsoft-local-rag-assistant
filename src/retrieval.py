import sqlite3
import numpy as np
from src.config import DB_PATH, TOP_K_RESULTS
from src.embeddings import get_embedding

def cosine_similarity(vec_a, vec_b):
    ''' Evaluates the angle between two multi-dimensional vectors to determine
    how conceptually related two pieces of text are, regardless of their length. '''
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def retrieve_top_k(query):
    ''' Queries the local database and ranks the stored vectors against the query
    vector to surface the most relevant pieces of context. '''
    query_embedding = get_embedding(query)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT source_file, chunk_text, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for source_file, chunk_text, embedding_blob in rows:
        # Reconstructs the float32 array from the binary blob for math operations
        chunk_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
        
        score = cosine_similarity(query_embedding, chunk_embedding)
        results.append({
            "source": source_file,
            "text": chunk_text,
            "score": score
        })
        
    # Sorts descending to ensure the chunks with the highest similarity score are chosen
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:TOP_K_RESULTS]
