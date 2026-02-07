"""
Module: optimization_tab
Description: Frontend UI component for the Menu Engineering AI features.
             Designed to be imported and rendered within the main application.
Author: Team Flavor Flow
"""

import streamlit as st
import warnings
from src.services.menu_optimizer import MenuOptimizer

# Suppress FutureWarning from google.generativeai regarding package updates
warnings.filterwarnings("ignore", category=FutureWarning)


def render_optimization_tab():
    """
    Renders the Streamlit interface for the AI Menu Doctor.
    Instantiates the MenuOptimizer service and handles user interaction states.
    """
    st.header("🤖 The Menu Doctor")
    st.markdown(
        "Use Generative AI to re-engineer underperforming items (Dogs & Puzzles).")

    # Initialize the service using cache_resource to avoid reloading the model on every interaction
    @st.cache_resource
    def get_optimizer():
        return MenuOptimizer()

    optimizer = get_optimizer()

    # Section 1: Business Context
    st.subheader("1. Select Context")
    restaurant_name = st.selectbox(
        "Select Restaurant Profile",
        ["Joe's Pizza", "The Golden Dragon", "Le Petit Bistro", "Burger King"],
        help("The AI adapts its tone based on the selected brand identity.")
    )

    col1, col2 = st.columns(2)

    with col1:
        # Section 2: Data Input
        st.subheader("2. Item Diagnosis")
        item_name = st.text_input(
            "Menu Item Name", placeholder="e.g., House Special")
        current_desc = st.text_area(
            "Current Description", placeholder="e.g., Grilled chicken with sauce.", height=100)

    with col2:
        # Section 3: Action & Output
        st.subheader("3. AI Treatment")
        st.info("Generate new marketing copy and renaming strategies.")

        if st.button("✨ Re-Engineer Item", use_container_width=True):
            if not item_name:
                st.warning("Please enter a valid item name.")
            else:
                result = optimizer.improve_item(
                    restaurant_name, item_name, current_desc)
                st.success("Analysis Complete")
                st.markdown("### 📋 Recommendations:")
                st.markdown(result)
