"""
STEP 3: Interactive Menu Optimization Demo
============================================

Streamlit interface for the Menu Optimization Agent.

Run with: streamlit run step3_interactive_demo.py

Author: FlavorCraft Analysis Team
Date: February 5, 2026
"""

"""
INTERACTIVE WEB INTERFACE
==========================

This module provides a Streamlit-based web interface for real-time menu optimization.

FEATURES
--------
1. Live Optimization
   - Type any menu item details
   - Instant analysis and recommendations
   - Visual performance metrics
   
2. Quick Examples
   - Pre-loaded test cases (Small Latte, Tofu sandwich, etc.)
   - One-click form population
   - Demonstrates key insights
   
3. Visual Feedback
   - Performance percentile display
   - Issues highlighted in red
   - Strengths shown in green
   - Comparable performers table
   - Expandable recommendation cards

USER FLOW
---------
1. User enters menu item details (or clicks example button)
2. User clicks "Optimize Menu Item"
3. System analyzes item with loading spinner
4. Results displayed:
   - Current performance (purchases, percentile, word count)
   - Issues detected (with explanations)
   - Top comparable performers (table format)
   - Ranked recommendations (with reasoning)
   - Summary statement

LAYOUT
------
Sidebar:
  - System statistics
  - Key findings summary
  - Quick example buttons
  
Main Area:
  Left Column (Input):
    - Title text input
    - Category dropdown
    - Price number input
    - Purchases number input
    - Optimize button
    
  Right Column (Results):
    - Performance metrics (3 columns)
    - Issues/Strengths (expandable)
    - Comparables table
    - Recommendation cards (expandable)
    - Summary info box

CACHING
-------
@st.cache_resource on load_agent()
  - Prevents reloading agent on every interaction
  - Shared across all users/sessions
  - Invalidated only on code change

SESSION STATE
-------------
- example_title: Stores clicked example title
- example_category: Stores clicked example category
- example_price: Stores clicked example price
- example_purchases: Stores clicked example purchases

CONFIGURATION
-------------
Page Config:
  - Title: "Menu Optimization Agent"
  - Icon: Fork and knife emoji
  - Layout: Wide mode
  
Agent Config:
  - use_ollama: True/False (LLM vs fallback)
  - Loads from: data/step1_*.{csv,json}

RUNNING
-------
Command: streamlit run src/step3_interactive_demo.py
Port: http://localhost:8501
Requirements: streamlit >= 1.28.0

PERFORMANCE
-----------
- Initial load: ~2 seconds
- Per-optimization: <1 second (cached agent)
- Memory: ~100MB (includes Streamlit overhead)
"""

import streamlit as st
import sys
import json

# Import the agent
# Import from src directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.step2_optimization_agent import MenuOptimizationAgent

# Page config
st.set_page_config(
    page_title="Menu Optimization Agent",
    page_icon="🍽️",
    layout="wide"
)

# Initialize agent (cached)
@st.cache_resource
def load_agent():
    """Load the optimization agent (cached for performance)"""
    return MenuOptimizationAgent(
        data_path='data/step1_processed_data.csv',
        insights_path='data/step1_insights.json',
        results_path='data/step1_category_results.json',
        use_ollama=True  # Set to True if Ollama is installed
    )

