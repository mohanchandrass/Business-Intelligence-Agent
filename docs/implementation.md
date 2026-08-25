# Skylark Drones — Master System Implementation Blueprint

This document is the authoritative master implementation plan for the entire Skylark Business Intelligence Agent. It defines the strict architectural boundaries, API contracts, dependency rules, and phased execution roadmap necessary to build the system as a decoupled, parallel-developed, robust application.

---

## 1. Master Architectural Principle

The system follows a strict two-application architecture. The frontend handles presentation and the backend handles all deterministic data processing and AI orchestration.

```text
                    ┌──────────────────────┐
                    │       FRONTEND       │
                    │ Next.js + TypeScript │
                    └──────────┬───────────┘
                               │
                               │ HTTP/JSON
                               │
                    VERSIONED API CONTRACT
                               │
                               ▼
                    ┌──────────────────────┐
                    │       BACKEND        │
                    │ Python + FastAPI     │
                    └──────────┬───────────┘
                               │
                         Application
                               │
                         Domain Logic
                               │
              ┌────────────────┴────────────────┐
              │                                 │
       Infrastructure                     Data / Analytics
              │
       ┌──────┴──────┐
       │             │
   monday.com      Gemini
```

### Strict Boundary Rules
- **Frontend MUST NOT import**: Backend Python code, backend domain models, backend repositories, backend infrastructure, Gemini clients, Monday clients, or analytics implementations.
- **Backend MUST NOT depend on**: React components, Next.js internals, frontend state, or frontend services.
- **The REST API contract (`/api/v1/`) is the ONLY runtime boundary between them.**

---

## 2. Three Distinct Interface Layers

To ensure modularity and enable parallel development, three explicit interface boundaries must be enforced:

### Interface A — Frontend Internal
Frontend components must not directly call `fetch()` against arbitrary endpoints. All API access must pass through a typed API Connector.

```text
UI → Feature/Application Service → API Connector → HTTP
```

**Example:**
`ChatPage` → `ChatService` → `ChatConnector` (interface) → `ApiChatConnector` (implementation) → `POST /api/v1/chat`

This allows for `MockChatConnector` implementations to unblock frontend UI development before the backend is finished.

### Interface B — Frontend ↔ Backend (REST API)
The REST API is the formal contract. Every endpoint must explicitly define its request schema, response schema, error schema, HTTP status codes, authentication, timeouts, idempotency, and versioning behavior.
* All contracts are versioned under `/api/v1/`.
* Undocumented backend behavior must never be relied upon by the frontend.

### Interface C — Backend Internal
The backend relies on strict Dependency Inversion to protect business logic from infrastructure details.

```text
API Router → Application Service → Domain → Repository / Provider Interfaces → Infrastructure Implementations
```

**Examples:**
* **Interface**: `DealRepository`, `WorkOrderRepository`, `LLMProvider`
* **Implementation**: `MondayDealRepository`, `MondayWorkOrderRepository`, `GeminiProvider`

---

## 3. Parallel Development & Contract-First Strategy

The frontend and backend teams can proceed simultaneously without blocking each other.

```text
                API CONTRACT
                     │
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
      FRONTEND TEAM       BACKEND TEAM
           │                   │
      Mock Connector       FastAPI
           │                   │
      UI development       Application
           │                   │
      Contract tests       Domain
           │                   │
           └─────────┬─────────┘
                     │
                Integration
```

### Contract-First Workflow
1. Design endpoint & schemas (Request, Response, Error).
2. Freeze contract.
3. Create backend contract models (Pydantic, `backend/app/contracts/`).
4. Create frontend contract types (TypeScript, `frontend/src/contracts/`).
5. Implement frontend mock (`MockChatConnector`).
6. Implement backend router & logic.
7. Run integration tests.
8. Replace frontend mock with real API connector (`ApiChatConnector`).

---

## 4. API Surface & Contracts

### Initial API Surface
* `GET /api/v1/health`
* `POST /api/v1/chat`
* `GET /api/v1/metadata`

