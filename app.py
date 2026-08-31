import streamlit as st
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
    
    query = st.text_input("Ask a question about your documents:")
    
    if st.button("Generate Answer") and query:
        with st.spinner("Retrieving context and generating answer locally..."):
            answer, sources = generate_answer(query)
            
            st.markdown("### Answer")
            st.write(answer)
            
            # Encapsulates the raw context in an expander to maintain a clean UI
            # while still allowing debug inspection of the retrieval quality.
            with st.expander("Inspect Retrieved Context"):
                for i, source in enumerate(sources):
                    st.markdown(f"**Chunk {i+1}** (Source: {source['source']}, Score: {source['score']:.4f})")
                    st.text(source['text'])

if __name__ == "__main__":
    main()
