"""
FlavorCraft Menu Optimization System
Main Entry Point

This script provides a simple command-line interface to run the complete
menu optimization pipeline.

Usage:
    python main.py step1              # Run Step 1 analysis
    python main.py step2 "Small Latte" "Coffee & Espresso" 38 413  # Optimize an item
    python main.py demo               # Run Streamlit demo

Author: FlavorCraft Analysis Team
Date: February 5, 2026
"""

"""
SYSTEM OVERVIEW
===============

This is the main entry point for the FlavorCraft Menu Optimization System.
It provides a command-line interface to run the three-step optimization pipeline:

Step 1: Statistical Analysis
    - Analyzes 10,945 active menu items
    - Identifies high-impact description features (+122% for dietary labels)
    - Generates comparable item groups
    - Outputs: data/step1_*.{csv,json}
    
Step 2: Intelligent Optimization
    - Takes single menu item as input
    - Finds comparable high-performers
    - Generates validated recommendations
    - Estimates expected sales lift
    
Step 3: Interactive Demo
    - Launches Streamlit web interface
    - Real-time optimization with visual feedback
    - Pre-loaded examples for testing

DEPENDENCIES
============
- src.step1_category_analysis
- src.step2_optimization_agent
- streamlit (for demo mode)

USAGE EXAMPLES
==============
# Run full analysis
python main.py step1

# Optimize specific item
python main.py step2 "Small Latte" "Coffee & Espresso" 38 413

# Launch web demo
python main.py demo

ERROR HANDLING
==============
- Missing Step 1 outputs: Run step1 first
- Invalid arguments: Usage message displayed
- Streamlit not installed: Installation instructions shown
"""

import sys
import os

def run_step1():
    """Run Step 1: Statistical analysis"""
    print("🚀 Running Step 1: Category-Specific Comparative Analysis\n")
    
    # Import and run Step 1
    from src.step1_category_analysis import main as step1_main
    step1_main()

def run_step2(title: str, category: str, price: float, purchases: int):
    """Run Step 2: Optimize a single menu item"""
    print(f"🚀 Running Step 2: Optimizing '{title}'\n")
    
    # Import the agent
    from src.step2_optimization_agent import MenuOptimizationAgent
    
    # Initialize agent
    agent = MenuOptimizationAgent(
        data_path='data/step1_processed_data.csv',
        insights_path='data/step1_insights.json',
        results_path='data/step1_category_results.json',
        use_ollama=True
    )
    
    # Optimize
    result = agent.optimize(title, category, price, purchases)
    
    # Print results
    print(f"\n{'=' * 80}")
    print(f"OPTIMIZATION RESULTS: {title}")
    print('=' * 80)
    
    print(f"\n📊 Current Performance:")
    print(f"  • Purchases: {result['input']['current_purchases']}")
    print(f"  • Percentile: {result['analysis']['performance_percentile']}th in category")
    print(f"  • Word count: {result['analysis']['word_count']}")
    
    if result['analysis']['issues']:
        print(f"\n⚠️  Issues Detected:")
        for issue in result['analysis']['issues']:
            print(f"  • {issue}")
    
    if result['comparables']:
        print(f"\n🏆 Top Comparable Performers:")
        for comp in result['comparables'][:3]:
            print(f"  • {comp['title']:40s} ({comp['purchases']} purchases)")
    
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"\n  {i}. \"{rec['title']}\"")
            print(f"     Expected lift: +{rec['expected_lift']:.0f}%")
            print(f"     Confidence: {rec['confidence']*100:.0f}%")
            print(f"     Reason: {rec['reason']}")
    
    print(f"\n📝 Summary: {result['summary']}")
    print()

def run_demo():
    """Run Step 3: Interactive Streamlit demo"""
    print("🚀 Starting Interactive Demo (Streamlit)\n")
    
    import subprocess
    try:
        subprocess.run(['streamlit', 'run', 'src/step3_interactive_demo.py'])
    except FileNotFoundError:
        print("❌ Error: Streamlit not installed")
        print("   Install with: pip install streamlit")
        print("   Then run: streamlit run src/step3_interactive_demo.py")

def print_usage():
    """Print usage information"""
    print("""
🍽️  FlavorCraft Menu Optimization System
==========================================

Usage:
    python main.py step1
        Run Step 1: Analyze all menu items and generate insights
        
    python main.py step2 <title> <category> <price> <purchases>
        Run Step 2: Optimize a specific menu item
        Example: python main.py step2 "Small Latte" "Coffee & Espresso" 38 413
        
    python main.py demo
        Run Step 3: Launch interactive Streamlit demo
        
Categories:
    - Coffee & Espresso
    - Tea & Hot Drinks
    - Cold Beverages
    - Juice & Smoothies
    - Breakfast
    - Sandwiches
    - Salads
    - Pizza
    - Desserts & Sweets
    - Other

Examples:
    # Analyze the full menu
    python main.py step1
    
    # Optimize a specific item
    python main.py step2 "Small Latte" "Coffee & Espresso" 38.0 413
    python main.py step2 "Tofu sandwich 🌱" "Sandwiches" 95.0 593
    
    # Launch the interactive demo
    python main.py demo
    """)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'step1':
        run_step1()
    
    elif command == 'step2':
        if len(sys.argv) != 6:
            print("❌ Error: step2 requires 4 arguments")
            print("Usage: python main.py step2 <title> <category> <price> <purchases>")
            print('Example: python main.py step2 "Small Latte" "Coffee & Espresso" 38 413')
            return
        
        title = sys.argv[2]
        category = sys.argv[3]
        try:
            price = float(sys.argv[4])
            purchases = int(sys.argv[5])
        except ValueError:
            print("❌ Error: price must be a number, purchases must be an integer")
            return
        
        run_step2(title, category, price, purchases)
    
    elif command == 'demo':
        run_demo()
    
    elif command in ['help', '-h', '--help']:
        print_usage()
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main()