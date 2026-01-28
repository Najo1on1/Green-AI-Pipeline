import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- Configuration ---
# 1. Connect to Pipeline A (Your Local GPU)
llm = ChatOpenAI(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1",
    model_name="TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
    temperature=0,
    # This extra header sometimes helps vLLM process requests correctly
    default_headers={"Content-Type": "application/json"}
)

# 2. Connect to Neo4j (Pipeline B Database)
neo4j_url = "bolt://localhost:7687"
neo4j_auth = ("neo4j", "password123")

def ingest_policy():
    print("📂 Loading PDF...")
    loader = PyPDFLoader("company_policy.pdf")
    documents = loader.load()
    print(f"   - Loaded {len(documents)} pages.")

    print("🧠 Extracting Graph Relations (This uses your RTX 4060 Ti)...")
    
    # --- THE FIX ---
    # Define the prompt to force the "System" instructions 
    # to appear inside the "User" message.
    # This tricks Mistral/vLLM into accepting the format.
    
    prompt_string = """
    You are a data expert who extracts structured information from text.
    Extract the entities and relationships from the following text.
    
    Text: {input}
    
    Format your output as a JSON list of nodes and relationships.
    """
    
    # We wrap the transformer with this simpler prompt structure
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            ("user", prompt_string), # Force everything into 'user' role
        ])
    )
    
    try:
        # We convert text into graph documents
        graph_documents = llm_transformer.convert_to_graph_documents(documents)
        
        if not graph_documents:
            print("⚠️ Warning: No relations found. The model might have output empty JSON.")
            return

        print(f"   - Found {len(graph_documents[0].nodes)} nodes and {len(graph_documents[0].relationships)} relationships.")
        
        print("💾 Saving to Neo4j...")
        graph = Neo4jGraph(url=neo4j_url, username=neo4j_auth[0], password=neo4j_auth[1])
        graph.add_graph_documents(graph_documents)
        print("✅ Ingestion Complete!")
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        print("Tip: If this is a 'BadRequest 400', the model is rejecting the prompt format.")

if __name__ == "__main__":
    ingest_policy()