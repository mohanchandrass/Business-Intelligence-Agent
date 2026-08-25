# Skylark BI Agent

## Overview

Skylark BI is a specialized Business Intelligence agent designed for founders and executives. It bridges the gap between raw operational data stored in Monday.com and actionable leadership insights. Rather than forcing executives to build traditional dashboards or write complex queries, Skylark BI provides a polished, ChatGPT-style conversational interface that delivers definitive answers, deterministic business analytics, and executive summaries instantly.

## The Problem

Founders and operational leaders often struggle to extract high-level, cross-functional insights from raw project management tools like Monday.com. While the data exists, querying it requires manual dashboard construction, exporting to Excel, or learning a specific querying language. The resulting data is often messy, unstructured, or disconnected (e.g., pipeline deals vs. active execution work orders).

## The Solution

The agent acts as a conversational AI analyst that dynamically connects to Monday.com, reads operational data (Deals and Work Orders), and orchestrates analytical tools to answer business questions. 

When a user asks a question (e.g., *"How is our energy pipeline looking?"* or *"Compare Q3 deals with active work orders"*), the agent:
1. Translates the intent and fetches a fresh, point-in-time `BusinessDataSnapshot` from Monday.com.
2. Normalizes messy operational data into clean canonical business entities.
3. Orchestrates internal Python-based analytical tools to compute exact, deterministic answers.
4. Explains the findings in a concise, executive-friendly format, complete with data quality warnings if relevant.

## Key Features

* **Monday.com Read-Only Integration**: Safely extracts data via the GraphQL API without modifying the workspace.
* **Dynamic Board Discovery**: Automatically inspects board schemas and semantic column names to identify Deals and Work Orders boards, avoiding hardcoded board IDs.
* **Data Normalization & Resilience**: Casts messy textual data into strict Pydantic domain models.
* **Deterministic Business Analytics**: Computes KPIs using Python (pandas/aggregations) instead of relying on the LLM to do arithmetic, guaranteeing mathematical accuracy.
* **Gemini-Based Orchestration**: Uses Google Gemini and tool-calling to interpret questions, invoke analytical functions, and synthesize answers.
* **Cross-Board Analysis**: Joins Deals (Pipeline) with Work Orders (Execution) using Deal Reference mapping to provide holistic business views (where valid identifiers exist).
* **Data-Quality Warnings**: Tracks normalization errors and explicitly warns the user if records were excluded from the analysis.
* **Conversational Interface**: A modern, minimal, responsive Next.js frontend with dynamic intent-driven loading states.
* **Leadership-Update Support**: Natively structured to summarize insights, risks, and trends suitable for leadership reporting.

## Architecture

The system is designed as a modular, scalable, and efficient architecture rather than a tightly coupled one-off implementation. Monday.com infrastructure, data normalization, domain models, deterministic analytics, agent tooling, LLM orchestration, API services, and frontend presentation are separated into independent layers. 

This separation of concerns allows components to evolve independently while keeping quantitative business logic deterministic and using the LLM primarily for query interpretation, tool selection, and executive-level explanation. The implementation is lightweight enough for a rapid prototype while retaining clear extension points for additional boards, metrics, data sources, and tools.

## Data Flow

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

## Hosted Prototype

The prototype is currently deployed and publicly accessible. 
- **Frontend (Vercel)**: https://business-intelligence-agent-wine.vercel.app/
- **Backend (Render)**: https://business-intelligence-agent-yzpi.onrender.com

*Note: The frontend communicates directly with the Render backend. All Monday.com and Gemini credentials are securely configured server-side. No secrets are committed to the GitHub repository.*

## AI-Assisted Development

In alignment with modern engineering workflows, AI tools were utilized transparently:
- **ChatGPT**: Used for architectural planning, technical reasoning, implementation review, debugging/auditing, data-pipeline analysis, and documentation review.
- **Google Antigravity**: Used as the implementation/coding agent to modify the repository, implement the planned architecture, fix issues, and perform local verification.
- **Google Gemini API**: Used **INSIDE THE PRODUCT** as the runtime LLM for natural-language query understanding, tool selection/orchestration, and concise executive response synthesis.

*ChatGPT and Antigravity were used purely for development assistance and are NOT runtime dependencies of the deployed application.*

## Monday.com Configuration

