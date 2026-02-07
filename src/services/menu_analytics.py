import pandas as pd
import os
from sqlalchemy import create_engine, text  

class MenuAnalyzer:
    def __init__(self, db_connection_string):
        """
        Initialize with a database connection string.
        """
        self.engine = create_engine(db_connection_string)
        
        # Path to the SQL file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sql_path = os.path.join(base_dir, 'sql', 'q1_menu_matrix.sql')

    def calculate_matrix(self):
        """
        Runs the SQL query and applies Quadrant Analysis per section.
        """
        try:
            with open(self.sql_path, 'r') as f:
                query_str = f.read()
        except FileNotFoundError:
            raise Exception(f"SQL file not found at {self.sql_path}")

        with self.engine.connect() as connection:
            df = pd.read_sql(text(query_str), connection)

        if df.empty:
            return df

        results = []
        for section in df['section_name'].unique():
            section_df = df[df['section_name'] == section].copy()
            
            if len(section_df) < 2:
                section_df['Category'] = 'Unclassified'
                results.append(section_df)
                continue

            avg_sold = section_df['total_sold'].mean()
            avg_profit = section_df['estimated_profit_per_item'].mean()

            def classify(row):
                if row['total_sold'] >= avg_sold and row['estimated_profit_per_item'] >= avg_profit:
                    return 'Star'
                elif row['total_sold'] < avg_sold and row['estimated_profit_per_item'] >= avg_profit:
                    return 'Puzzle'
                elif row['total_sold'] >= avg_sold and row['estimated_profit_per_item'] < avg_profit:
                    return 'Plowhorse'
                else:
                    return 'Dog'

            section_df['Category'] = section_df.apply(classify, axis=1)
            results.append(section_df)

        return pd.concat(results) if results else df

    def get_stars(self):
        """High Profit, High Sales (Keep these!)"""
        df = self.calculate_matrix()
        return df[df['Category'] == 'Star'].sort_values('estimated_profit_per_item', ascending=False)

    def get_dogs(self):
        """Low Profit, Low Sales (Consider removing)"""
        df = self.calculate_matrix()
        return df[df['Category'] == 'Dog'].sort_values('total_sold', ascending=True)

    def get_plowhorses(self):
        """Low Profit, High Sales (Price increase opportunity)"""
        df = self.calculate_matrix()
        return df[df['Category'] == 'Plowhorse'].sort_values('total_sold', ascending=False)

    def get_puzzles(self):
        """High Profit, Low Sales (Marketing/Rename opportunity)"""
        df = self.calculate_matrix()
        return df[df['Category'] == 'Puzzle'].sort_values('estimated_profit_per_item', ascending=False)