# Multi-Tenant AI Platform Backend

An enterprise-ready, Retrieval-Augmented Generation (RAG) multi-tenant AI chat platform backend. Built using FastAPI, SQLModel, PostgreSQL with `pgvector`, Google Gemini, OpenRouter, and Cloudinary.

## Quick Start & Core Documentation

To help you get started quickly and understand the internal workings, database schema, and REST API routes, please refer to the main documentation file:

👉 **[documentation.md](documentation.md)**

### Features Included in the Documentation:
1. **Core Features & PRD Overview**: Details on data isolation, custom tenant personas, and smart RAG retrieval.
2. **System Architecture**: Flow diagram and core technology choices.
3. **Project Directory Structure**: Component-level mapping of all files and folders.
4. **Data Pipelines & Workflows**: In-depth explanation of Tenant Onboarding, Ingestion/Embedding pipeline, and RAG search pipeline.
5. **API Routes Reference**: Exhaustive specifications of endpoints, request models, headers, and standard response envelopes.
6. **Starting & Running Guide**: Simple step-by-step terminal commands for local execution.

---

### Local Run Cheat Sheet

```bash
# 1. Start the PostgreSQL db with pgvector
docker-compose up -d

# 2. Setup virtual environment & dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt

# 3. Configure environment variable keys in .env
cp .env.example .env

# 4. Start the server
uvicorn app.main:app --reload
```
View the interactive API Swagger docs at `http://127.0.0.1:8000/docs` once the server is running.
