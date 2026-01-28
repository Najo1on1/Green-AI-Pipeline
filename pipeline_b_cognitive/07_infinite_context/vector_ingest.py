import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Configuration ---
# 1. Path to the PDF (We grab the one we made in Project 4)
PDF_PATH = "../04_private_graph/company_policy.pdf"

# 2. ChromaDB Settings (Must match docker-compose.yml)
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001  # We mapped this in Docker

def ingest_vectors():
    print(f"📂 Loading PDF from {PDF_PATH}...")
    if not os.path.exists(PDF_PATH):
        print("❌ Error: PDF not found! Did you run Project 4?")
        return

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print("✂️ Splitting text into chunks...")
    # We chop text so we can retrieve specific paragraphs later
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"   - Created {len(chunks)} chunks.")

    print("🧠 Generating Embeddings (Running locally via HuggingFace)...")
    # This downloads a small, high-performance model (all-MiniLM-L6-v2)
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("💾 Saving to ChromaDB...")
    # We connect to the Docker container via HTTP
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name="company_policy",
        client_settings=None, # LangChain defaults usually work, but let's be safe
        # In newer LangChain versions, we might need HttpClient. 
        # For now, let's try the standard persistence or http mode.
    )
    
    # Actually, connecting LangChain Chroma to a server can be tricky. 
    # Let's use the HttpClient explicitly to be robust.
    import chromadb
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    vector_db = Chroma(
        client=client,
        collection_name="company_policy",
        embedding_function=embedding_model,
    )
    
    # Add the documents
    vector_db.add_documents(chunks)
    
    print(f"✅ Ingestion Complete! Stored {len(chunks)} vectors in 'company_policy'.")

if __name__ == "__main__":
    ingest_vectors()