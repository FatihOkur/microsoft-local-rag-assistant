import sqlite3
import numpy as np
from src.config import DB_PATH

def init_db():
    ''' Defines the schema for persistent local vector storage to ensure
    the application can retrieve embeddings across different user sessions. '''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def clear_db():
    ''' Clears existing documents from the database to allow fresh ingestion. '''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents")
    conn.commit()
    conn.close()

def insert_chunk(source_file, chunk_text, embedding):
    ''' Converts the numpy array into a binary format so it can be stored
    safely within SQLite's BLOB data type. '''
    embedding_bytes = embedding.tobytes()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (source_file, chunk_text, embedding)
        VALUES (?, ?, ?)
    """, (source_file, chunk_text, embedding_bytes))
    conn.commit()
    conn.close()
