import streamlit as st
import pandas as pd
from src.services.menu_analytics import MenuAnalyzer

# Database Connection
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

# --- THE MAGIC FIX: CACHING ---
@st.cache_data(show_spinner="Fetching millions of records...")
def get_cached_matrix(selected_id):
    """
    Fetches ALL matrix data for a specific store and saves it to RAM.
    This prevents reloading the database every time you interact with the page.
    """
    analyzer = MenuAnalyzer(DB_CONN)
    
    if selected_id == 'All':
        stars = analyzer.get_stars()
        dogs = analyzer.get_dogs()
        plow = analyzer.get_plowhorses()
        puzzles = analyzer.get_puzzles()
    else:
        stars = analyzer.get_stars(store_filter=selected_id)
        dogs = analyzer.get_dogs(store_filter=selected_id)
        plow = analyzer.get_plowhorses(store_filter=selected_id)
        puzzles = analyzer.get_puzzles(store_filter=selected_id)
        
    return stars, dogs, plow, puzzles

def render_sales_tab():
    # 1. RETRIEVE CONTEXT
    selected_id = st.session_state.get('selected_store_id', 'All')
    selected_name = st.session_state.get('selected_store_name', 'Global View')

    st.header(f"📊 Profit & Popularity Matrix: {selected_name}")
    
    # 2. LOAD DATA (USING CACHE)
    try:
        # We call the cached function instead of the analyzer directly
        df_stars, df_dogs, df_plow, df_puzzles = get_cached_matrix(selected_id)

    except Exception as e:
        st.error(f"Database Error: {e}")
        return

    # 3. DISPLAY MATRIX
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(" Stars (High Profit, High Popularity)")
        st.caption("Keep these! Promote them.")
        if not df_stars.empty:
            st.dataframe(df_stars[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Stars found.")

        st.subheader(" Plowhorses (Low Profit, High Popularity)")
        st.caption("Increase prices or lower cost.")
        if not df_plow.empty:
            st.dataframe(df_plow[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Plowhorses found.")

    with col2:
        st.subheader(" Puzzles (High Profit, Low Popularity)")
        st.caption("Market these better!")
        if not df_puzzles.empty:
            st.dataframe(df_puzzles[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Puzzles found.")

        st.subheader(" Dogs (Low Profit, Low Popularity)")
        st.caption("Remove these from the menu.")
        if not df_dogs.empty:
            st.dataframe(df_dogs[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Dogs found.")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    if 'selected_store_id' not in st.session_state:
        st.session_state['selected_store_id'] = 'All'
    render_sales_tab()