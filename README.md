Automated Sanskrit Knowledge Graph Pipeline

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB-018bff.svg)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203-orange.svg)
![Firecrawl](https://img.shields.io/badge/Scraping-Firecrawl-ff69b4.svg)

Overview
This repository contains an end-to-end automated Artificial Intelligence data pipeline. It extracts unstructured web text (specifically translated Sanskrit verses from the Valmiki Ramayana), processes it through a Large Language Model to identify precise grammatical relationships (**Paninian Karaka roles**), and ingests the structured data into a **Neo4j Graph Database** for analysis and visualization.

This project serves as a Proof of Concept (PoC) for an advanced NLP architecture that requires strict data provenance (auditability back to the source URL) and deterministic relationship mapping.

---

System Architecture

The pipeline consists of two main execution stages:

1. Extraction & NLP Parsing (`scraper_script.py`)
   * Web Scraping:** Uses `FirecrawlApp` to convert unstructured HTML web pages into clean Markdown.
   * LLM Processing:** Passes the truncated text to Groq's API (`llama-3.3-70b-versatile`) with a strict prompt to act as a backend data API.
   * JSON Purification:** Implements a custom Python string-slicing algorithm to bypass LLM conversational "hallucinations" and extract strict, schema-compliant JSON data.
   * Output:** Generates `automated_graph_data.json`.

2. Graph Ingestion (`push_to_neo4j.py`)
   * Driver Connection:** Uses the official `neo4j` Python driver to connect to a cloud-hosted Neo4j AuraDB instance.
   * Data Modeling:** Executes Cypher transactions to create `TextWitness` (source URLs), `Assertion` (events), and `Entity` (characters) nodes.
   * Grammar Mapping:** Maps entities to assertions using directed edges labeled with Sanskrit grammar roles (e.g., `kartri` for agent, `karma` for object).

---

Key Features
* Zero-Shot Entity & Relation Extraction: Leverages Llama-3 to extract complex linguistic relationships without needing a fine-tuned Named Entity Recognition (NER) model.
* Strict Source Provenance: Every fact/assertion in the database is visually and cryptographically tethered to a `TextWitness` node containing the exact URL it was scraped from.
* Cost & Speed Optimized: Uses Groq's high-speed LPU infrastructure for lightning-fast LLM inference and truncates text to stay within free-tier limits.

---

Prerequisites

Before you begin, ensure you have the following accounts and API keys:
* [Groq API Key](https://console.groq.com/)
* [Firecrawl API Key](https://www.firecrawl.dev/)
* [Neo4j AuraDB Account](https://console.neo4j.io/) (Free Tier)

---

Setup & Installation

1. Clone the repository:
```bash
git clone [https://github.com/Shivpatil-byte/LangGraph-and-Web-Scraping.git](https://github.com/Shivpatil-byte/LangGraph-and-Web-Scraping.git)
cd LangGraph-and-Web-Scraping

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install python-dotenv langchain-groq firecrawl-py neo4j

Configure Environment Variables:
Create a .env file in the root directory and add your keys:

FIRECRAWL_API_KEY=your_firecrawl_key_here
GROQ_API_KEY=your_groq_key_here

4. Update Neo4j Credentials:
Open push_to_neo4j.py and replace the placeholder credentials at the top of the script with your Neo4j Aura URI and Password.

Usage
Step 1: Run the Extraction Pipeline
This will scrape the URLs, query the LLM, and generate the JSON payload.
Bash
python scraper_script.py
(Verify that automated_graph_data.json is created in your directory).

Step 2: Populate the Graph Database
This will read the JSON file and execute the Cypher queries to build the graph.
Bash
python push_to_neo4j.py


Example Cypher Queries
Once the data is pushed to Neo4j, open your Neo4j Workspace and run these commands to visualize the results:

1. View the Entire Knowledge Graph:
Cypher
MATCH (n)-[r]->(m) RETURN n, r, m

2. Find the "Agent" (Kartri) of an Action:
Cypher
MATCH (e:Entity)-[r:ACTS_AS {karaka_role: 'kartri'}]->(a:Assertion)
RETURN e.name AS Agent, a.relation AS Action

3. Trace an Assertion Back to its Web Source (Provenance):
Cypher
MATCH (e:Entity)-[:ACTS_AS]->(a:Assertion)-[:SUPPORTED_BY]->(s:TextWitness)
RETURN e.name AS Entity, a.relation AS Action, s.uri AS SourceURL

