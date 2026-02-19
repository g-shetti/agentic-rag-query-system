# Smart Home Agentic RAG System

## Overview
This project implements an Agentic RAG system using:
- Neo4j (Graph DB)
- LangGraph (Agent orchestration)
- Gemini (LLM)
- Sentence Transformers (Embeddings)
- FastAPI (API layer)

## Setup

### 1. Start Neo4j
docker-compose up -d

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set environment variables
cp .env.example .env

### 4. Populate database
python -m scripts.populate_db

### 5. Generate embeddings
python -m scripts.create_embeddings

### 6. Create Vector Index
python -m scripts.create_index

### 7. Run API
uvicorn app.main:app --reload

### 8. Test Query
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "lights in bedroom", "include_reasoning": true}'


## API
POST /query

{
  "question": "devices in bedroom",
  "include_reasoning": true
}
