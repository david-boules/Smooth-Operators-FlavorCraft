import unittest
from sqlalchemy import create_engine, text

class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        # Your real local DB connection
        self.db_url = "postgresql://postgres:admin@localhost:5432/flavor_flow"
        self.engine = create_engine(self.db_url)

    def test_connection_is_alive(self):
        """Ensure we can actually talk to Postgres."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
            self.assertEqual(result, 1)
            print("\n✅ Database Connection: ALIVE")
        except Exception as e:
            self.fail(f"Database connection failed: {e}")

    def test_tables_exist(self):
        """Ensure the critical tables exist and have data."""
        critical_tables = ['fct_order_items', 'fct_payments', 'dim_menu_items']
        
        with self.engine.connect() as conn:
            for table in critical_tables:
                # Check if table has at least 1 row
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"   -> Table '{table}' has {count:,} rows.")
                self.assertGreater(count, 0, f"Table {table} is empty!")

if __name__ == '__main__':
    unittest.main()