# Skylark BI Agent — Decision Log

## 1. Monday.com API vs MCP
**Decision:** Direct Monday.com GraphQL API.
**Reason:** While MCP (Model Context Protocol) is standardizing LLM-to-tool connections, building a custom GraphQL integration provided absolute control over deterministic parsing, aggressive pagination, and robust error handling essential for this 6-hour hackathon constraints.

## 2. Dynamic Board Discovery vs Hardcoded Board IDs
**Decision:** Dynamic Board Discovery.
**Reason:** The assignment required building a generalized BI agent rather than a script locked to a specific workspace. The `SchemaInspector` dynamically identifies Deals and Work Orders boards based on column semantics, allowing it to adapt to different Monday.com setups seamlessly.

## 3. Deterministic Python Analytics vs LLM-Generated Calculations
**Decision:** Deterministic Python analytics.
**Reason:** LLMs hallucinate or fail at arithmetic when dealing with hundreds of records. All KPIs and aggregations are computed deterministically in Python using the canonical data models. The LLM is only used to synthesize the resulting exact numbers into an executive summary.

## 4. Gemini + Tool Calling for Agent Orchestration
**Decision:** Google Gemini with structured tool calling.
**Reason:** Gemini provides fast and reliable tool-calling capabilities. The `AgentOrchestrator` maps Python functions to Gemini tool definitions dynamically and manages the conversation loop, ensuring the LLM can fetch the exact analytical slice it needs to answer the user's prompt.

## 5. Canonical Domain Models and Normalization Layer
**Decision:** Strict Pydantic domain models separating Monday.com DTOs from Business logic.
**Reason:** Monday.com data is messy (e.g., text instead of numbers, varying statuses). The Normalization Layer catches invalid formats and casts everything to canonical `Deal` and `WorkOrder` entities. Analytics run strictly against the canonical models.

## 6. Query-Scoped Data-Quality Reporting
**Decision:** Explicitly track and report normalization failures.
**Reason:** Executives must trust the data. If $50k in deals is excluded because a user typed "50k" instead of "50000" in Monday.com, the `DataQualityReport` tracks the exclusion and the LLM explicitly warns the user about the missing data in its response.

## 7. Request-Scoped BusinessDataSnapshot
**Decision:** Fetch all relevant data lazily once per request into a `BusinessDataSnapshot`.
**Reason:** Prevents the agent from endlessly querying Monday.com within a single multi-turn tool loop. The snapshot acts as an immutable, point-in-time state for all deterministic tools to query against.

## 8. Lightweight In-Memory Board Catalog Caching
**Decision:** In-memory caching for `BoardCatalog` discovery.
**Reason:** Fetching and inspecting all board schemas is expensive. Caching schemas in-memory drastically speeds up query times without introducing external infrastructure dependencies like Redis, aligning with the hackathon's time constraint.

## 9. Structured KPI/Table Response Data
**Decision:** Tools return structured data sets (JSON/dicts).
**Reason:** Instead of asking the LLM to format markdown tables blindly, returning strict data objects forces the LLM to write factual summaries based on concrete properties. This prevents hallucinations in reporting.

## 10. Frontend Simplicity and Executive UX
**Decision:** A ChatGPT-style conversational interface over a static dashboard.
**Reason:** Executives want answers, not tools to learn. The UI prioritizes a polished, intent-aware loading state, clean typography, and a conversational flow that presents clear KPIs and explanations directly.

## 11. Leadership Updates Interpretation
**Decision:** Embedded into the agent prompt and deterministic tools.
**Reason:** The system satisfies the optional leadership update requirement by instructing the agent to structure answers around KPIs, risk factors, and trends. When asked for a summary, the agent leverages cross-board analysis (Deals vs Execution) to present a high-level executive briefing.

---

## What We Would Improve With More Time

1. **Broader Schema Inference & Relationship Discovery**: Use a lightweight LLM call to classify messy columns dynamically instead of relying on regex/semantic alias lists.
2. **Persistent Caching & Webhooks**: Transition from an on-demand fetching model to a materialized view synced via Monday.com webhooks to support workspaces with hundreds of thousands of items instantly.
3. **Authentication & Multi-User Support**: Add Clerk/Auth0 and restrict Monday.com API access via OAuth on a per-tenant basis.
4. **Richer Visualizations**: Pass structured data (Recharts/Chart.js specs) directly from the backend to the frontend for rich, interactive, deterministic charting embedded in the chat log.
5. **E2E Testing**: Add Cypress/Playwright tests covering the full flow from frontend UI input to the mocked Monday.com backend response.
