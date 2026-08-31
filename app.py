import streamlit as st
import time
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.database import init_db
from src.generation import generate_answer
from src.config import APP_NAME

@st.cache_resource
def init_foundry():
    ''' 
    Caches the Foundry Local Configuration initialization to prevent redundant
    overhead on every Streamlit component re-render. 
    '''
    config = Configuration(app_name=APP_NAME)
    try:
        FoundryLocalManager.initialize(config)
    except Exception:
        pass # Ignore if already initialized
    return True

def main():
    st.set_page_config(page_title="Local RAG Assistant", page_icon="🤖")
    st.title("Local RAG Q&A Assistant")
    
    # Prepares the underlying SQLite vector storage scheme
    init_db()
    init_foundry()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Display latency and sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                st.caption(f"Generation Latency: {message['latency']:.2f} s")
                with st.expander("Inspect Retrieved Context"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Chunk {i+1}** (Source: {source['source']}, Score: {source['score']:.4f})")
                        st.text(source['text'])

    # React to user input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer locally..."):
                start_time = time.time()
                answer, sources = generate_answer(prompt)
                end_time = time.time()
                latency = end_time - start_time
                
                st.markdown(answer)
                st.caption(f"Generation Latency: {latency:.2f} s")
                
                # Encapsulates the raw context in an expander
                with st.expander("Inspect Retrieved Context"):
                    for i, source in enumerate(sources):
                        st.markdown(f"**Chunk {i+1}** (Source: {source['source']}, Score: {source['score']:.4f})")
                        st.text(source['text'])
                        
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources,
                "latency": latency
            })

if __name__ == "__main__":
    main()