*Future candidate endpoints (post-canonical modeling):*
* `GET /api/v1/dashboard/overview`
* `GET /api/v1/dashboard/pipeline`
* `POST /api/v1/leadership-update`

### Chat API Contract (Preliminary)
**Endpoint**: `POST /api/v1/chat`

**Request Schema (Concept):**
```json
{
    "message": "...",
    "conversation_id": "...",
    "context": {}
}
```

**Response Schema (Concept):**
```json
{
    "conversation_id": "...",
    "answer": "...",
    "insights": [],
    "data": {},
    "citations": [],
    "data_quality": [],
    "follow_up_questions": [],
    "metadata": {}
}
```
*Note: This response structure supports founder-level answers (insights, tables, citations) rather than just raw LLM text streams.*

### Error Contract
One standardized API error structure across all endpoints.

**Schema:**
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human readable message",
        "details": {},
        "request_id": "req-12345"
    }
}
```
**Categories**: `VALIDATION_ERROR`, `AUTHENTICATION_ERROR`, `AUTHORIZATION_ERROR`, `NOT_FOUND`, `RATE_LIMITED`, `UPSTREAM_ERROR`, `DATA_QUALITY_ERROR`, `INTERNAL_ERROR`, `SERVICE_UNAVAILABLE`.

### Request IDs & Observability
* Every backend request receives a unique `request_id`.
* It appears in backend logs and error responses for end-to-end traceablity (Frontend → Backend → Gemini → Monday).
* Secrets (API keys, tokens) must never be logged.

---

## 5. Data & Analytics Boundaries

### Data Layer Separation
Raw Monday.com data (infrastructure DTOs) MUST NOT leak into the domain, analytics, agent prompts, or frontend.

```text
Raw Monday Data → Infrastructure DTOs → Normalization → Canonical Domain Model → Analytics → Agent Tools → API Response
```
*Example*: Monday's `numeric_mm6jty17` becomes `Deal.value` in the domain.

### Normalization Boundary
A deterministic normalization layer resolves structural inconsistencies:
* Maps ambiguous customer codes (`WOCOMPANY_xxx` vs `COMPANY_xxx`).
* Handles currency defaults, whitespace, date formatting, and duplicate records.
* The LLM **must not** perform basic data cleaning; it consumes pre-normalized canonical models.

### Analytics Boundary
Business calculations (pipeline value, conversion rates, counts) **must be deterministic** and computed via Python algorithms. The LLM must not do arithmetic on hundreds of rows.

```text
Question → Agent Coordinator → Intent → Select Analytics Tool → Deterministic Calculation → Structured Result → LLM Explanation
```

### Data Quality in API Responses
Data quality is a first-class concept. The API response must expose missing fields, excluded records, unmatched joins, and stale data. The frontend renders these caveats (e.g., "Pipeline value is based on 92 of 97 deals because 5 records have missing values."). Do not hide data quality problems.

---

## 6. Agent Architecture & Safety

The agent does not query Monday.com arbitrarily. It acts as an orchestrator that selects strictly defined internal tools.

**Tool Candidates (To be finalized):**
* `get_pipeline_summary`
* `get_sector_performance`
* `compare_deals_and_work_orders`
* `get_data_quality_report`

**Agent Safety Constraints:**
* Strictly enforced maximum tool calls, context size limits, and execution timeouts.
* Halts on invalid tool arguments.
* Built-in hallucination prevention: The agent must explicitly state when data is unavailable rather than inventing it.

**Conversation State:**
* Backend remains stateless at the HTTP layer using `conversation_id`.
* Frontend state is not the source of truth for business data.

**Leadership Update Feature:**
* A deterministic aggregation of business metrics, risks, wins, and operational concerns. The analytics layer supplies the hard numbers; the LLM generates the narrative summary.

---

## 7. Configuration, Caching & Testing Strategies

* **Configuration**: Centralized using `pydantic-settings` to ensure fail-fast validation of critical secrets (`GEMINI_API_KEY`, `MONDAY_API_TOKEN`) upon startup.
* **Mock Strategy**: Frontend relies on Interface mocks (`MockChatConnector`). Backend relies on Fake/Mock infrastructure (`FakeDealRepository`, `MockLLMProvider`).
* **Testing Strategy**: 
  * Frontend: Unit, Component, Connector.
  * Backend: Unit, Integration, API Contract.
* **Caching (Future-Proofing)**: Built modularly to allow in-memory caches to be swapped with Redis later. Avoid premature distributed infrastructure during the hackathon.

---

## 8. Frontend & Backend Architectures

### Frontend (`frontend/src/`)
* `app/`: Routing/pages (Next.js App Router).
* `components/`: Generic reusable UI elements.
* `features/`: Feature-specific UI and business logic.
* `services/`: Application-facing frontend services.
* `contracts/`: Strict API request/response TS types.
* `hooks/`: React integration.
* `lib/`: Generic frontend utilities.
* `config/`: Frontend runtime configuration.

### Backend (`backend/app/`)
* `api/`: FastAPI routers and dependency injection.
* `application/`: High-level orchestrators and use cases.
* `domain/`: Core business logic, entities, interfaces (No infrastructure imports).
* `infrastructure/`: Concrete implementations (Monday API, Gemini API, DB).
* `normalization/`: Data cleaning pipelines.
* `analytics/`: Deterministic business calculators.
* `agents/`: LLM orchestration and prompt engineering.
* `contracts/`: Pydantic schemas for the REST API.
* `config/`: Pydantic settings.
* `errors/`: Custom error definitions and handlers.

*Required Backend Dependency Direction*: `API` → `Application` → `Domain` ← `Infrastructure`

---

## 9. Phased Implementation Roadmap

Every phase defines strict deliverables, interfaces, and testing requirements.

### PHASE 0: Architecture & Repository Setup
* **COMPLETE**: Next.js and FastAPI scaffolding, environment management.

### PHASE 1: Discovery & Diagnostics
* **COMPLETE**: API connectivity verified, board schemas pulled, relationship keys identified (`Serial #` matches `name`).

