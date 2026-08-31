import os
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.ingestion import ingest_directory
from src.database import init_db
from src.config import APP_NAME

def main():
    ''' Initializes the database and ingests all text documents from the data directory. '''
    from src.database import init_db, clear_db
    print("Initializing database...")
    init_db()
    print("Clearing old records from database...")
    clear_db()
    
    print("Initializing Foundry Local...")
    config = Configuration(app_name=APP_NAME)
    try:
        FoundryLocalManager.initialize(config)
    except Exception:
        pass
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    print(f"Starting ingestion from {data_dir}...")
    
    ingest_directory(data_dir)
    print("Ingestion complete. The vector database is ready.")

if __name__ == "__main__":
    main()
