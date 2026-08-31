import os
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.embeddings import get_embedding
from src.database import insert_chunk

def read_and_chunk_file(filepath):
    ''' Splits large documents into smaller overlapping segments so that the
    context boundaries are not abruptly cut off, preserving semantic meaning
    for the LLM to understand. '''
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += (CHUNK_SIZE - CHUNK_OVERLAP)
        
    return chunks

def ingest_directory(directory_path):
    ''' Processes the entire directory of text files to build the initial
    knowledge base, transforming raw text into vectorized data in the local store. '''
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            chunks = read_and_chunk_file(filepath)
            
            for chunk in chunks:
                embedding = get_embedding(chunk)
                insert_chunk(source_file=filename, chunk_text=chunk, embedding=embedding)
