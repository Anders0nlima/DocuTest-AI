# 🚀 DocuTest AI - Runbook & Learning Notes

Welcome to the ultimate DevSecOps documentation generator! This document outlines everything you need to know to run the project locally, understand the architecture, and present this repository as a high-quality asset for technical interviews.

## 🧠 Architecture Overview

**DocuTest AI** operates with a modern, decoupled architecture:

1. **Frontend (React + Vite + TypeScript)**
   - Provides a sleek, glassmorphism UI with reactive drag-and-drop.
   - Implements an asynchronous polling pattern (fetching Job ID status) to prevent browser timeouts on long AI requests.
2. **Backend (FastAPI + Python)**
   - Built around high performance and asynchronous programming.
   - Parses incoming source code, sanitizes it, and delegates the heavy lifting to Google's Gemini 2.5 Flash via a strict DevSecOps system prompt.
3. **Database (Supabase / PostgreSQL)**
   - Handles the persistence layer.
   - Tracks asynchronous Jobs (`PENDING`, `COMPLETED`, `FAILED`) to provide a full history of generated documentation.

## ⚙️ Local Setup Instructions

### 1. Prerequisites

- Python 3.11+
- Node.js 20+
- [Supabase](https://supabase.com/) Account (Free Tier)
- [Google Gemini API Key](https://aistudio.google.com/) (Free Tier)

### 2. Environment Variables

Create a `.env` file inside the `backend/` directory by copying `.env.example`:

```bash
cd backend
cp .env.example .env
```

Fill in your actual keys:

- `SUPABASE_URL`: Your Supabase Project URL.
- `SUPABASE_KEY`: Your Supabase `anon` public key.
- `GEMINI_API_KEY`: Your generated Gemini API key.

### 3. Database Initialization

Execute the SQL script located in `backend/database/schema.sql` directly inside your Supabase project's SQL Editor to create the `jobs` table.

### 4. Running the Backend

```bash
cd backend
# Create and activate virtual environment
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
```

The backend will be live at `http://localhost:8000`. You can check `http://localhost:8000/api/v1/health`.

### 5. Running the Frontend

Open a new terminal window:

```bash
cd frontend
# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be live at `http://localhost:5173`.

## 🛡️ Learning Notes for Technical Interviews

If you are showcasing this project in an interview, make sure to highlight the following technical decisions:

> [!TIP]
> **Asynchronous Orchestration:** "I utilized FastAPI's `BackgroundTasks` to immediately return a Job ID while the LLM processes the code. The React frontend implements a 2-second polling mechanism. This prevents HTTP timeouts and guarantees a fluid UX."

> [!IMPORTANT]
> **Structured AI Outputs:** "Instead of relying on fragile prompt parsing, I configured the Gemini API with a strict Pydantic `GenerationResult` schema (`response_schema`). This guarantees the AI responds in a deterministic JSON format containing the OpenAPI spec, Test Suite, and Security Insights."

> [!NOTE]
> **DevSecOps Prompt Engineering:** "I enforced a `system_instruction` that commands the AI to act as a DevSecOps engineer. It actively hunts for mutable routes (POST/PUT/DELETE) and forces the generation of negative tests (e.g., verifying 401/403 responses without auth tokens)."

> [!TIP]
> **Robust Observability:** "The AI provider wrapper implements strict `try/except` blocks catching `pydantic.ValidationError`, logs exact token consumption for cost monitoring, and tracks total execution time via `time.time()`."
