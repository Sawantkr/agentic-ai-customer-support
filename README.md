# Agentic AI Customer Support

AI-powered customer support system built with
LangGraph, FastAPI and Streamlit.

## Features
- Intent-based routing
- Specialized support workflows
- Human-in-the-loop escalation
- Conversation persistence
- SQLite checkpointing
- FastAPI REST API
- Streamlit chat interface
- Automated tests
- Docker support

## Architecture

User
 ↓
Streamlit
 ↓
FastAPI
 ↓
LangGraph
 ↓
Intent Classification
 ↓
Specialized Workflow
 ├── Account
 ├── Billing
 ├── Technical
 └── General
 ↓
Response / Human Escalation

## Tech Stack

Python
LangGraph
LangChain
Groq
FastAPI
Streamlit
SQLite
PostgreSQL
Docker
Pytest

## Run Locally

python -m venv venv

Windows:
venv\Scripts\Activate.ps1

pip install -r requirements.txt

Create .env and add:

GROQ_API_KEY=your_api_key
CHECKPOINTER_BACKEND=sqlite
DATABASE_PATH=support_checkpoints.db

Run backend:

uvicorn api.main:app --reload

Run frontend:

streamlit run frontend/app.py

## API

GET /health
POST /support
GET /support/{thread_id}
POST /support/resume

## Human-in-the-Loop

When automatic resolution fails:

User Request
 ↓
Agent Workflow
 ↓
Escalation
 ↓
Human Review
 ↓
Workflow Resume
 ↓
Final Response

## Testing

pytest -v

## Author

Sawant Kumar Sawant

GitHub:
https://github.com/Sawantkr