# Main app
def main():
    # Header
    st.title("🍽️ Menu Optimization Agent")
    st.markdown("### AI-Powered Menu Description Optimizer")
    st.markdown("Trained on 10,945 FlavorCraft menu items | Powered by statistical analysis + LLM")
    
    st.markdown("---")
    
    # Sidebar with info
    with st.sidebar:
        st.header("📊 System Info")
        st.markdown("""
        **Training Data:**
        - 10,945 active menu items
        - 42.6M DKK total revenue
        - 10 categories analyzed
        
        **Key Findings:**
        - Dietary labels: +122% lift
        - Flavor descriptors: +60% lift
        - Combo descriptions: -49% impact
        - Optimal length: 3-6 words
        """)
        
        st.markdown("---")
        st.header("🎯 Quick Examples")
        
        if st.button("Small Latte"):
            st.session_state['example_title'] = "Small Latte"
            st.session_state['example_category'] = "Coffee & Espresso"
            st.session_state['example_price'] = 38.0
            st.session_state['example_purchases'] = 413
        
        if st.button("Tofu sandwich 🌱"):
            st.session_state['example_title'] = "Tofu sandwich 🌱"
            st.session_state['example_category'] = "Sandwiches"
            st.session_state['example_price'] = 95.0
            st.session_state['example_purchases'] = 593
        
        if st.button("Bread, butter and cheese"):
            st.session_state['example_title'] = "Bread, butter and cheese"
            st.session_state['example_category'] = "Breakfast"
            st.session_state['example_price'] = 35.0
            st.session_state['example_purchases'] = 842
    
    # Main input area
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("📝 Input Menu Item")
        
        # Get values from session state if example was clicked
        default_title = st.session_state.get('example_title', '')
        default_category = st.session_state.get('example_category', 'Other')
        default_price = st.session_state.get('example_price', 50.0)
        default_purchases = st.session_state.get('example_purchases', 100)
        
        title = st.text_input(
            "Current Title",
            value=default_title,
            placeholder="e.g., Small Latte"
        )
        
        category = st.selectbox(
            "Category",
            [
                "Coffee & Espresso",
                "Tea & Hot Drinks",
                "Cold Beverages",
                "Juice & Smoothies",
                "Breakfast",
                "Sandwiches",
                "Salads",
                "Pizza",
                "Desserts & Sweets",
                "Other"
            ],
            index=["Coffee & Espresso", "Tea & Hot Drinks", "Cold Beverages", "Juice & Smoothies",
                   "Breakfast", "Sandwiches", "Salads", "Pizza", "Desserts & Sweets", "Other"].index(default_category)
        )
        
        col1a, col1b = st.columns(2)
        
        with col1a:
            price = st.number_input(
                "Price (DKK)",
                min_value=0.0,
                value=float(default_price),
                step=5.0
            )
        
        with col1b:
            purchases = st.number_input(
                "Current Purchases",
                min_value=0,
                value=int(default_purchases),
                step=10
            )
        
        optimize_button = st.button(
            "🚀 Optimize Menu Item",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.subheader("💡 Optimization Results")
        
        if optimize_button and title:
            # Load agent
            with st.spinner("Analyzing menu item..."):
                agent = load_agent()
                result = agent.optimize(title, category, price, purchases)
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            # Performance overview
            st.markdown("#### 📊 Current Performance")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Purchases", f"{result['input']['current_purchases']:,}")
            
            with metric_col2:
                percentile = result['analysis']['performance_percentile']
                st.metric("Percentile", f"{percentile}th", 
                         delta=f"{100-percentile}% to top" if percentile < 90 else "Top performer!")
            
            with metric_col3:
                wc = result['analysis']['word_count']
                optimal = "✓" if 3 <= wc <= 6 else "⚠️"
                st.metric("Word Count", f"{wc} {optimal}")
            
            # Issues and strengths
            if result['analysis']['issues'] or result['analysis']['strengths']:
                st.markdown("#### 🔍 Analysis")
                
                if result['analysis']['issues']:
                    with st.expander("⚠️ Issues Detected", expanded=True):
                        for issue in result['analysis']['issues']:
                            st.markdown(f"- {issue}")
                
                if result['analysis']['strengths']:
                    with st.expander("✅ Strengths"):
                        for strength in result['analysis']['strengths']:
                            st.markdown(f"- {strength}")
            
            # Comparables
            if result['comparables']:
                st.markdown("#### 🏆 Top Comparable Performers")
                comp_data = []
                for comp in result['comparables'][:3]:
                    comp_data.append({
                        'Title': comp['title'],
                        'Purchases': f"{comp['purchases']:,}",
                        'Price': f"{comp['price']:.0f} DKK"
                    })
                st.table(comp_data)
            
            # Recommendations
            st.markdown("#### 💡 Recommendations")
            
            if result['recommendations']:
                for i, rec in enumerate(result['recommendations'], 1):
                    with st.expander(f"🎯 Option {i}: \"{rec['title']}\"", expanded=(i==1)):
                        rec_col1, rec_col2 = st.columns([1, 2])
                        
                        with rec_col1:
                            st.metric("Expected Lift", f"+{rec['expected_lift']:.0f}%")
                            st.metric("Confidence", f"{rec['confidence']*100:.0f}%")
                        
                        with rec_col2:
                            st.markdown(f"**Reasoning:** {rec['reason']}")
                            st.markdown(f"**Inspired by:** {rec['inspired_by']}")
                
                # Summary
                st.info(f"📝 **Summary:** {result['summary']}")
            else:
                st.warning("No strong recommendations at this time. Item may already be well-optimized.")
        
        elif not title:
            st.info("👈 Enter menu item details to get optimization recommendations")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>FlavorCraft Menu Engineering System</strong></p>
        <p>Trained on 10,945 items | Built with Python, pandas, Streamlit</p>
        <p>Deloitte x AUC Hackathon 2026</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()