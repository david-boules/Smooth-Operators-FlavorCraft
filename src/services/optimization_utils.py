import sqlalchemy
from sqlalchemy import text

# ==========================================
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

def main():
    engine = sqlalchemy.create_engine(DB_CONN)
    print(" Optimizing Database for Location Filtering...")
    
    with engine.connect() as conn:
        # This is the critical index for your dashboard dropdown
        print("   -> Creating Index on fct_payments(place_id)... (This takes ~30s)")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_place_id ON fct_payments (place_id);"))
        
        # We also index the boolean "payment_for_type" to speed up filtering
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_type ON fct_payments (payment_for_type);"))
        
        conn.commit()
    
    print(" Optimization Complete. Queries should be 10x faster.")

if __name__ == "__main__":
    main()