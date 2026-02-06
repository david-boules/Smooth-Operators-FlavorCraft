from src.services.menu_analytics import MenuAnalyzer
import pandas as pd


''' 
    You need to make a database called "flavor_flow" using postgresql on your pc, and ensure that all csv files
    are loaded into that db. 
'''

# Format: postgresql://postgres:password@host:port/database_name
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

# OPTIONAL: Configure Pandas to not cut off wide columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

try:
    analyzer = MenuAnalyzer(DB_CONN)
    
    stars = analyzer.get_stars()
    dogs = analyzer.get_dogs()
    plowhorses = analyzer.get_plowhorses()
    puzzles = analyzer.get_puzzles()

    
    print("\n" + "="*80)
    print(f" TOP 50 STARS (High Profit & High Popularity)")
    print("   ACTION: Keep these, promote them, do not change recipes.")
    print("="*80)

    # change the .head() parameter to limit number of items shown

    print(stars[['menu_item_name', 'section_name', 'estimated_profit_per_item', 'total_sold']].head(30).to_string(index=False))

    print("\n" + "="*80)
    print(f" TOP 50 DOGS (Low Profit & Low Popularity)")
    print("   ACTION: Remove from menu or completely reinvent.")
    print("="*80)
    print(dogs[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']].head(30).to_string(index=False))

    print("\n" + "="*80)
    print(f" TOP 50 PLOWHORSES (Low Profit & High Popularity)")
    print("   ACTION: Increase price slightly or lower food cost.")
    print("="*80)
    print(plowhorses[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']].head(30).to_string(index=False))

    print("\n" + "="*80)
    print(f" TOP 50 PUZZLES (High Profit & Low Popularity)")
    print("   ACTION: Rename, take better photos, or run a marketing campaign.")
    print("="*80)
    print(puzzles[['menu_item_name', 'section_name', 'estimated_profit_per_item', 'total_sold']].head(30).to_string(index=False))

    print("\n Analysis Complete!")

except Exception as e:
    print(f" Error: {e}")
    print("Check your DB password.")