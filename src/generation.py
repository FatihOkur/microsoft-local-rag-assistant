from foundry_local_sdk import FoundryLocalManager
from src.config import CHAT_MODEL_ID
from src.retrieval import retrieve_top_k

def generate_answer(query):
    ''' Retrieves relevant chunks and assembles a prompt to ground the LLM's response,
    minimizing hallucinations and ensuring it relies only on local offline data. '''
    retrieved_chunks = retrieve_top_k(query)
    
    context_string = "\n\n".join([f"Source: {chunk['source']}\n{chunk['text']}" for chunk in retrieved_chunks])
    
    # A strict system prompt dictates the persona and boundary conditions
    # to enforce the RAG paradigm strictly.
    system_prompt = (
        "You are an offline knowledge assistant. Answer the user's question based ONLY on the "
        "provided context. If the context does not contain sufficient information to answer, "
        "you must say 'I don't know'. Do not hallucinate or use outside knowledge.\n"
        "When answering, you MUST cite the source document name in your answer (e.g., 'according to document_name.txt...').\n\n"
        f"Context:\n{context_string}"
    )
    
    manager = FoundryLocalManager.instance
    model = manager.catalog.get_model(CHAT_MODEL_ID)
    
    if not model.is_cached:
        print(f"Downloading {CHAT_MODEL_ID}...")
        model.download()
    if not model.is_loaded:
        print(f"Loading {CHAT_MODEL_ID}...")
        model.load()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    client = model.get_chat_client()
    
    # Executes the query locally against the chat model
    try:
        response = client.complete_chat(messages=messages)
        # Assumes an API signature where the response content is accessible via choices
        answer_text = response.choices[0].message.content
    except Exception as e:
        # Fallback mechanism if the library exposes the text directly on the response object
        answer_text = str(getattr(response, 'text', response))
        
    return answer_text, retrieved_chunks
