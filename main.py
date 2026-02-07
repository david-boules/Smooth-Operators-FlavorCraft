"""
File: main.py
Description: The Unified Streamlit Dashboard.
             Replaces the old CLI tool with a proper Web Interface.
"""

import streamlit as st
import sys
import os
import importlib.util

# --- 1. PATH SETUP ---
# Forces Python to see the 'src' folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="FlavorCraft Menu System",
    page_icon=".",
    layout="wide"
)

# --- 3. HERO STORES CONFIGURATION (NEW) ---
# Hardcoded list of specific stores for the demo
HERO_STORES = {
    '94025':  ' The Bustling Cafe (High Volume)',
    '323013': ' Sushi Bar (Specialty)',
    '172950': ' Asian Bistro (Dinner)',
    '254209': ' Wine & Dine (High Margin)',
    '324728': ' Sandwich Shop (Lunch Spot)',
    '59897':  ' Italian Pizzeria (Family)',
    'All':    ' Global Company View'
}

# --- 4. HELPER TO LOAD PARTNER A's CODE ---
def load_partner_demo():
    """
    Imports and runs the Sales Tab logic cleanly.
    """
    try:
        # Import the function we just created in Step 1
        from src.step3_interactive_demo import render_sales_tab
        render_sales_tab()
    except ImportError as e:
        st.error(f" Import Error: Could not load src/step3_interactive_demo.py\nDetails: {e}")
    except Exception as e:
        st.error(f" Runtime Error in Sales Tab: {e}")

# --- 5. MAIN APP ---
def main():
    # --- SIDEBAR SELECTOR (NEW) ---
    with st.sidebar:
        st.title("FlavorCraft")
        st.markdown("---")
        st.header("📍 Select Location")
        
        # The Dropdown
        selected_name = st.selectbox(
            "Choose a Store for Analysis:",
            options=list(HERO_STORES.values()),
            index=0 # Default to the first one
        )
        
        # Reverse lookup to find the ID from the name
        selected_id = [k for k, v in HERO_STORES.items() if v == selected_name][0]
        
        # Save to Session State (So tabs can see it)
        st.session_state['selected_store_id'] = selected_id
        st.session_state['selected_store_name'] = selected_name
        
        st.markdown("---")
        st.info(f"**Active ID:** `{selected_id}`")

    # --- MAIN PAGE HEADER ---
    st.title(f"🚀 {selected_name}")
    st.markdown("### Integrated Menu Engineering Platform")

    # Create Two Tabs
    tab_sales, tab_ai = st.tabs(
        [" Existing Analysis (Step 3)", " AI Menu Doctor (New)"])

    # --- TAB 1: Partner A's Original Demo ---
    with tab_sales:
        load_partner_demo()

    # --- TAB 2: Your AI Module ---
    with tab_ai:
        try:
            # We pass the selected ID to the AI tab function if it accepts arguments,
            # otherwise it can read from st.session_state inside.
            from src.frontend.tabs.optimization_tab import render_optimization_tab
            render_optimization_tab() 
        except ImportError as e:
            st.error(f" Setup Error: {e}")
            st.code("Ensure src/frontend/tabs/optimization_tab.py exists!")

if __name__ == "__main__":
    main()