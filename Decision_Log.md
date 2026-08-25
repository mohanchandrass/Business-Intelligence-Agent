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
