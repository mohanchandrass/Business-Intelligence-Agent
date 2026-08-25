# Skylark BI Agent

Skylark BI is a specialized Business Intelligence agent designed for founders and executives. It bridges the gap between raw operational data stored in Monday.com and actionable leadership insights. Rather than forcing executives to build traditional dashboards or write complex queries, Skylark BI provides a polished, ChatGPT-style conversational interface that delivers definitive answers, deterministic business analytics, and executive summaries instantly.

## What It Does

The agent acts as a conversational AI analyst that dynamically connects to Monday.com, reads operational data (Deals and Work Orders), and orchestrates analytical tools to answer business questions. 

When a user asks a question (e.g., *"How is our energy pipeline looking?"* or *"Compare Q3 deals with active work orders"*), the agent:
1. Translates the intent and fetches a fresh, point-in-time `BusinessDataSnapshot` from Monday.com.
2. Normalizes messy operational data into clean canonical business entities.
3. Orchestrates internal Python-based analytical tools to compute exact, deterministic answers.
4. Explains the findings in a concise, executive-friendly format, complete with data quality warnings if relevant.

## Key Capabilities

* **Monday.com Read-Only Integration**: Safely extracts data via the GraphQL API without modifying the workspace.
* **Dynamic Board Discovery**: Automatically inspects board schemas and semantic column names to identify Deals and Work Orders boards, avoiding hardcoded board IDs.
* **Data Normalization & Resilience**: Casts messy textual data into strict Pydantic domain models.
* **Deterministic Business Analytics**: Computes KPIs using Python (pandas/aggregations) instead of relying on the LLM to do arithmetic, guaranteeing mathematical accuracy.
* **Gemini-Based Orchestration**: Uses Google Gemini and tool-calling to interpret questions, invoke analytical functions, and synthesize answers.
* **Cross-Board Analysis**: Joins Deals (Pipeline) with Work Orders (Execution) using Deal Reference mapping to provide holistic business views.
* **Data-Quality Warnings**: Tracks normalization errors and explicitly warns the user if records were excluded from the analysis.
* **Conversational Interface**: A modern, minimal, responsive Next.js frontend with dynamic intent-driven loading states.
* **Leadership-Update Support**: Natively structured to summarize insights, risks, and trends suitable for leadership reporting.

## Architecture

The system is designed as a modular, scalable, and efficient architecture rather than a tightly coupled one-off implementation. Monday.com infrastructure, data normalization, domain models, deterministic analytics, agent tooling, LLM orchestration, API services, and frontend presentation are separated into independent layers. 

This separation of concerns allows components to evolve independently while keeping quantitative business logic deterministic and using the LLM primarily for query interpretation, tool selection, and executive-level explanation. The implementation is lightweight enough for a rapid prototype while retaining clear extension points for additional boards, metrics, data sources, and tools.

### Data Flow

```text
User Query (Frontend)
  ↓
FastAPI Backend (/api/v1/chat)
  ↓
Agent Orchestrator (Gemini Tool Loop)
  ↓
Tool Call (e.g. get_pipeline_overview)
  ↓ (lazy fetch on first tool call)
Board Catalog & Discovery (Monday.com GraphQL)
  ↓
Raw DTOs
  ↓
Data Normalization & Error Tracking
  ↓
BusinessDataSnapshot (Canonical Entities)
  ↓
Analytical Tool Execution (Deterministic Python)
  ↓
Gemini Synthesizes Response
  ↓
Executive Summary sent to Frontend
```

*Note: Dynamic Monday.com board discovery was chosen instead of hardcoding the supplied board IDs because the goal is to demonstrate a generalized BI agent capable of inspecting and adapting to a workspace dynamically.*

## Technology Stack

### Frontend
* **Next.js (App Router)**: Fast UI development and React server components.
* **TypeScript & Tailwind CSS v4**: Strict typing and utility-first styling for a polished, Monday-inspired aesthetic.
* **Lucide React**: Clean, modern iconography.

### Backend
* **Python & FastAPI**: High-performance, type-safe API generation ideal for orchestrating data logic and AI workflows.
* **Google GenAI SDK (Gemini)**: Powers intent recognition and tool-calling orchestration.
* **Pydantic**: Strict data validation, environment configuration, and domain modeling.
* **Pytest**: Comprehensive unit and integration testing.

## Implementation Status

* **Dynamic Board Discovery**: Implemented (SchemaInspector automatically maps columns to canonical types based on semantic aliases). Some test coverage edge-cases failing locally.
* **Data Normalization**: Implemented (Pydantic DTOs map to canonical `Deal` and `WorkOrder` entities).
* **Gemini Tool Calling Loop**: Implemented and verified (Preserves `thought_signature` and raw SDK parts for multi-turn loops).
* **Frontend UI**: Implemented (Fully functional ChatGPT-style interface with context-aware loading states and proper auto-scrolling).
* **Cross-Board Joins**: Implemented (Joins `deal.name` to `wo.deal_reference`).
* **Hosted Prototype**: *Pending (Local deployment only at this stage).*

## Setup & Execution

### 1. Prerequisites
- Node.js v18+
- Python 3.11+
- A valid Gemini API Key (`GEMINI_API_KEY`)
- A valid Monday.com API Token (`MONDAY_API_TOKEN`)

### 2. Environment Configuration
Create a `.env` file in the project root based on `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key
MONDAY_API_TOKEN=your_monday_token

MONDAY_API_URL=https://api.monday.com/v2
MONDAY_API_VERSION=2026-07
GEMINI_MODEL=gemini-2.5-flash
```

*(Note: While `MONDAY_DEALS_BOARD_ID` and `MONDAY_WORK_ORDERS_BOARD_ID` exist in the example, the system relies on dynamic discovery and does not strictly require them).*

### 3. Running Locally

A convenient startup script is provided for Windows:
```bash
start-dev.bat
```

Alternatively, run them manually:

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Backend Health Check: `http://localhost:8000/api/v1/health`

## Example Queries
Try asking the agent:
- *"Give me a high-level overview of our sales pipeline."*
- *"How many work orders are currently active?"*
- *"Compare our Q3 energy deals with the ongoing execution work orders."*
- *"Are there any operational bottlenecks in our work orders?"*

## Limitations and Assumptions
- **Read-Only**: The agent only reads data; it cannot update Monday.com boards.
- **In-Memory Caching**: Board schema discovery is cached in-memory. In a production multi-tenant system, this would move to Redis.
- **Pagination Limits**: The current MVP assumes relatively small datasets for the 6-hour hackathon constraints. Large-scale BI would require a materialized data warehouse syncing from Monday webhooks.
- **Discovery Fallbacks**: Dynamic discovery currently maps columns based on predefined semantic aliases. Highly customized workspaces might require manual board mapping overrides.
