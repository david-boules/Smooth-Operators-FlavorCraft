## Testing Strategy

To ensure system reliability, we implemented a dual-layer testing strategy:

1.  **Unit Tests (`tests/test_analytics.py`):**
    * Verifies the core "Menu Matrix" algorithms (Stars vs. Dogs logic).
    * Uses mocked data frames to test edge cases without database dependency.

2.  **Integration Tests (`tests/test_connection.py`):**
    * Validates live connectivity to the PostgreSQL database.
    * Performs "Health Checks" on critical tables (`fct_order_items`, `fct_payments`) to ensure data ingestion pipelines were successful.
    * Verifies row counts > 0 to prevent "Silent Failures."

**To run the suite:**
python -m unittest discover tests