import time
import csv
from src.generation import generate_answer
from src.database import init_db
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.config import APP_NAME

TEST_QUERIES = [
    {
        "query": "What are the advantages of using SQLite for local data in this application?",
        "expected": "SQLite is advantageous because it is a serverless, self-contained SQL database engine with cross-platform support, no separate server process, and extremely simple integration."
    },
    {
        "query": "What is the company's policy regarding business class flights for travel?",
        "expected": "Business class travel is only authorized for international flights where the continuous airborne travel time exceeds 6 hours. Domestic flights under 6 hours must be economy class."
    },
    {
        "query": "What are the specific requirements for conducting the humidity resistance test on the electronic control unit?",
        "expected": "The system must operate up to 95% relative humidity. The test is performed at +40 °C for 48 hours. No condensation causing an electrical short circuit or loss of function should occur."
    },
    {
        "query": "What is the capital of France?",
        "expected": "I don't know (or a fallback message indicating the context lacks this info)."
    }
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
    
    for i, item in enumerate(TEST_QUERIES):
        query = item["query"]
        expected = item["expected"]
        print(f"[{i+1}/{len(TEST_QUERIES)}] Query: {query}")
        
        start_time = time.time()
        answer, sources = generate_answer(query)
        end_time = time.time()
        
        latency = end_time - start_time
        source_filenames = ", ".join(list(set([s['source'] for s in sources])))
        
        logs.append({
            "query": query,
            "expected_answer": expected,
            "answer": answer,
            "sources": source_filenames,
            "latency_seconds": round(latency, 4)
        })
        
        print(f"Latency: {latency:.4f}s")
        print(f"Expected: {expected}")
        print(f"Generated: {answer}")
        print(f"Sources: {source_filenames}")
        print("-" * 50)
        
    csv_file = "evaluation_logs.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["query", "expected_answer", "answer", "sources", "latency_seconds"])
        writer.writeheader()
        writer.writerows(logs)
        
    md_file = "evaluation_logs.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# RAG Evaluation Logs\n\n")
        for i, log in enumerate(logs):
            f.write(f"## Query {i+1}: {log['query']}\n\n")
            f.write(f"**Expected Answer:**\n> {log['expected_answer']}\n\n")
            formatted_ans = log['answer'].strip().replace('\n', '\n> ')
            f.write(f"**Generated Answer:**\n> {formatted_ans}\n\n")
            f.write(f"- **Sources Used:** {log['sources']}\n")
            f.write(f"- **Latency:** {log['latency_seconds']} seconds\n\n")
            f.write("---\n\n")
            
    print(f"\nEvaluation complete. Results saved to {csv_file} and {md_file}")

if __name__ == "__main__":
    run_evaluation()
