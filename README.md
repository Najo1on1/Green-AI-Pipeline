# 🌿 Green-AI Cognitive Pipeline

**A Private, Energy-Aware Autonomous Agent running on Local Hardware.**

## 📖 Overview

This project demonstrates a full-stack **"Green AI" architecture**. Instead of relying on energy-intensive cloud APIs (OpenAI/Anthropic), this system runs a quantized LLM (`Mistral-7B-AWQ`) entirely on local consumer hardware.

It features a **Real-Time Energy Router** that measures the carbon footprint of every inference token and an **Autonomous Agent** capable of switching between Graph (Structured) and Vector (Unstructured) memory to answer complex compliance questions.

## 🏗️ Architecture

The system is divided into three modular pipelines connecting local compute, cognitive reasoning, and user telemetry.

![System Architecture](images/Green_AI_Architecture.png)

### **Pipeline A: The Green Compute Engine ⚡**
* **Infrastructure:** Dockerized `vLLM` server running on NVIDIA Container Toolkit.
* **Model:** `TheBloke/Mistral-7B-Instruct-v0.2-AWQ` (4-bit Quantization for efficiency).
* **Eco-Router:** A custom Python router that fetches real-time Carbon Grid Intensity data.
* **Green-Ops:** `CodeCarbon` integration to track Joules/Token and CO2 emissions per query.

### **Pipeline B: The Cognitive Core 🧠**
* **Graph Memory:** `Neo4j` database for storing strict relationships (e.g., *Who approves budgets?*).
* **Vector Memory:** `ChromaDB` for storing unstructured semantic data (e.g., *Compliance policies*).
* **Agentic Logic:** A **ReAct Agent** (Reasoning + Acting) built with `LangGraph` that autonomously decides which database to query based on user intent.

### **Pipeline C: The Interface 🖥️**
* **UI:** A `Streamlit` dashboard providing a chat interface.
* **Telemetry:** Real-time energy gauge visualizing the exact power consumption of the local GPU during inference.

---

## 🚀 Getting Started

### **1. Prerequisites**
* Linux (WSL2 supported) with NVIDIA Drivers.
* Docker & NVIDIA Container Toolkit.
* Python 3.10+.

### **2. Installation**
Clone the repo and organize the structure:

```bash
git clone [https://github.com/Najo1on1/Green-AI-Pipeline.git](https://github.com/Najo1on1/Green-AI-Pipeline.git)
cd Green-AI-Pipeline

```

### **3. Start the Infrastructure**

This system relies on microservices. Start the Compute and Cognitive stacks:

```bash
# 1. Start vLLM (Local GPU Inference)
cd pipeline_a_green_compute
docker-compose up -d

# 2. Start Databases (Neo4j & Chroma)
cd ../pipeline_b_cognitive
docker-compose up -d

```

### **4. Run the Dashboard**

Launch the interface to interact with the agent:

```bash
cd ../pipeline_c_interface
source port3env/bin/activate
pip install -r requirements.txt
streamlit run 09_green_dashboard/app.py

```

---

## 📊 Performance & Telemetry

| Metric | Value | Context |
| --- | --- | --- |
| **Hardware** | NVIDIA Card | Consumer GPU |
| **Inference Speed** | ~35 Tokens/Sec | Real-time chat capable |
| **Energy Efficiency** | **~14 Joules/Token** | Benchmarked via CodeCarbon |
| **Grid Awareness** | Real-time CO2 API | Routes traffic based on grid dirty/clean state |

---

## 🧠 Example "Thought Process"

When asked *"Who approves cloud budgets?"*, the Agent performs a multi-step reasoning process, switching strategies when one method fails.

**Step-by-Step Logic:**

> **Thought:** I need to find specific responsibilities for a role.
> **Action:** `graph_lookup` ("Cloud Budget Approver")
> **Observation:** *No direct relationships found.*
> **Thought:** The Graph failed. I will try searching the raw text policy.
> **Action:** `search_policy` ("cloud budget approval process")
> **Observation:** *Found text: "The CTO is responsible for approving all Cloud Budgets."*
> **Final Answer:** The CTO approves cloud budgets.

---

## 🛠️ Technology Stack

* **Compute:** vLLM, PyTorch, NVIDIA CUDA.
* **Orchestration:** LangChain, LangGraph.
* **Database:** Neo4j (Graph), ChromaDB (Vector).
* **Monitoring:** CodeCarbon, Plotly.

* **Frontend:** Streamlit.
