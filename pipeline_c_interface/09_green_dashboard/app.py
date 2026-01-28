import streamlit as st
import sys
import os
import time
import plotly.graph_objects as go

# --- 1. CONNECT TO THE BRAIN (Pipeline B) ---
# We need to tell Python where to find your Agent code.
# logic: Go up 3 folders (../../), then down into pipeline_b/08_deep_research
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'pipeline_b_cognitive', '08_deep_research'))
sys.path.append(agent_path)

try:
    # We import the 'run_agent' function we wrote in Project 8
    from agent import run_agent
except ImportError as e:
    st.error(f"❌ CRITICAL ERROR: Could not find the AI Brain.\nPath searched: {agent_path}\nError: {e}")
    st.stop()

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Green AI Dashboard",
    page_icon="🌿",
    layout="wide"
)

# --- 3. SIDEBAR (Energy Telemetry) ---
with st.sidebar:
    st.title("🌿 Eco-Monitor")
    st.markdown("Real-time estimates based on your RTX 4060 Ti.")
    
    # Energy Gauge (Plotly)
    # We estimate: 1 Token ≈ 14 Joules (from your Project 3 benchmark)
    if "total_energy" not in st.session_state:
        st.session_state.total_energy = 0.0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = st.session_state.total_energy,
        title = {'text': "Joules Consumed"},
        gauge = {'axis': {'range': [None, 10000]}, 'bar': {'color': "lightgreen"}}
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Equivalency
    bulb_seconds = st.session_state.total_energy / 10 # 10W LED bulb
    st.info(f"💡 This equals keeping an LED bulb on for **{bulb_seconds:.1f} seconds**.")
    
    if st.button("Reset Meter"):
        st.session_state.total_energy = 0.0
        st.rerun()

# --- 4. MAIN CHAT INTERFACE ---
st.title("🧠 Deep Research Assistant")
st.caption("Powered by: Mistral-7B (Local GPU) | Neo4j (Graph) | Chroma (Vector)")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about company policy or cloud budgets..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response (The "Thinking" Phase)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... 🕵️‍♀️")
        
        try:
            # CALL THE PIPELINE B AGENT
            # We wrap it in a spinner so the UI doesn't freeze visually
            with st.spinner("Accessing Knowledge Graph & Vector DB..."):
                response_text = run_agent(prompt)
            
            # 3. Update Energy Metrics (Green Ops Logic)
            # Estimate tokens: ~0.75 words per token. Rough count from response length.
            # Formula: (Input Chars + Output Chars) / 4 * 14 Joules
            est_tokens = (len(prompt) + len(response_text)) / 4
            energy_cost = est_tokens * 14.0 # 14 J/tok from Project 3
            
            st.session_state.total_energy += energy_cost
            
            # 4. Display Answer
            message_placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Force refresh to update the gauge
            st.rerun()
            
        except Exception as e:
            message_placeholder.error(f"Agent Failure: {e}")