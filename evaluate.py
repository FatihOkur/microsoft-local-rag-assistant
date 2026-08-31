import time
import csv
from src.generation import generate_answer
from src.database import init_db
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.config import APP_NAME

TEST_QUERIES = [
    "What is Microsoft Foundry Local?",
    "How does Vector Search work in this architecture?",
    "Why use SQLite for local data?",
    "What language models are typically used?",
    "What is the capital of France?" # Edge case: unanswerable
]

def init_foundry():
    config = Configuration(app_name=APP_NAME)
    try:
        FoundryLocalManager.initialize(config)
    except Exception:
        pass

def run_evaluation():
    print("Initializing components for evaluation...")
    init_db()
    init_foundry()
    
    logs = []
    print("\nStarting evaluation loop...\n")
    
    for i, query in enumerate(TEST_QUERIES):
        print(f"[{i+1}/{len(TEST_QUERIES)}] Query: {query}")
        
        start_time = time.time()
        answer, sources = generate_answer(query)
        end_time = time.time()
        
        latency = end_time - start_time
        source_filenames = ", ".join(list(set([s['source'] for s in sources])))
        
        logs.append({
            "query": query,
            "answer": answer,
            "sources": source_filenames,
            "latency_seconds": round(latency, 4)
        })
        
        print(f"Latency: {latency:.4f}s")
        print(f"Sources: {source_filenames}")
        print("-" * 50)
        
    csv_file = "evaluation_logs.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["query", "answer", "sources", "latency_seconds"])
        writer.writeheader()
        writer.writerows(logs)
        
    print(f"\nEvaluation complete. Results saved to {csv_file}")

if __name__ == "__main__":
    run_evaluation()
