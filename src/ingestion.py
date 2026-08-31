import os
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.embeddings import get_embedding
from src.database import insert_chunk

def read_and_chunk_file(filepath):
    ''' Splits documents into semantically coherent chunks based on paragraphs
    and sentences, preventing words from being abruptly cut off, while preserving
    contextual overlap across chunks. '''
    global CHUNK_SIZE, CHUNK_OVERLAP
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    def get_overlap_text(text, overlap_size):
        if not text or overlap_size <= 0:
            return ""
        text = text.strip()
        if len(text) <= overlap_size:
            return text
        overlap = text[-overlap_size:]
        space_idx = overlap.find(' ')
        if space_idx != -1 and space_idx < len(overlap) - 1:
            return overlap[space_idx + 1:]
        return overlap

    # Split by paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(p) > CHUNK_SIZE:
            if current_chunk:
                chunks.append(current_chunk.strip())
                overlap_text = get_overlap_text(current_chunk, CHUNK_OVERLAP)
                current_chunk = overlap_text + " " if overlap_text else ""
            
            # Fallback to sentence splitting if paragraph is huge
            sentences = [s.strip() + '.' for s in p.split('. ') if s.strip()]
            for s in sentences:
                if len(current_chunk) + len(s) <= CHUNK_SIZE:
                    current_chunk += s + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        overlap_text = get_overlap_text(current_chunk, CHUNK_OVERLAP)
                        current_chunk = (overlap_text + " ") if overlap_text else ""
                    
                    if len(current_chunk) + len(s) > CHUNK_SIZE:
                        current_chunk = s + " "
                    else:
                        current_chunk += s + " "
            current_chunk = current_chunk.strip() + "\n\n" if current_chunk else ""
            
        else:
            if len(current_chunk) + len(p) <= CHUNK_SIZE:
                current_chunk += p + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    overlap_text = get_overlap_text(current_chunk, CHUNK_OVERLAP)
                    current_chunk = (overlap_text + " ") if overlap_text else ""
                
                if len(current_chunk) + len(p) > CHUNK_SIZE:
                    current_chunk = p + "\n\n"
                else:
                    current_chunk += p + "\n\n"
                
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def ingest_directory(directory_path):
    ''' Processes the directory of text files incrementally.
    It tracks file modification times and only re-ingests files that are new or changed.
    It also removes chunks for files that have been deleted. '''
    from src.database import get_tracked_files, delete_document, update_file_metadata
    
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return

    tracked_files = get_tracked_files()
    current_files = {}
    
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            current_files[filename] = os.path.getmtime(filepath)
            
    # Remove files that are tracked but no longer exist on disk
    for tracked_file in tracked_files.keys():
        if tracked_file not in current_files:
            print(f"Removing deleted file from database: {tracked_file}")
            delete_document(tracked_file)
            
    # Ingest new or modified files
    for filename, mtime in current_files.items():
        if filename not in tracked_files or mtime > tracked_files[filename]:
            print(f"Ingesting file: {filename}")
            
            # If it was tracked (meaning it was modified), delete old chunks first
            if filename in tracked_files:
                delete_document(filename)
                
            filepath = os.path.join(directory_path, filename)
            chunks = read_and_chunk_file(filepath)
            
            for chunk in chunks:
                embedding = get_embedding(chunk)
                insert_chunk(source_file=filename, chunk_text=chunk, embedding=embedding)
                
            update_file_metadata(filename, mtime)
        else:
            print(f"Skipping unmodified file: {filename}")
