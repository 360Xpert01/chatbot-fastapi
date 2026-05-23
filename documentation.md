# Multi-Tenant AI Platform: Backend Documentation

Welcome to the backend documentation for the **Multi-Tenant AI Platform**. This application is a high-performance, Retrieval-Augmented Generation (RAG) backend designed to host multiple tenants (organizations) in a single deployment. Each tenant enjoys absolute data isolation, customized brand instructions (system prompts), and a semantic knowledge base populated from uploaded text files.

---

## Table of Contents
1. [Core Features & Business Logic (PRD Overview)](#1-core-features--business-logic-prd-overview)
2. [System Architecture & Core Technologies](#2-system-architecture--core-technologies)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Data Flow & Working Pipelines](#4-data-flow--working-pipelines)
   - [A. Tenant Onboarding](#a-tenant-onboarding)
   - [B. Document Ingestion & RAG Ingestion Pipeline](#b-document-ingestion--rag-ingestion-pipeline)
   - [C. RAG-Powered Contextual Chat Pipeline](#c-rag-powered-contextual-chat-pipeline)
5. [API Routes Reference](#5-api-routes-reference)
   - [Standard Response Envelope](#standard-response-envelope)
   - [Route Index & Specifications](#route-index--specifications)
6. [Quick Starting & Running Guide](#6-quick-starting--running-guide)

---

## 1. Core Features & Business Logic (PRD Overview)

This backend system addresses the needs of a multi-tenant SaaS application providing AI chatbot services:

*   **Strict Multi-Tenant Isolation**: Data is separated securely in a single PostgreSQL database. All documents and vector embeddings are associated with a `tenant_id` (UUID). Queries are strictly scoped to the requesting tenant's workspace.
*   **Custom Prompting & Brand Alignment**: Tenants can define a custom `system_prompt` (e.g., specific customer service guidelines, tone of voice, or operating parameters). The LLM adopts this persona when answering queries.
*   **Sentence-Aware Smart RAG**: Documents are parsed, split using a sentence-aware smart-chunking algorithm to prevent mid-sentence fragmentation, and embedded into vectors. 
*   **High-Quality Semantic Retrieval**: Leverages Google Gemini embeddings and `pgvector` cosine similarity search to retrieve relevant text segments based on user query context.
*   **Flexible Integration**: Designed as a pure REST API returning standardized envelopes, making frontend UI integration simple and uniform.

---

## 2. System Architecture & Core Technologies

The application is built on a modern, robust async Python stack:

```mermaid
graph TD
    Client[Client UI / API Client] -->|HTTP Request| FastAPI[FastAPI Server]
    FastAPI -->|ORM / pgvector queries| PostgreSQL[(PostgreSQL + pgvector)]
    FastAPI -->|Upload / Delete Files| Cloudinary[Cloudinary Storage]
    FastAPI -->|Generate Embeddings| Gemini[Google Gemini API]
    FastAPI -->|Complete Conversational Prompt| OpenRouter[OpenRouter API / GPT-4o-Mini]
```

*   **FastAPI**: Async web framework providing high performance, automatic input validation (via Pydantic), and interactive API documentation (Swagger UI / ReDoc).
*   **SQLModel**: A merge of `SQLAlchemy` and `Pydantic` that allows developers to write single-source-of-truth models serving both as SQL database tables and validation schemas.
*   **PostgreSQL with `pgvector`**: Stores relational tenant records and high-dimensional document chunk vector embeddings, executing fast vector cosine distance calculations.
*   **Google Gemini (`text-embedding-004`)**: Generates premium 768-dimensional semantic embeddings for text chunks.
*   **OpenRouter (`gpt-4o-mini`)**: Used for cost-effective, high-quality, and context-bound conversational completions.
*   **Cloudinary**: Third-party secure cloud object storage for managing uploaded raw tenant documents.

---

## 3. Project Directory Structure

The project code is clean, modular, and organized into encapsulated domains inside the `app/` folder:

```text
├── .env.example                # Template for required environment variables
├── docker-compose.yml          # Local container configuration for Postgres + pgvector
├── requirements.txt            # Python application dependencies
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI initialization, routing configuration, startup lifecycle
│   ├── core/                   # Shared system utilities & core configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings class parsing environment variables
│   │   ├── constants.py        # Centralized magic strings, status codes, and error messages
│   │   ├── database.py         # SQLAlchemy engine setup and SQLModel metadata init
│   │   ├── exceptions.py       # Custom domain exceptions and registration of global handlers
│   │   ├── logging.py          # Unified structured logging configuration
│   │   └── responses.py        # Standardized API response Envelope definitions
│   │
│   ├── services/               # Shared external vendor integrations
│   │   ├── __init__.py
│   │   └── storage.py          # Cloudinary storage upload and fail-safe file deletion services
│   │
│   ├── rag/                    # Isolated RAG domain package
│   │   ├── __init__.py         # Exposes all smart chunking, embedding, LLM, and RAG interfaces
│   │   ├── chunking.py         # Smart sentence-aware text segmenting & boundaries
│   │   ├── embedding.py        # Google Gemini API embedding generation wrapper
│   │   ├── llm.py              # OpenRouter API client executing RAG conversation completion
│   │   └── services.py         # Parameterized pgvector similarity search & generation
│   │
│   └── modules/                # Enclosed business-domain modules
│       ├── tenants/            # Tenant creation, retrieval, updates, and cascading deletion
│       │   ├── __init__.py
│       │   ├── models.py       # SQLModel Tenant table schema
│       │   ├── router.py       # HTTP request handlers & tenant endpoints
│       │   ├── schemas.py      # Pydantic validation schemas (Create, Update, Response)
│       │   └── services.py     # Business operations and database transactions for tenants
│       │
│       ├── knowledge/          # File uploads, text-chunk parsing, embeddings generation
│       │   ├── __init__.py
│       │   ├── models.py       # SQLModel Document and DocumentEmbedding table schemas
│       │   ├── router.py       # HTTP uploads, document deletions, list and retry endpoints
│       │   ├── schemas.py      # Pydantic response structures for documents
│       │   └── services.py     # Text extraction, chunking, embedding, pgvector persistence, retry flows
│       │
│       └── engine/             # Chat engine endpoint routing
│           ├── __init__.py
│           ├── router.py       # HTTP Chat endpoint accepting tenant context validation
│           └── schemas.py      # Conversational thread schemas and chat messages
```

---

## 4. Data Flow & Working Pipelines

### A. Tenant Onboarding
1. A client submits a `POST /api/v1/tenants` request with a tenant name and an optional custom prompt instruction set.
2. The `TenantService` inserts the record into PostgreSQL and generates a persistent unique UUID `tenant_id`.

### B. Document Ingestion & RAG Ingestion Pipeline
1. **Upload**: Client sends file bytes to `POST /api/v1/tenants/{tenant_id}/files/upload`.
2. **Cloud Storage**: The `StorageService` streams bytes to Cloudinary, obtaining a permanent secure URL.
3. **Database Registry**: A record is created in the `documents` table with status `pending`.
4. **Text Extraction**: The text content is extracted from the uploaded file bytes.
5. **Smart Chunking**: `chunk_text_smart` splits the text by sentence delimiters (e.g. `.`, `!`, `?` or double newlines). Sentences are systematically grouped into chunks matching the configured size (default `1000` characters, `200` overlap) without breaking sentences in half.
6. **Vectorization**: For each chunk, the `EmbeddingService` communicates with the Google Gemini API, receiving a 768-dimensional float list representing the semantic vector.
7. **Vector DB Storage**: Chunks and their matching embedding arrays are stored in the `document_embeddings` table. Because `pgvector` is active, PostgreSQL can perform vector comparisons.
8. **Final Status**: Upon successful processing, the document's status in the database transitions to `done`. If any step fails, status goes to `failed`. Failed records can be re-indexed using `POST /api/v1/tenants/{tenant_id}/files/{file_id}/retry`.

### C. RAG-Powered Contextual Chat Pipeline
1. **Request Intake**: Client issues a `POST /api/v1/chat` request containing the current user message and historical message thread. The `X-Tenant-ID` header must be supplied.
2. **Tenant Verification & Persona Load**: The backend ensures the tenant exists and loads their custom `system_prompt` instruction set.
3. **Query Embedding**: The user's query is vectorized via the Google Gemini API to yield a search vector.
4. **Isolated Similarity Search**: A parameterized SQL query executes a Cosine Distance calculation on the `document_embeddings` table, constrained to `tenant_id == X-Tenant-ID`.
5. **Relevance Filter**: Retrieved chunks are sorted by cosine distance. Elements with similarity scores below the threshold (default `0.7`) are discarded. The remaining top chunks are merged to form the context.
6. **LLM Execution**: The tenant system instructions, the retrieved context block, the historical thread, and the new user question are packaged into standard conversational format and dispatched to OpenRouter.
7. **Structured Return**: The finalized response text is wrapped in the standard response envelope and sent back to the user.

---

## 5. API Routes Reference

### Standard Response Envelope
All API endpoints follow a unified response layout to simplify error handling and data parsing on client applications.

```json
{
  "success": true,
  "code": "RESPONSE_CODE_ENUM",
  "message": "Human-readable status description",
  "data": { ... }
}
```

*   **Success Scenarios**: Returns `status_code 200` (or `201`) with `"success": true`.
*   **Error Scenarios**: Returns `status_code 400`, `404`, or `500` with `"success": false`, an descriptive `code` (e.g., `TENANT_NOT_FOUND`), and `data: null`.

---

### Route Index & Specifications

| Method | Endpoint | Description | Request Headers | Request Body | Response Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | API health check & version info | None | None | `200` |
| **GET** | `/health` | Core server liveness check | None | None | `200` |
| **POST** | `/api/v1/tenants` | Onboard a new tenant | None | `TenantCreate` (JSON) | `201`, `500` |
| **GET** | `/api/v1/tenants` | List all registered tenants | None | None | `200`, `500` |
| **GET** | `/api/v1/tenants/{tenant_id}` | Retrieve details of a specific tenant | None | None | `200`, `404` |
| **PUT** | `/api/v1/tenants/{tenant_id}` | Update tenant config or system prompts | None | `TenantUpdate` (JSON) | `200`, `404` |
| **DELETE** | `/api/v1/tenants/{tenant_id}` | Delete tenant and clean up all resources (cascading) | None | None | `200`, `404` |
| **GET** | `/api/v1/tenants/{tenant_id}/files` | List all documents belonging to a tenant | None | None | `200`, `404` |
| **POST** | `/api/v1/tenants/{tenant_id}/files/upload` | Upload a document and index its vector embeddings | None | `file` (Multipart form-data) | `201`, `404`, `500` |
| **POST** | `/api/v1/tenants/{tenant_id}/files/{file_id}/retry` | Manually restart indexing on a failed document | None | None | `200`, `404`, `500` |
| **DELETE** | `/api/v1/tenants/{tenant_id}/files/{file_id}` | Remove a document from database & storage | None | None | `200`, `404` |
| **POST** | `/api/v1/chat` | Issue an isolated, context-aware RAG query | `X-Tenant-ID` (UUID) | `ChatRequest` (JSON) | `200`, `400`, `404`, `500` |

---

## 6. Quick Starting & Running Guide

Follow these steps to set up and run the Multi-Tenant AI Platform backend on your local Windows system.

### Prerequisites
*   [Python 3.10 or 3.11](https://www.python.org/downloads/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended for executing PostgreSQL with pgvector)

---

### Step 1: Clone & Configure Infrastructure
Boot up the PostgreSQL database container pre-packaged with the `pgvector` extension. In your terminal, navigate to the project directory and run:

```bash
docker-compose up -d
```

This starts a background Postgres database listening on port `5432` with username `postgres`, password `supersecretpassword`, and db name `chatbot_platform`.

---

### Step 2: Establish Virtual Environment
Create and activate a virtual environment to manage dependencies locally:

```powershell
# Create environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Or activate on Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

Install the required library packages:

```bash
pip install -r requirements.txt
```

---

### Step 3: Populate Environment Settings (`.env`)
Create a new file named `.env` in the root of the project directory (use `.env.example` as a baseline reference). Fill in your custom API credentials:

```ini
# Database Connection URI (defaults to the docker-compose credentials)
DATABASE_URL=postgresql://postgres:supersecretpassword@localhost:5432/chatbot_platform

# API Keys
OPENAI_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here

# Cloudinary Storage Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Logging Level (Optional: DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

---

### Step 4: Run the Backend Application Server
Execute the server using Uvicorn with hot-reload enabled for local development:

```bash
uvicorn app.main:app --reload
```

You should see logs in the console confirming that logging is initialized, the pgvector database extension has been registered, tables are successfully created, and the application is listening on `http://127.0.0.1:8000`.

---

### Step 5: Test and Verify
*   **API Documentation**: Open your browser and navigate to `http://127.0.0.1:8000/docs` to view the interactive OpenAPI/Swagger Swagger interface. You can execute requests directly from your browser.
*   **Health Check**: Issue a quick GET request to verify the server status:
    ```bash
    curl http://127.0.0.1:8000/health
    ```
    Expected output:
    ```json
    {"status": "ok"}
    ```
