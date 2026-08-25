# Data Pipeline Audit

## 1. Actual Monday Schema Discovered
- **Deals Board**: Identified successfully based on board name ("Deals Board"). Contains columns: Name, Client Code, Deal Status, Close Date (A), Closure Probability, Masked Deal value, Tentative Close Date, Deal Stage, Product deal, Sector/service, Created Date.
- **Work Orders Board**: Identified successfully. Contains columns: Name, Customer Name Code, Serial #, Nature of Work, Execution Status, Data Delivery Date, Date of PO/LOI, Document Type, Sector, various masked amounts, and Invoice status.

## 2. Semantic Mappings
A deterministic alias matching and type-scoring system was implemented.
- `deal_value` matched to `numeric_mm6jty17` ("Masked Deal value").
- `amount_excl_gst` matched to `numeric_mm6jcs5f` ("Amount in Rupees (Excl of GST)").
- `deal_reference` (serial_number) matched to `dropdown_mm6j6em5` ("Serial #").
- `po_date` matched to `date_mm6j2525` ("Date of PO/LOI").
- `client_code` (customer_code) matched to client codes on both boards.

## 3. Representative Parsed Records
- Deal: Name="Naruto", Client="COMPANY089", Stage="B. Sales Qualified Leads", Status="Open", Sector="Mining". Value mapping issues due to incorrect `numbers` type mapping were fixed.
- Work Order: Name="Scooby-Doo", Customer="WOCOMPANY_002" -> mapped to `COMPANY_002`. Serial #="SDPLDEAL-075". 

## 4. Normalization Behavior
- Handled missing numeric values by issuing `MISSING_VALUE` warnings instead of silently omitting deals or raising exceptions.
- Unified `WOCOMPANY_xxx` prefix into standard `COMPANY_xxx` prefix for potential future joins.
- Parsed monetary values dynamically removing non-numeric characters.

## 5. Cross-Board Relationship Result
- Verified that **NO legitimate shared identifier exists** in the sample data.
- The `Serial #` column in Work Orders holds values like `SDPLDEAL-075`.
- The Deal identifiers are names like `Naruto` or `Sasuke`.
- Because these do not overlap, 176 work orders were deterministically marked as "orphan_work_orders" and 346 deals were marked as unmatched.
- **0 matches were preserved legitimately as a dataset limitation.**

## 6. Analytics Calculations
- Upgraded the Analytics classes (`PipelineAnalytics`, `DealAnalytics`, `WorkOrderAnalytics`, `CrossBoardAnalytics`, `SectorAnalytics`) to perform all numeric totals deterministically.
- All classes now return frontend-compatible `VisualizationData` containing `kpis` and `tables`.
- Gemini no longer processes tables or calculates KPIs.

## 7. Final ChatResponse Schema
```json
{
  "answer": "Concise natural language synthesis from Gemini",
  "data": [
    {"type": "kpi", "title": "Active Deals", "value": "49"},
    {"type": "table", "title": "Pipeline Distribution", "columns": [...], "data": [...]}
  ],
  "data_quality": [
    {"severity": "warning", "message": "2 open deals have no assigned monetary value."}
  ]
}
```

## 8. Caching Behavior
- `BoardCatalog`: Maintained as a Singleton application cache. Discovery only happens once on startup or explicit refresh.
- `BusinessDataSnapshot`: Passed into `AgentOrchestrator` as a lazy `Callable` factory. Only fetched once when the first analytics tool is invoked.
- Avoids retrieving Monday data completely for conversational "HI" queries.

## 9. Test Results
- Added 8 unit tests in `test_regression.py` covering mapping, extraction, and analytical reconciliation.
- Tests executed successfully with `pytest`, confirming the exact integrity of the pipeline logic.
