import pandas as pd
import sys
from sqlalchemy import create_engine, text

# =========================================================
# CONFIGURATION
# =========================================================
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

def get_active_stores(engine):
    """
    Returns Store IDs that have matching items.
    """
    # CAST BOTH SIDES TO TEXT AND TRIM WHITESPACE
    query = text("""
        SELECT DISTINCT TRIM(CAST(p.place_id AS VARCHAR))
        FROM fct_payments p
        JOIN fct_order_items f 
          ON TRIM(CAST(p.payment_for_id AS VARCHAR)) = TRIM(CAST(f.order_id AS VARCHAR))
        WHERE p.place_id IS NOT NULL
        ORDER BY 1;
    """)
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return [row[0] for row in result]

def get_store_menu(engine, store_id):
    """
    Fetches the menu for a specific store using a robust TEXT join.
    """
    # We explicitly cast and trim IDs to ensure '123' matches '123'
    query = text(f"""
        WITH store_sales AS (
            SELECT DISTINCT 
                TRIM(CAST(payment_for_id AS VARCHAR)) as order_id
            FROM fct_payments 
            WHERE TRIM(CAST(place_id AS VARCHAR)) = '{store_id}'
        )
        
        SELECT 
            COALESCE(s.title, 'OTHER') AS section,
            m.title AS item_name,
            COUNT(f.id) AS units_sold,
            AVG(f.price) AS price
        FROM fct_order_items f
        JOIN dim_menu_items m ON f.item_id = m.id
        LEFT JOIN dim_sections s ON m.section_id = s.id
        -- ROBUST JOIN: Cast Order ID to Text to match the Payment ID
        JOIN store_sales ss ON TRIM(CAST(f.order_id AS VARCHAR)) = ss.order_id
        GROUP BY s.title, m.title
        ORDER BY section, units_sold DESC;
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df

def main():
    # Windows Encoding Fix
    try:
        if sys.platform.startswith('win'):
            sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    engine = create_engine(DB_CONN)
    
    print(" Scanning for ACTIVE Stores (This may take a moment due to 5M+ rows)...")
    
    try:
        store_ids = get_active_stores(engine)
    except Exception as e:
        print(f" Error finding stores: {e}")
        return

    if not store_ids:
        print(" No active stores found! This means the IDs still don't match.")
        return

    print(f" Found {len(store_ids)} Active Stores: {', '.join(store_ids)}")
    
    # Loop through and print Menus
    for store_id in store_ids:
        print("\n" + "="*60)
        print(f" MENU FOR STORE ID: {store_id}")
        print("="*60)
        
        try:
            df = get_store_menu(engine, store_id)
            
            if df.empty:
                print("   [No Sales Data Found - IDs matched but query returned empty]")
                continue

            current_section = ""
            for _, row in df.iterrows():
                if row['section'] != current_section:
                    current_section = row['section']
                    print(f"\n {current_section.upper()}")
                    print(f"   {'Item Name':<35} | {'Price':<8} | {'Sold':<5}")
                    print("   " + "-"*55)
                
                print(f"   {row['item_name']:<35} | ${row['price']:<7.2f} | {row['units_sold']:<5}")
        
        except Exception as e:
            print(f"    Error analyzing store {store_id}: {e}")

    print("\n End of Menus")

if __name__ == "__main__":
    main()