To configure the application against a Monday.com workspace:
1. Create/import the Deals board.
2. Create/import the Work Orders board.
3. Configure appropriate Monday column types.
4. Create a Monday API token.
5. Add `MONDAY_API_TOKEN` to the backend environment variables.
6. The backend dynamically discovers board schemas via semantic mapping (it does not require hardcoded board IDs).
7. The application strictly reads data.

*Note: Supplied CSV/XLSX sample data is only used to populate the Monday.com workspace and is not hardcoded into the application.*

## Environment Variables

An `.env.example` is provided in the repository. Do not commit actual secrets. 

```env
# SECRETS
GEMINI_API_KEY=
MONDAY_API_TOKEN=

# DEPLOYMENT
MONDAY_API_URL=https://api.monday.com/v2
MONDAY_API_VERSION=2026-07
MONDAY_TIMEOUT_SECONDS=30
MONDAY_MAX_RETRIES=3
CORS_ORIGINS=*

# MODEL CONFIG
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TEMPERATURE=0.0
GEMINI_MAX_OUTPUT_TOKENS=2048
GEMINI_TOP_P=0.95
GEMINI_TOP_K=40

# AGENT CONFIG
AGENT_MAX_TOOL_CALLS=5
AGENT_MAX_CONTEXT_RECORDS=50
```

## Local Development

### 1. Prerequisites
- Node.js v18+
- Python 3.11+

### 2. Running Locally

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

### 3. Access the Application
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Backend Health Check: `http://localhost:8000/api/v1/health`

## Example Queries
Try asking the agent:
- *"Give me a high-level overview of our sales pipeline."*
- *"How many work orders are currently active?"*
- *"Which sectors have the most active deals?"*
- *"Are there any operational bottlenecks in our work orders?"*

## Data Resilience
Real-world data is inherently messy. We enforced robust data resilience measures:
- The normalization pipeline actively catches and corrects missing values, inconsistent text, and typing anomalies (e.g., standardizing disparate client codes).
- The Deal monetary column was exposed by Monday as a generic `numbers` type with masked strings; we applied robust regex-based monetary parsing.
- Missing values and missing cross-board relationships are intentionally preserved. If data is missing (e.g. 176 Work Orders have no corresponding Deal), we flag it as an orphan rather than fabricating links.
- The LLM receives `data_quality` warnings so it can explicitly inform the user when requested figures might be underrepresented.

## Analytics Architecture
**Python owns**: counting, sums, aggregations, filtering, KPI generation, table generation, and data-quality tracking.
**Gemini does NOT calculate business metrics.**
**Gemini is responsible for**: understanding the user's natural-language request, selecting the correct analytical tools, and synthesizing the deterministic results into a concise executive explanation.
Separating these concerns ensures exact, hallucination-free reporting.

## Assumptions & Limitations
- **Read-Only**: The agent only reads data; it cannot update Monday.com boards.
- **In-Memory Caching**: Board schema discovery is cached in-memory. In a production multi-tenant system, this would move to Redis.
- **Pagination Limits**: The current MVP assumes relatively small datasets for the 6-hour hackathon constraints. Large-scale BI would require a materialized data warehouse syncing from Monday webhooks.
- **Discovery Fallbacks**: Dynamic discovery currently maps columns based on predefined semantic aliases. Highly customized workspaces might require manual board mapping overrides.
- **Cross-board Linkages**: We assume reliable identifiers exist to cross-reference Deals with Work Orders. Since the sample dataset contains fully disjoint identifiers, the current engine gracefully processes them as zero-matches rather than fabricating them.

## Challenges
- **Messy Schemas**: Disparate column names across Work Orders and Deals required dynamic semantic discovery.
- **Numeric Typing**: Monday.com presented the Deal monetary field as a masked `numbers` type rather than a native `numeric` type.
- **Missing Identifiers**: The Deal board used anime character names (`Naruto`), while Work Orders used generic serial numbers (`SDPLDEAL-075`). This required establishing robust "orphan" tracking.
- **UX Restraint**: Forcing the LLM to strictly output structured data rather than rewriting the user's metrics as markdown lists.

