import os
import re
import chromadb
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.graphs import Neo4jGraph

# --- 1. SETUP THE BRAIN (Pipeline A) ---
llm = ChatOpenAI(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1",
    model_name="TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
    temperature=0,
    # Stop exactly when the AI tries to hallucinate the result of an action
    model_kwargs={"stop": ["\nObservation:", "Observation:"]}
)

# --- 2. SETUP TOOLS (Pipeline B) ---
print("🔌 Connecting to Vector DB...")
# Suppress the huggingface warning by just letting it run
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.HttpClient(host="localhost", port=8001)
vector_db = Chroma(
    client=chroma_client, 
    collection_name="company_policy", 
    embedding_function=embedding_model
)

def tool_vector_search(query):
    """Search Company Policy for text."""
    print(f"   [Tool] Searching Vectors for: {query}")
    try:
        results = vector_db.similarity_search(query, k=2)
        if not results:
            return "Observation: No relevant documents found in the database."
        return "\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Vector DB Error: {e}"

print("🔌 Connecting to Graph DB...")
graph = Neo4jGraph(
    url="bolt://localhost:7687", 
    username="neo4j", 
    password="password123"
)

def tool_graph_search(entity_name):
    """Find responsibilities/relationships for a role (e.g. CTO)."""
    print(f"   [Tool] Querying Graph for: {entity_name}")
    clean_name = entity_name.replace("'", "").replace('"', "")
    query = f"MATCH (n)-[r]->(m) WHERE n.id CONTAINS '{clean_name}' OR m.id CONTAINS '{clean_name}' RETURN n.id, type(r), m.id LIMIT 5"
    try:
        result = graph.query(query)
        return str(result) if result else "No relationships found."
    except Exception as e:
        return f"Graph Error: {e}"

# Map tool names to functions
TOOL_MAP = {
    "search_policy": tool_vector_search,
    "graph_lookup": tool_graph_search
}

# --- 3. THE REASONING ENGINE (Manual Loop) ---
SYSTEM_PROMPT = """
You are a Research Agent. Answer the user question by using the following tools:

1. search_policy: Useful for finding text about rules (e.g., "MFA", "breach"). Input: Search query.
2. graph_lookup: Useful for finding responsibilities of roles (e.g., "CTO", "Engineers"). Input: Role name.

Format your answer EXACTLY like this:
Question: the input question
Thought: you should always think about what to do
Action: the action to take, should be one of [search_policy, graph_lookup]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""

def run_agent(question):
    # Initialize conversation history
    history = f"{SYSTEM_PROMPT}\nQuestion: {question}\n"
    
    # Run loop (max 5 steps to prevent infinite loops)
    for i in range(5):
        # 1. Ask LLM what to do
        try:
            response = llm.invoke(history).content
        except Exception as e:
            return f"LLM Error: {e}"
            
        print(f"\n🧠 AGENT (Step {i+1}):\n{response}")
        
        # 2. Check if finished
        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()
        
        # 3. Parse Action
        # We look for "Action: name" and "Action Input: value"
        action_match = re.search(r"Action:\s*(.+)", response)
        input_match = re.search(r"Action Input:\s*(.+)", response)
        
        if action_match and input_match:
            action_name = action_match.group(1).strip()
            action_input = input_match.group(1).strip()
            
            # 4. Run Tool
            tool_func = TOOL_MAP.get(action_name)
            if tool_func:
                observation = tool_func(action_input)
            else:
                observation = f"Error: Tool '{action_name}' not found. Use [search_policy, graph_lookup]"
            
            # 5. Feed result back to Brain
            print(f"👀 OBSERVATION: {observation}")
            history += f"{response}\nObservation: {observation}\n"
        else:
            # If the model messed up the format, tell it to try again
            if "Action:" in response:
                history += f"{response}\nObservation: Invalid format. Please use 'Action:' and 'Action Input:' on separate lines.\n"
            else:
                # If it didn't even try to act, force it
                history += f"{response}\nObservation: You must output an Action or Final Answer.\n"

    return "Agent timed out (Too many steps)."

# --- 4. INTERACTIVE LOOP ---
if __name__ == "__main__":
    print("\n🤖 MANUAL AGENT READY (Dependency-Free).")
    while True:
        q = input("\n>> Ask: ")
        if q.lower() in ["exit", "quit"]: break
        try:
            answer = run_agent(q)
            print(f"\n💡 FINAL ANSWER: {answer}")
        except Exception as e:
            print(f"❌ Error: {e}")