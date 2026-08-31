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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            source_file TEXT PRIMARY KEY,
            last_modified REAL NOT NULL
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

def get_tracked_files():
    ''' Returns a dictionary of {filename: last_modified} for all tracked files. '''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT source_file, last_modified FROM file_metadata")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = [] # Table might not exist yet if schema wasn't re-initialized
    conn.close()
    return {row[0]: row[1] for row in rows}

def delete_document(source_file):
    ''' Deletes all chunks and metadata for a specific document. '''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE source_file = ?", (source_file,))
    cursor.execute("DELETE FROM file_metadata WHERE source_file = ?", (source_file,))
    conn.commit()
    conn.close()

def update_file_metadata(source_file, last_modified):
    ''' Inserts or updates the modification time for a tracked file. '''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO file_metadata (source_file, last_modified)
        VALUES (?, ?)
        ON CONFLICT(source_file) DO UPDATE SET last_modified = excluded.last_modified
    """, (source_file, last_modified))
    conn.commit()
    conn.close()
