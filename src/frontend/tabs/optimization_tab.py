"""
Module: optimization_tab
Description: Frontend UI component for the Menu Engineering AI features.
             Optimized for speed (Caching) and actionable AI outputs.
Author: Team Flavor Flow
"""

import streamlit as st
import pandas as pd
import os
import warnings
import google.generativeai as genai
from src.services.menu_analytics import MenuAnalyzer

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# CONFIGURATION
# ==========================================
DB_CONN = "postgresql://postgres:admin@localhost:5432/flavor_flow"

# Configure Gemini
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"AI Config Error: {e}")

# ==========================================
# CACHED DATA FETCHING (SPEED FIX)
# ==========================================
@st.cache_data(show_spinner="Fetching menu diagnostics...", ttl=600)
def fetch_problem_items(store_id):
    """
    Fetches Dogs, Puzzles, and Plowhorses in one go and caches them.
    This makes the UI instant after the first load.
    """
    analyzer = MenuAnalyzer(DB_CONN)
    
    # Handle 'All' vs Specific ID
    filter_id = None if store_id == 'All' else store_id
    
    # Fetch all 3 categories of "Problem Items"
    dogs = analyzer.get_dogs(store_filter=filter_id).head(15)
    puzzles = analyzer.get_puzzles(store_filter=filter_id).head(15)
    plowhorses = analyzer.get_plowhorses(store_filter=filter_id).head(15)
    
    return dogs, puzzles, plowhorses

# ==========================================
# MAIN UI RENDERER
# ==========================================
def render_optimization_tab():
    # 1. GET CONTEXT
    selected_id = st.session_state.get('selected_store_id', 'All')
    selected_name = st.session_state.get('selected_store_name', 'Global View')

    st.header(f"🤖 AI Menu Doctor: {selected_name}")

    # 2. FETCH DATA (INSTANTLY via Cache)
    try:
        df_dogs, df_puzzles, df_plow = fetch_problem_items(selected_id)
    except Exception as e:
        st.error(f"Database Error: {e}")
        return

    # Layout: Control Panel (Left) vs. AI Result (Right)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. Triage Category")
        
        # CATEGORY SELECTOR
        category = st.selectbox(
            "Which problem are we fixing?",
            ["🐕 Dogs (Low Profit, Low Sales)", 
             "🧩 Puzzles (High Profit, Low Sales)", 
             "🐴 Plowhorses (Low Profit, High Sales)"]
        )
        
        # Switch DataFrame based on selection
        if "Dogs" in category:
            active_df = df_dogs
            prompt_context = "This item is dead weight. We need to cut costs or kill it."
        elif "Puzzles" in category:
            active_df = df_puzzles
            prompt_context = "This item makes money but nobody buys it. We need Marketing/Rebranding."
        else: # Plowhorses
            active_df = df_plow
            prompt_context = "This sells huge volume but loses margin. We need Cost Reduction or Price Hike."

        st.divider()
        st.subheader("2. Select Patient")

        if active_df.empty:
            st.success(f"✅ No items found in this category!")
            return

        # ITEM SELECTOR (Crash-Proof Index Method)
        options = active_df.apply(
            lambda x: f"{x['menu_item_name']} (Profit: ${x['estimated_profit_per_item']:.2f})", 
            axis=1
        ).tolist()
        
        selected_option = st.radio("Select Item:", options, label_visibility="collapsed")
        
        # Get Data Row safely
        try:
            selected_index = options.index(selected_option)
            item_data = active_df.iloc[selected_index]
            item_name = item_data['menu_item_name']
        except:
            st.error("Selection error.")
            return

    with col2:
        st.subheader(f"3. Prescription: **{item_name}**")
        
        # METRICS
        price = item_data['avg_price']
        profit = item_data['estimated_profit_per_item']
        est_cost = price - profit
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Price", f"${price:.2f}")
        m2.metric("Est. Cost", f"${est_cost:.2f}")
        m3.metric("Profit", f"${profit:.2f}", delta_color="inverse")

        st.divider()

        # AI ACTION BUTTON
        if st.button("✨ Generate Action Plan", type="primary", use_container_width=True):
            if not os.getenv("GEMINI_API_KEY"):
                st.error("❌ GEMINI_API_KEY missing.")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        # --- STRICT "NO FLUFF" PROMPT ---
                        prompt = f"""
                        Role: Ruthless Menu Engineer.
                        Task: Fix "{item_name}" for a restaurant ({selected_name}).
                        Context: {prompt_context}
                        Data: Price=${price:.2f}, Est. Cost=${est_cost:.2f}.

                        OUTPUT STRICTLY IN THIS FORMAT (No intro text):
                        
                        **1. INGREDIENTS (Inferred):**
                        [Comma-separated list]

                        **2. THE FIX (Actionable):**
                        * [Specific action to fix the problem defined in Context]
                        * [Secondary action]

                        **3. REBRAND (Marketing):**
                        * **Name:** [New Catchy Name]
                        * **Copy:** [1-sentence description]

                        **4. PRICE CHANGE:**
                        * [Keep / Increase / Decrease] to [New Price]. [Brief Why].
                        """
                        
                        model = genai.GenerativeModel('gemini-flash-latest')
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"AI Error: {e}")