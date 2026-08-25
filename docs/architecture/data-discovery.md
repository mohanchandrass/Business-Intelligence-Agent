# Monday.com Data Discovery

The backend architecture uses a dynamic data discovery layer instead of hardcoded board IDs.

## Motivation

Initially, Phase 1 relied on `.env` variables (`MONDAY_DEALS_BOARD_ID` and `MONDAY_WORK_ORDERS_BOARD_ID`) to bind to specific boards. While sufficient for a proof of concept, this approach lacks scalability across diverse customer workspaces. The system must adapt dynamically without requiring manual configuration.

## Architecture

1. **Board Discovery:** The `BoardDiscoverer` hits the Monday GraphQL API to fetch metadata and columns for all accessible boards.
2. **Schema Inspection:** The `SchemaInspector` executes deterministic algorithms against column titles and metadata to classify a board (e.g., `DEALS` or `WORK_ORDERS`).
3. **Semantic Mapping:** Once a board is classified, a `SemanticMapping` bridges abstract concepts (like "Deal Value") to raw Monday column IDs (like "numeric_mm6jty17").
4. **Board Catalog:** The `BoardCatalog` caches these results in memory.
5. **Dynamic Repositories:** Domain repositories (`MondayDealRepository` and `MondayWorkOrderRepository`) initialize dynamically via the catalog and apply the `SemanticMapping` when converting Raw DTOs.
6. **Existing Normalization:** Domain records continue through the existing data-quality pipeline unchanged.

This approach guarantees robust, environment-agnostic execution while preserving the strict typing of the business logic.
