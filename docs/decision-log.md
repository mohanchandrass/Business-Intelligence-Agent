# Skylark Drones — Decision Log

## Decision 1 — Two-Application Architecture
**Decision:** Two-application architecture.
**Reason:** Next.js handles presentation well, while Python provides superior tools for deterministic data processing and AI orchestration.
**Trade-off:** Slightly higher complexity in setup, but vastly better maintainability.

## Decision 2 — Frontend Stack
**Decision:** Next.js for frontend.
**Reason:** Allows rapid development of the UI and components.
**Trade-off:** React ecosystem overhead, but acceptable given the capabilities.

## Decision 3 — Backend Stack
**Decision:** FastAPI/Python for backend.
**Reason:** Python is ideal for messy data (pandas/openpyxl) and FastAPI provides rapid, type-safe API generation.
**Trade-off:** Additional service to run locally, but ensures proper separation of concerns.

## Decision 4 — Communication Boundary
**Decision:** REST API boundary (`/api/v1/`).
**Reason:** Enforces a strict contract between the frontend and backend, allowing simultaneous independent development.
**Trade-off:** Requires defining and maintaining schema contracts.

## Decision 5 — Architecture Pattern
**Decision:** Modular monolith rather than microservices.
**Reason:** Keeps the deployment simple for a 5-hour hackathon while retaining the benefits of modularity.
**Trade-off:** Less scalable than true microservices, but perfectly appropriate for this stage.

## Decision 6 — Dependency Rule
**Decision:** Strict Dependency inversion.
**Reason:** Business logic (domain) must not depend on infrastructure details (like monday.com API). Infrastructure implements domain interfaces.
**Trade-off:** Initial setup requires more boilerplate (interfaces/protocols).

## Decision 7 — Data Source
**Decision:** Dynamic monday.com access.
**Reason:** Meets assignment requirements to not hardcode data; ensures the BI agent uses live data.
**Trade-off:** Requires handling API limits and pagination.

## Decision 8 — AI Provider
**Decision:** Gemini provider abstraction.
**Reason:** Prevents vendor lock-in and allows for easier test mocking.
**Trade-off:** Extra abstraction layer over the native SDK.

## Decision 9 — Analytics
**Decision:** Deterministic analytics before LLM explanation.
**Reason:** LLMs are unreliable at arithmetic across hundreds of records; Python handles computation deterministically.
**Trade-off:** Requires writing manual aggregation logic instead of just prompting the LLM.

## Decision 10 — Domain Models
**Decision:** Domain model deferred until actual data inspection.
**Reason:** Prevents building assumptions that conflict with the actual monday.com boards.
**Trade-off:** Delays full implementation of application logic until data profiling is done.

## Decision 11 — Pydantic Configuration Architecture
**Decision:** Use `pydantic-settings` to parse `.env` files and validate settings with `default_factory` for strict validation.
**Reason:** The backend should fail-fast at startup if critical API credentials are missing. `default_factory` avoids baking in import-time environment state into class defaults, ensuring robust testability.
**Trade-off:** slightly more verbose configuration definitions.

## Decision 12 — Cross-Board Join Strategy
**Decision:** Use `Serial #` ("SDPLDEAL-XXX") in the Work Orders board to map to the `name` column in the Deals board.
**Reason:** Data profiling revealed that Customer Identifiers differ slightly (`COMPANY` vs `WOCOMPANY`), but the `Serial #` is a strict string match to the Deal Identifier.
**Trade-off:** Demands a normalization layer before aggregation, but guarantees high fidelity joins.
