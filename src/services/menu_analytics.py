import pandas as pd
import os
from sqlalchemy import create_engine, text

class MenuAnalyzer:
    def __init__(self, db_connection_string):
        self.engine = create_engine(db_connection_string)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sql_path = os.path.join(base_dir, 'sql', 'q1_menu_matrix.sql')

    def calculate_matrix(self, store_filter=None):
        try:
            with open(self.sql_path, 'r') as f:
                query_str = f.read()
        except FileNotFoundError:
            raise Exception(f"SQL file not found at {self.sql_path}")

        with self.engine.connect() as connection:
            df = pd.read_sql(text(query_str), connection)

        if df.empty:
            df['Category'] = None
            return df
            
        df['store_name'] = df['store_name'].fillna('Unknown').astype(str)

        # --- FILTERING ---
        if store_filter:
            df = df[df['store_name'] == str(store_filter)].copy()
            if df.empty:
                df['Category'] = None
                return df
        else:
            # Global Aggregation
            df = df.groupby(['section_name', 'menu_item_name']).agg({
                'total_sold': 'sum',
                'estimated_profit_per_item': 'mean', 
                'avg_price': 'mean',
                'store_name': lambda x: 'All Locations'
            }).reset_index()

        # --- SEGMENTATION ---
        results = []
        # We classify per section (Burgers vs Burgers, Drinks vs Drinks)
        for section in df['section_name'].unique():
            section_df = df[df['section_name'] == section].copy()
            
            # FIXED: Even if there is only 1 item, we calculate it against itself
            avg_sold = section_df['total_sold'].mean()
            avg_profit = section_df['estimated_profit_per_item'].mean()

            def classify(row):
                # If values are exactly equal to average (common in small lists), we count them as High (Stars)
                high_sales = row['total_sold'] >= avg_sold
                high_profit = row['estimated_profit_per_item'] >= avg_profit
                
                if high_sales and high_profit: return 'Star'
                elif not high_sales and high_profit: return 'Puzzle'
                elif high_sales and not high_profit: return 'Plowhorse'
                else: return 'Dog'

            section_df['Category'] = section_df.apply(classify, axis=1)
            results.append(section_df)

        return pd.concat(results) if results else df

    # --- KEEP THESE HELPERS ---
    def get_stars(self, store_filter=None):
        df = self.calculate_matrix(store_filter)
        if df is None or df.empty: return pd.DataFrame()
        return df[df['Category'] == 'Star'].sort_values('estimated_profit_per_item', ascending=False)

    def get_dogs(self, store_filter=None):
        df = self.calculate_matrix(store_filter)
        if df is None or df.empty: return pd.DataFrame()
        return df[df['Category'] == 'Dog'].sort_values('total_sold', ascending=True)

    def get_plowhorses(self, store_filter=None):
        df = self.calculate_matrix(store_filter)
        if df is None or df.empty: return pd.DataFrame()
        return df[df['Category'] == 'Plowhorse'].sort_values('total_sold', ascending=False)

    def get_puzzles(self, store_filter=None):
        df = self.calculate_matrix(store_filter)
        if df is None or df.empty: return pd.DataFrame()
        return df[df['Category'] == 'Puzzle'].sort_values('estimated_profit_per_item', ascending=False)
    
    def get_store_ids(self):
        query = "SELECT DISTINCT place_id FROM fct_payments WHERE place_id IS NOT NULL ORDER BY place_id;"
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return [str(row[0]) for row in result]