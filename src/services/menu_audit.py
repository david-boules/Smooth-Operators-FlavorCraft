import pandas as pd
import sys
from sqlalchemy import create_engine, text

# =========================================================
# CONFIGURATION
# =========================================================
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

def main():
    try:
        if sys.platform.startswith('win'):
            sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    engine = create_engine(DB_CONN)
    
    print(" DIAGNOSING ID MISMATCH...")
    print("="*60)

    with engine.connect() as conn:
        # 1. CHECK ROW COUNTS (Did Part 2 load?)
        pay_count = conn.execute(text("SELECT COUNT(*) FROM fct_payments")).scalar()
        print(f" Rows in 'fct_payments': {pay_count:,}")
        
        if pay_count < 100000: # Adjust based on your CSV size
            print("     WARNING: This looks low. Did Part 2 actually load?")
        else:
            print("    Looks like a full dataset (Part 1 + Part 2 likely merged).")

        # 2. CHECK ID FORMATS (The "Float" Bug)
        print("\n ID FORMAT CHECK:")
        print("   We need to see if one side has '.0' at the end.")
        
        print("\n   [fct_order_items] Sample Order IDs:")
        orders = conn.execute(text("SELECT DISTINCT order_id FROM fct_order_items LIMIT 5")).fetchall()
        for o in orders:
            print(f"    -> '{o[0]}'  (Type: {type(o[0])})")

        print("\n   [fct_payments] Sample Payment-for-IDs:")
        payments = conn.execute(text("SELECT DISTINCT payment_for_id FROM fct_payments WHERE payment_for_type='order' LIMIT 5")).fetchall()
        for p in payments:
            print(f"    -> '{p[0]}'  (Type: {type(p[0])})")

        # 3. TEST A DIRECT LOOKUP
        # Pick one real order ID and try to find it in payments manually
        test_id = orders[0][0]
        print(f"\n TRACING ORDER ID: {test_id}")
        
        match = conn.execute(text(f"SELECT COUNT(*) FROM fct_payments WHERE CAST(payment_for_id AS VARCHAR) = '{test_id}'")).scalar()
        match_float = conn.execute(text(f"SELECT COUNT(*) FROM fct_payments WHERE CAST(payment_for_id AS VARCHAR) = '{test_id}.0'")).scalar()
        
        if match > 0:
            print(f"    FOUND! Exact match exists.")
        elif match_float > 0:
            print(f"    FOUND, BUT WITH '.0' MISMATCH! (This is the 26% cause)")
        else:
            print(f"    NOT FOUND. This specific order has no payment record.")

if __name__ == "__main__":
    main()