## Future Improvements
- **Stronger Schema Inference**: Using a lightweight LLM call (e.g. Gemini Flash) to semantically map custom user columns into canonical ones instead of alias arrays.
- **Persistent Caching**: Transitioning to a materialized data layer synced via Monday.com webhooks to support workspaces with hundreds of thousands of items without API latency.
- **Authentication**: Restrict Monday.com API access via OAuth on a per-tenant basis using Clerk or Auth0.
- **Richer Visualizations**: Pass Recharts specs directly from the backend to render sophisticated graphical charts embedded directly in the chat log.
- **Automated E2E Testing**: Add Cypress/Playwright integration tests simulating a full user conversation against a mocked backend.

## Testing
The application uses Pytest for backend unit testing. It contains 8+ deterministic regression tests verifying the exact integrity of the normalization, extraction, mapping, missing value handling, and analytical reconciliation logic against raw Monday.com fixtures. Run `pytest` in the backend directory.

## Assignment Requirement Checklist

| Requirement | Status | Implementation Details |
| --- | --- | --- |
| **Publicly accessible hosted application** | Complete | Deployed on Vercel (frontend) and Render (backend). |
| **GitHub repository containing source code** | Complete | Codebase structured monorepo style in `frontend` and `backend`. |
| **Detailed README** | Complete | This document. |
| **Decision Log** | Complete | Included in `Decision_Log.md` (Max 2 pages). |
| **Monday.com integration** | Complete | Direct GraphQL API (over MCP for deterministic extraction/pagination). |
| **Read-only access** | Complete | App strictly executes read queries. |
| **Dynamic data fetching** | Complete | Schema discovery auto-identifies columns. Snapshot lazily fetches up-to-date data. |
| **No hardcoded CSV data** | Complete | Hardcoded CSV is strictly avoided. |
| **Data resilience (null/missing/dates)** | Complete | Normalization pipeline handles dates, formats currencies, and drops invalid metrics cleanly. |
| **Query understanding** | Complete | Gemini reliably converts user intents into strict tool-calling arguments. |
| **Business intelligence / founder queries** | Complete | Covers Pipeline tracking, Sectoral tracking, Risk bottlenecks, etc. |
| **Cross-board analysis** | Complete | Cross-board relationships are mapped dynamically where shared identifiers actually exist. |
| **Conversational interface** | Complete | Polished UI featuring dynamic responses and structured tables/KPIs. |
| **Graceful API/data errors** | Complete | Bad mappings and missing values result in structured warnings instead of API crashes. |
| **Leadership updates** | Complete | Capable of presenting executive summaries covering KPIs, trends, and caveats naturally. |
| **Tech-stack justification** | Complete | Outlined heavily in this README and the Decision Log. |







# Skylark BI — Decision Log

## 1. Solution Approach
The primary design decision was to build a modular, scalable, and efficient architecture rather than a tightly coupled one-off implementation. The system separates Monday.com integration, schema discovery, normalization, deterministic analytics, agent orchestration, API contracts, and frontend presentation so each layer can evolve independently. This approach was particularly important because the assignment was intentionally open-ended and constrained to a 5–6 hour implementation window. 

## 2. Monday.com Integration: API vs MCP
Direct Monday.com GraphQL API was selected instead of using the Model Context Protocol (MCP).
- **Why**: Interfacing directly with the API provided absolute control over requests, predictable error handling, deterministic parsing, aggressive pagination, and schema inspection with a lower implementation overhead. 
- Monday.com is strictly READ ONLY.
- Data is fetched dynamically.
- CSV/sample data is NOT embedded into the application.

## 3. Dynamic Board Discovery
Hardcoding board IDs and structures restricts usability. We built a dynamic discovery engine instead:
- **BoardCatalog**: Inspects the entire Monday.com workspace.
- **Schema Inspection**: Uses a semantic, alias-based scoring mechanism to identify the true Deals and Work Orders boards based on column structures rather than names.
- **Canonical Models**: Maps whatever Monday returns into canonical Deals and Work Orders models.
This decision ensures the prototype is adaptable seamlessly to different, customized Monday.com setups.

## 4. Data Resilience
Real-world data is inherently messy. We enforced robust data resilience measures:
- The normalization pipeline actively catches and corrects missing values, inconsistent text, and typing anomalies (e.g., standardizing disparate client codes).
- The Deal monetary column was exposed by Monday as a generic `numbers` type with masked strings; we applied robust regex-based monetary parsing.
- Missing values and missing cross-board relationships are intentionally preserved. If data is missing (e.g. 176 Work Orders have no corresponding Deal), we flag it as an orphan rather than fabricating links.
- The LLM receives `data_quality` warnings so it can explicitly inform the user when requested figures might be underrepresented.

