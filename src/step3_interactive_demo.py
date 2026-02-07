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

# 1. Update the Cache Function to include Categories
@st.cache_data(show_spinner="Crunching numbers...", ttl=600)
def get_cached_data(selected_id):
    analyzer = MenuAnalyzer(DB_CONN)
    
    # Fetch Matrix Data
    if selected_id == 'All':
        stars = analyzer.get_stars()
        dogs = analyzer.get_dogs()
        plow = analyzer.get_plowhorses()
        puzzles = analyzer.get_puzzles()
        # Fetch Category Data (NEW)
        cats = analyzer.get_category_breakdown()
    else:
        stars = analyzer.get_stars(store_filter=selected_id)
        dogs = analyzer.get_dogs(store_filter=selected_id)
        plow = analyzer.get_plowhorses(store_filter=selected_id)
        puzzles = analyzer.get_puzzles(store_filter=selected_id)
        # Fetch Category Data (NEW)
        cats = analyzer.get_category_breakdown(store_filter=selected_id)
        
    return stars, dogs, plow, puzzles, cats

def render_sales_tab():
    # 1. CONTEXT
    selected_id = st.session_state.get('selected_store_id', 'All')
    selected_name = st.session_state.get('selected_store_name', 'Global View')

    st.header(f"📊 Sales Performance: {selected_name}")

    # 2. LOAD DATA
    try:
        df_stars, df_dogs, df_plow, df_puzzles, df_cats = get_cached_data(selected_id)
    except Exception as e:
        st.error(f"Data Error: {e}")
        return

    # --- NEW: STEP 1 (CATEGORY ANALYSIS) ---
    st.subheader("1. Category Health (The Macro View)")
    
    col_chart, col_metrics = st.columns([2, 1])
    
    with col_chart:
        # Beautiful Bar Chart of Revenue
        st.caption("Revenue by Category")
        st.bar_chart(
            df_cats.set_index("category")["total_revenue"], 
            color="#FF4B4B" # Deloitte-ish Red/Pink
        )

    with col_metrics:
        # High-level KPIs
        total_rev = df_cats['total_revenue'].sum()
        top_cat = df_cats.iloc[0]['category']
        top_cat_rev = df_cats.iloc[0]['total_revenue']
        
        st.metric("Total Revenue", f"${total_rev:,.0f}")
        st.metric("Top Category", top_cat)
        st.metric(f"{top_cat} Revenue", f"${top_cat_rev:,.0f}", 
                 delta=f"{top_cat_rev/total_rev:.1%} of Total")

    st.divider()

    # --- EXISTING: STEP 2 (ITEM MATRIX) ---
    st.subheader("2. Profit & Popularity Matrix (The Micro View)")
    
    # ... (Keep your existing Matrix columns code here: col1, col2 etc.) ...
    col1, col2 = st.columns(2)
    # [Paste your existing Star/Dog/Plowhorse code here]
    with col1:
        st.subheader("🌟 Stars (High Profit, High Popularity)")
        if not df_stars.empty:
            st.dataframe(df_stars[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Stars found.")
        
        st.subheader("🐴 Plowhorses (Low Profit, High Popularity)")
        if not df_plow.empty:
            st.dataframe(df_plow[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Plowhorses found.")

    with col2:
        st.subheader("🧩 Puzzles (High Profit, Low Popularity)")
        if not df_puzzles.empty:
            st.dataframe(df_puzzles[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Puzzles found.")

        st.subheader("🐕 Dogs (Low Profit, Low Popularity)")
        if not df_dogs.empty:
            st.dataframe(df_dogs[['menu_item_name', 'section_name', 'total_sold', 'estimated_profit_per_item']], hide_index=True)
        else:
            st.info("No Dogs found.")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    if 'selected_store_id' not in st.session_state:
        st.session_state['selected_store_id'] = 'All'
    render_sales_tab()