### PHASE 2: Canonical Data Model & Deterministic Normalization
* **Deliverables**: Domain models (`Deal`, `WorkOrder`), normalized representations, data quality model, cross-board relationships validation, and related unit tests.

### PHASE 3: Monday Data Access Layer
* **Deliverables**: Repository interfaces, concrete Monday repositories, pagination handling, resilience, and mapping infrastructure from DTOs to Domain.

### PHASE 4: Deterministic BI Analytics
* **Deliverables**: Pipeline metrics, sector analysis, work order metrics, structured analytical outputs, and cross-board analytics calculators.

### PHASE 5: Agent Orchestration
* **Deliverables**: Agent coordinator, query understanding, tool registry, tool execution loop, Gemini integration, and executive answer generation.

### PHASE 6: Backend API
* **Deliverables**: REST contracts, `/api/v1/chat` endpoint, error handling implementation, request IDs middleware, and API validation.

### PHASE 7: Frontend UI & Integration
*(May begin in parallel during Phase 6 using mock connectors)*
* **Deliverables**: Conversational UI, loading/error states, insight cards, data-quality warnings, API connector, and mock connector swap.

### PHASE 8: Leadership Updates
* **Deliverables**: Executive summary generation pipeline (Key metrics, risks, wins, trends, and recommended actions).

### PHASE 9: Testing / Hardening
* **Deliverables**: Unit, integration, contract, and E2E tests. Failure testing and API resilience verification.

### PHASE 10: Deployment / Submission
* **Deliverables**: Production build, environment configuration, hosted frontend/backend, finalized README, and demo validation.

---

## 10. Master Plan Status

* **Current Phase**: Phase 2 — Canonical Data Model & Normalization
* **Completed**: Phase 0, Phase 1
* **Next**: Phase 2
