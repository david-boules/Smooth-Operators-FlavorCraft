from src.services.menu_analytics import MenuAnalyzer
import pandas as pd
import sys

# =========================================================
# CONFIGURATION
# =========================================================
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def safe_print(df):
    """Helper to print data without crashing on Windows special characters"""
    try:
        if df.empty:
            print("   [No data for this category]")
        else:
            print(df.to_string(index=False))
    except UnicodeEncodeError:
        print(df.to_string(index=False).encode('ascii', 'replace').decode('ascii'))

def main():
    # Force UTF-8 for Windows
    try:
        if sys.platform.startswith('win'):
            sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass 

    try:
        print("[INFO] Connecting to database...")
        analyzer = MenuAnalyzer(DB_CONN)
        
        # 1. GET STORE LIST
        # We fetch the list of available store IDs from the helper we wrote
        store_ids = analyzer.get_store_ids()
        print(f"\n[INFO]  FOUND DATA FOR {len(store_ids)} LOCATIONS")
        print(f"      IDs: {', '.join(store_ids)}")

        # 2. RUN GLOBAL ANALYSIS (Company Wide)
        print("\n" + "="*80)
        print(" GLOBAL BRAND AUDIT (All Stores Combined)")
        print("="*80)
        
        global_stars = analyzer.get_stars() # No filter = Global
        print("\n*** TOP 5 GLOBAL STARS ***")
        safe_print(global_stars[['menu_item_name', 'section_name', 'estimated_profit_per_item', 'total_sold']].head(5))

        # 3. RUN PER-STORE ANALYSIS
        print("\n" + "="*80)
        print(" STORE-BY-STORE DIAGNOSIS")
        print("="*80)

        # Loop through each store to show specific insights
        for store_id in store_ids:
            print(f"\n ANALYSIS FOR STORE ID: {store_id}")
            print("-" * 40)
            
            # Get data specific to this store
            local_stars = analyzer.get_stars(store_filter=store_id)
            local_dogs = analyzer.get_dogs(store_filter=store_id)
            
            # Print Top Star (Best Item)
            if not local_stars.empty:
                top_star = local_stars.iloc[0]
                print(f"    BEST ITEM: {top_star['menu_item_name']} (Sold: {top_star['total_sold']}, Profit: ${top_star['estimated_profit_per_item']:.2f})")
            else:
                print("    BEST ITEM: None (No Stars found)")

            # Print Top Dog (Worst Item)
            if not local_dogs.empty:
                top_dog = local_dogs.iloc[0]
                print(f"    WORST ITEM: {top_dog['menu_item_name']} (Sold: {top_dog['total_sold']}, Profit: ${top_dog['estimated_profit_per_item']:.2f})")
            else:
                print("    WORST ITEM: None (No Dogs found)")

        print("\n Analysis Complete!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("Tip: If 'get_store_ids' is missing, ensure you updated 'src/services/menu_analytics.py' in the previous step.")

if __name__ == "__main__":
    main()