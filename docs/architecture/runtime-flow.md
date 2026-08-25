# Current Runtime Architecture & Flow

This document details the exact, current implementation path from User Query to Final Response for the Skylark BI Agent backend. It reflects what is actually running, distinguishing between implemented logic and pending features.

## 1. Exact Entry Point
- **Path:** `app/main.py -> @app.post("/api/v1/chat")`
- **IMPLEMENTED:** The FastAPI server receives a JSON payload `{"message": "..."}`. A `req_id` is generated and logged, then the request is passed to `ChatApplicationService.process_query()`.
- **NOT IMPLEMENTED:** No conversational persistence (history/session management) or authentication.

## 2. Exact Data Retrieval Path
- **Path:** `app/application/snapshot.py -> BusinessDataService.get_snapshot()` -> `BoardCatalog` -> `MondayDealRepository`
- **IMPLEMENTED:** 
  - `BoardCatalog` dynamically discovers boards using heuristics in `BoardDiscoverer` based on column types and names.
  - `MondayDealRepository` and `MondayWorkOrderRepository` fetch raw data from Monday.com using GraphQL via `MondayClient`.
  - Pagination is implemented in `_fetch_all_items()` to fetch the entire dataset.

## 3. Exact Normalization Path
- **Path:** `app/normalization/normalizer.py -> NormalizationService`
- **IMPLEMENTED:**
  - Raw DTOs are mapped to Domain Models (`Deal`, `WorkOrder`, `Money`).
  - Money parsing strips characters and parses floats. Dates are parsed as `YYYY-MM-DD`.
  - Data quality issues are accumulated into a `DataQualityReport` during this step.
- **NOT IMPLEMENTED / BROKEN:** 
  - **Critical Data Disconnect:** Work Orders map `deal_reference` to the `serial_number` column (e.g., `SDPLDEAL-075`). Deals map `name` to the core Monday name column (e.g., `Naruto`). The normalization logic incorrectly assumes they share the same format or space.

## 4. Exact Snapshot Construction
- **Path:** `app/application/snapshot.py -> BusinessDataSnapshot`
- **IMPLEMENTED:**
  - A `CrossBoardDataset` is built by matching `wo.deal_reference == deal.name`.
  - Work orders that match are attached to `dataset.work_orders_by_deal`.
- **BROKEN:** Because of the normalization mapping issue mentioned above, 0 matches occur (`Matched WOs: 0, Orphan WOs: 176, Unmatched Deals: 346`). 

## 5. Available Tools
- **Path:** `app/agents/tools/registry.py` & `app/agents/tools/__init__.py`
- **IMPLEMENTED:**
  1. `get_pipeline_overview` (returns active deal count and value by stage)
  2. `get_deal_metrics` (returns avg/median/win-loss ratios)
  3. `get_sector_performance` (returns pipeline and execution metrics by sector)
  4. `get_cross_board_metrics` (combines deals and WOs - currently outputs 0 due to Snapshot bug)
  5. `get_work_order_metrics` (returns work order status and values)

## 6. Exact Gemini Request Structure
- **Path:** `app/infrastructure/llm/gemini.py`
- **IMPLEMENTED:**
  - Uses `genai.Client` via `google-genai` Python SDK.
  - Converts internal `messages` dictionary array into `types.Content` with `types.Part` elements.
  - Explicitly disabled `automatic_function_calling` to allow internal orchestration.

## 7. How Tool Calls are Represented Internally
- **Path:** `app/infrastructure/llm/provider.py`
- **IMPLEMENTED:**
  - Gemini responses are parsed and converted to `ToolCallRequest` which holds `tool_name`, `arguments`, and notably the `raw_part` (the original SDK `FunctionCall` object that contains internal grpc metadata like `id` and `thought_signature`).
  - `orchestrator.py` appends this raw content block into the message history dictionary under `"raw_content"`.

## 8. How Tool Results are Returned to Gemini
- **Path:** `app/infrastructure/llm/gemini.py`
- **IMPLEMENTED:**
  - `orchestrator.py` executes the python function mapping to the tool.
  - The tool execution generates a JSON response which is appended as `{"role": "tool", "parts": [...]}`.
  - `gemini.py` creates a `types.Part.from_function_response(name=..., response=...)` and attaches it to a `role="user"` Content block, fulfilling the Google GenAI tool return contract.

## 9. Where the Final Response is Generated
- **Path:** `app/agents/orchestrator.py`
- **IMPLEMENTED:**
  - In a `while` loop (up to 5 turns), the orchestrator yields back to Gemini with the tool results.
  - When Gemini stops outputting `response.function_calls` and returns `response.text`, the string is returned to `ChatApplicationService`, which wraps it in a standard JSON dict and returns to FastAPI.

## 10. Current Known Limitations
- The Cross-Board mapping in the snapshot fails entirely because `deal.name` (Monday item name) does not equal the Work Order's `serial_number` column (e.g. `SDPLDEAL-075`).
- The frontend assumes the presence of inline charts, but the backend currently only returns `answer` and `warnings` without extracting structured metrics into the `insights` and `data` properties of the response contract.