## 5. Deterministic Analytics vs LLM Calculations
**Python owns**: counting, sums, aggregations, filtering, KPI generation, table generation, and data-quality tracking.
**Gemini does NOT calculate business metrics.**
**Gemini is responsible for**: understanding the user's natural-language request, selecting the correct analytical tools, and synthesizing the deterministic results into a concise executive explanation.
- **Why**: LLMs are known to hallucinate or miscalculate arithmetic when processing hundreds of raw records. Separating these concerns ensures exact reporting.

## 6. Gemini + Tool Calling
Google Gemini was selected as the orchestration LLM. The `AgentOrchestrator` maps Python functions to Gemini tool definitions dynamically. The agent invokes the deterministic Python analytics tools, receiving exact structured KPI and tabular data back. The final response combines this exact data with a natural language summary.

## 7. UX Decision
The application intentionally avoids presenting a static, overly complex dashboard. Instead, we built a polished, conversational interface tailored for executives and founders. The UI prioritizes low cognitive load: the user asks a question, receives a concise natural-language answer, and immediately sees the most relevant KPIs and tables rendered natively on the screen. 

## 8. Leadership Updates Interpretation
To satisfy the optional "leadership updates" requirement, we interpreted it as the ability to turn raw operational data into an executive-ready summary. The system achieves this by structuring answers around core KPIs, bottlenecks (like "stuck" status items), relevant trends, and data-quality caveats. Founders can ask for high-level summaries and receive cross-board analysis (Deals vs Execution) packaged as a daily briefing.

## 9. Key Assumptions
- The supplied Monday boards accurately represent the relevant business data and schemas.
- Monday.com remains the singular source of truth.
- The application requires strictly read-only access.
- Dynamic board discovery is vastly superior to fixed board IDs.
- Raw operational records may be incomplete or missing associations.
- Cross-board relationships are mapped using reliable identifiers (`deal_reference` matching `serial_number`). Because the live dataset has disjoint identifiers (e.g. `Naruto` vs `SDPLDEAL-075`), 0-matches are reported accurately; missing relationships are NOT fabricated.

## 10. Trade-offs
- **API vs MCP**: API was chosen for deterministic control at the expense of standardized LLM tool integration.
- **In-Memory Caching vs Redis**: Used the FastAPI singleton container for caching board schemas to minimize infrastructure dependencies for a prototype.
- **Deterministic Alias Mapping vs LLM Schema Inference**: Regex/alias checking is faster and highly reliable compared to making expensive LLM calls to classify every column.
- **Request-Scoped Snapshots**: Instead of syncing a database, we fetch a point-in-time snapshot to ensure fresh analysis while avoiding loop fetching. 
- **Structured Output**: Passing structured tables/KPIs down to the frontend prevents the LLM from outputting unreadable markdown blobs. 
*Every trade-off was measured against the tight 5–6 hour assignment timeframe.*

## 11. Challenges
- **Messy Schemas**: Disparate column names across Work Orders and Deals required dynamic semantic discovery.
- **Numeric Typing**: Monday.com presented the Deal monetary field as a masked `numbers` type rather than a native `numeric` type.
- **Missing Identifiers**: The Deal board used anime character names (`Naruto`), while Work Orders used generic serial numbers (`SDPLDEAL-075`). This required establishing robust "orphan" tracking.
- **UX Restraint**: Forcing the LLM to strictly output structured data rather than rewriting the user's metrics as markdown lists.

## 12. What We Would Improve With More Time
- **Stronger Schema Inference**: Using a lightweight LLM call (e.g. Gemini Flash) to semantically map custom user columns into canonical ones instead of alias arrays.
- **Persistent Caching**: Transitioning to a materialized data layer synced via Monday.com webhooks to support workspaces with hundreds of thousands of items without API latency.
- **Authentication**: Restrict Monday.com API access via OAuth on a per-tenant basis using Clerk or Auth0.
- **Richer Visualizations**: Pass Recharts specs directly from the backend to render sophisticated graphical charts embedded directly in the chat log.
- **Automated E2E Testing**: Add Cypress/Playwright integration tests simulating a full user conversation against a mocked backend.
