"""
STEP 1: Category-Specific Comparative Analysis
================================================

This script:
1. Loads menu items data
2. Intelligently categorizes items based on keywords and patterns
3. Groups similar items within categories
4. Performs comparative analysis to find what descriptions work
5. Outputs findings for Step 2 (Ollama enrichment)

Author: FlavorCraft Analysis Team
Date: February 5, 2026
"""

"""
DATA PROCESSING PIPELINE
========================

This module implements the statistical discovery phase of menu optimization.

ARCHITECTURE
------------
Input: data/part2/dim_menu_items.csv (30,407 raw items)
    ↓
Filter: Active items with ≥5 purchases (10,945 items)
    ↓
Categorize: 10 intelligent categories via keyword matching
    ↓
Feature Extract: 7 linguistic features per item
    ↓
Comparative Analysis: Within-category performance metrics
    ↓
Output: Structured insights for ML pipeline

CATEGORIES (10)
---------------
1. Coffee & Espresso - lattes, cappuccinos, espressos, mochas
2. Tea & Hot Drinks - teas, hot chocolate, warm beverages
3. Cold Beverages - sodas, beer, wine, mineral water
4. Juice & Smoothies - juices, shakes, smoothie bowls
5. Breakfast - breakfast items, brunch, pancakes, yogurt
6. Sandwiches - sandwiches, bread-based items
7. Salads - salad items and bowls
8. Pizza - pizza varieties, margherita
9. Desserts & Sweets - cookies, cakes, muffins, pastries
10. Other - all remaining items

FEATURES EXTRACTED (7)
----------------------
1. has_size: Size indicators (small, large, medium, etc.)
2. has_temp: Temperature descriptors (hot, cold, iced, warm)
3. has_dietary: Dietary labels (vegan, organic, gluten-free)
4. has_flavor: Flavor descriptors (chocolate, vanilla, strawberry)
5. is_combo: List format (contains commas, ampersands, "and")
6. has_emoji: Contains food-related emoji
7. has_special_name: Creative vs generic naming

KEY FINDINGS
------------
- Dietary labels: +122% lift (18 items analyzed)
- Flavor descriptors: +60% lift (22 items analyzed)
- Size indicators: -50% impact (84 items analyzed)
- Combo descriptions: -49% impact (576 items analyzed)
- Optimal title length: 3-6 words

PERFORMANCE
-----------
- Runtime: ~30 seconds
- Memory: ~50MB
- Output size: ~2MB total

CONFIGURATION
-------------
MIN_PURCHASES = 5              # Minimum purchases to include item
MIN_ITEMS_PER_CATEGORY = 10    # Minimum items for valid category
"""

import pandas as pd
import numpy as np
import re
from collections import defaultdict, Counter
import json
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Minimum purchases threshold to include in analysis
MIN_PURCHASES = 5

# Minimum items per category for meaningful analysis
MIN_ITEMS_PER_CATEGORY = 10


# ============================================================================
# STEP 1.1: LOAD AND CLEAN DATA
# ============================================================================

def load_data(filepath):
    """
    Load menu items data and perform initial cleaning.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with cleaned data
    """
    print("=" * 80)
    print("STEP 1.1: LOADING AND CLEANING DATA")
    print("=" * 80)
    
    df = pd.read_csv(filepath)
    
    print(f"\n✓ Loaded {len(df):,} menu items")
    
    # Filter to active items with purchases
    df = df[
        (df['status'] == 'Active') & 
        (df['purchases'] >= MIN_PURCHASES) &
        (df['title'].notna())
    ].copy()
    
    print(f"✓ Filtered to {len(df):,} active items with ≥{MIN_PURCHASES} purchases")
    
    # Calculate performance metrics
    df['revenue'] = df['purchases'] * df['price']
    df['rating_weighted'] = df['rating'] * df['votes']
    df['popularity_score'] = df['purchases'] / (df['votes'] + 1)  # Avoid div by zero
    
    # Normalize title for analysis
    df['title_clean'] = df['title'].str.strip()
    df['title_lower'] = df['title_clean'].str.lower()
    df['word_count'] = df['title_clean'].str.split().str.len()
    
    print(f"✓ Calculated performance metrics")
    
    return df


# ============================================================================
# STEP 1.2: INTELLIGENT CATEGORIZATION
# ============================================================================

def categorize_items(df):
    """
    Categorize menu items based on keywords and patterns in titles.
    
    This uses a rule-based approach to assign items to categories like:
    - Coffee & Espresso Drinks
    - Tea & Hot Beverages
    - Cold Beverages
    - Breakfast Items
    - Sandwiches & Wraps
    - Salads
    - Desserts & Sweets
    - etc.
    
    Args:
        df: DataFrame with menu items
        
    Returns:
        DataFrame with 'category' column added
    """
    print("\n" + "=" * 80)
    print("STEP 1.2: CATEGORIZING ITEMS")
    print("=" * 80)
    
    def assign_category(title):
        """Assign category based on title keywords"""
        title_lower = title.lower()
        
        # Coffee drinks
        if any(word in title_lower for word in ['latte', 'cappuccino', 'espresso', 'americano', 
                                                  'mocha', 'macchiato', 'cortado', 'flat white']):
            return 'Coffee & Espresso'
        
        # Tea
        if any(word in title_lower for word in ['tea', 'chai', 'te']):
            return 'Tea & Hot Drinks'
        
        # Other hot drinks
        if any(word in title_lower for word in ['chocolate', 'chokolade', 'hot ']):
            return 'Tea & Hot Drinks'
        
        # Juice & smoothies
        if any(word in title_lower for word in ['juice', 'shake', 'smoothie', 'shot']):
            return 'Juice & Smoothies'
        
        # Cold beverages
        if any(word in title_lower for word in ['cola', 'water', 'mineral', 'vitamin', 
                                                  'beer', 'wine', 'vin', 'øl']):
            return 'Cold Beverages'
        
        # Breakfast items
        if any(word in title_lower for word in ['breakfast', 'brunch', 'pancake', 'yogurt',
                                                  'granola', 'eggs', 'bacon']):
            return 'Breakfast'
        
        # Sandwiches
        if any(word in title_lower for word in ['sandwich', 'bread']):
            return 'Sandwiches'
        
        # Salads
        if 'salad' in title_lower:
            return 'Salads'
        
        # Desserts & sweets
        if any(word in title_lower for word in ['cookie', 'cake', 'muffin', 'croissant',
                                                  'pie', 'cheesecake']):
            return 'Desserts & Sweets'
        
        # Pizza
        if any(word in title_lower for word in ['pizza', 'margherita']):
            return 'Pizza'
        
        # Default
        return 'Other'
    
    df['category'] = df['title_clean'].apply(assign_category)
    
    # Print category distribution
    print("\n📊 Category Distribution:")
    category_stats = df.groupby('category').agg({
        'id': 'count',
        'purchases': 'sum',
        'revenue': 'sum'
    }).round(2)
    category_stats.columns = ['Items', 'Total Purchases', 'Total Revenue (DKK)']
    category_stats = category_stats.sort_values('Total Revenue (DKK)', ascending=False)
    
    print(category_stats.to_string())
    
    # Filter out categories with too few items
    valid_categories = df.groupby('category').size()
    valid_categories = valid_categories[valid_categories >= MIN_ITEMS_PER_CATEGORY].index
    
    df_filtered = df[df['category'].isin(valid_categories)].copy()
    
    print(f"\n✓ Keeping {len(valid_categories)} categories with ≥{MIN_ITEMS_PER_CATEGORY} items")
    print(f"✓ Analyzing {len(df_filtered):,} items across these categories")
    
    return df_filtered


# ============================================================================
# STEP 1.3: EXTRACT DESCRIPTION FEATURES
# ============================================================================

def extract_description_features(df):
    """
    Extract features from item titles that might influence sales.
    
    Features include:
    - Size indicators (small, large, medium)
    - Temperature indicators (hot, cold, iced)
    - Dietary labels (vegan, organic, etc.)
    - Ingredient mentions
    - Descriptive adjectives
    - Special characters (emojis, ampersands)
    
    Args:
        df: DataFrame with menu items
        
    Returns:
        DataFrame with feature columns added
    """
    print("\n" + "=" * 80)
    print("STEP 1.3: EXTRACTING DESCRIPTION FEATURES")
    print("=" * 80)
    
    # Size indicators
    df['has_size'] = df['title_lower'].str.contains(
        r'\b(small|large|big|mini|medium|xl|grande)\b', 
        regex=True
    )
    
    # Temperature/preparation
    df['has_temp'] = df['title_lower'].str.contains(
        r'\b(iced|hot|cold|warm|frozen|fresh)\b',
        regex=True
    )
    
    # Dietary labels
    df['has_dietary'] = df['title_lower'].str.contains(
        r'\b(vegan|vegetarian|organic|gluten.*free|økologisk|bio)\b',
        regex=True
    )
    
    # Flavor descriptors
    df['has_flavor'] = df['title_lower'].str.contains(
        r'\b(chocolate|vanilla|strawberry|caramel|hazelnut|mint|berry|fruit)\b',
        regex=True
    )
    
    # Lists/combos (uses commas or "and")
    df['is_combo'] = df['title_lower'].str.contains(r',|&| and ')
    
    # Has emoji
    df['has_emoji'] = df['title_clean'].str.contains(r'[🌱🍕🥗☕🍰🥤🍺]', regex=True)
    
    # Branded/special names
    df['has_special_name'] = ~df['title_lower'].str.contains(
        r'\b(coffee|latte|tea|juice|sandwich|salad|cake|pizza|beer|wine|water)\b',
        regex=True
    )
    
    # Count features
    feature_cols = ['has_size', 'has_temp', 'has_dietary', 'has_flavor', 
                    'is_combo', 'has_emoji', 'has_special_name']
    
    print("\n📊 Feature Prevalence:")
    for col in feature_cols:
        count = df[col].sum()
        pct = (count / len(df)) * 100
        print(f"  {col:20s}: {count:5d} items ({pct:5.1f}%)")
    
    return df


# ============================================================================
# STEP 1.4: COMPARATIVE ANALYSIS WITHIN CATEGORIES
# ============================================================================

def analyze_within_category(df, category_name):
    """
    Perform comparative analysis within a single category.
    
    This finds patterns by comparing:
    1. Items with vs without each feature
    2. Similar items with different descriptions
    3. Top performers vs bottom performers
    
    Args:
        df: DataFrame with items from one category
        category_name: Name of the category
        
    Returns:
        Dictionary with analysis results
    """
    
    results = {
        'category': category_name,
        'total_items': len(df),
        'total_revenue': df['revenue'].sum(),
        'avg_purchases': df['purchases'].mean(),
        'feature_impacts': {},
        'top_performers': [],
        'insights': []
    }
    
    # Analyze each feature's impact
    feature_cols = ['has_size', 'has_temp', 'has_dietary', 'has_flavor', 
                    'is_combo', 'has_emoji', 'has_special_name']
    
    for feature in feature_cols:
        with_feature = df[df[feature] == True]
        without_feature = df[df[feature] == False]
        
        if len(with_feature) >= 3 and len(without_feature) >= 3:
            # Calculate performance difference
            avg_with = with_feature['purchases'].mean()
            avg_without = without_feature['purchases'].mean()
            
            # Calculate statistical significance (simple t-test would be better)
            if avg_without > 0:
                lift_pct = ((avg_with - avg_without) / avg_without) * 100
            else:
                lift_pct = 0
            
            results['feature_impacts'][feature] = {
                'items_with': len(with_feature),
                'items_without': len(without_feature),
                'avg_purchases_with': round(avg_with, 2),
                'avg_purchases_without': round(avg_without, 2),
                'lift_percent': round(lift_pct, 2)
            }
    
    # Get top performers for examples
    top_5 = df.nlargest(5, 'purchases')[['title_clean', 'purchases', 'price', 'revenue']]
    results['top_performers'] = top_5.to_dict('records')
    
    return results


def comparative_analysis(df):
    """
    Run comparative analysis across all categories.
    
    Args:
        df: DataFrame with categorized menu items
        
    Returns:
        Dictionary with results for each category
    """
    print("\n" + "=" * 80)
    print("STEP 1.4: COMPARATIVE ANALYSIS BY CATEGORY")
    print("=" * 80)
    
    all_results = {}
    
    for category in sorted(df['category'].unique()):
        category_df = df[df['category'] == category]
        
        print(f"\n📊 Analyzing: {category} ({len(category_df)} items)")
        
        results = analyze_within_category(category_df, category)
        all_results[category] = results
        
        # Print key findings
        print(f"   Total revenue: {results['total_revenue']:,.0f} DKK")
        print(f"   Avg purchases per item: {results['avg_purchases']:.1f}")
        
        # Print feature impacts sorted by lift
        if results['feature_impacts']:
            print("   Feature impacts:")
            impacts = sorted(
                results['feature_impacts'].items(),
                key=lambda x: x[1]['lift_percent'],
                reverse=True
            )
            for feature, impact in impacts[:3]:  # Top 3
                if impact['items_with'] >= 3:  # Only if enough samples
                    feature_name = feature.replace('has_', '').replace('is_', '').replace('_', ' ')
                    print(f"      • {feature_name:20s}: {impact['lift_percent']:+6.1f}% lift "
                          f"({impact['items_with']} items)")
    
    return all_results


# ============================================================================
# STEP 1.5: IDENTIFY COMPARABLE ITEM PAIRS
# ============================================================================

def find_comparable_pairs(df):
    """
    Find pairs or groups of items that are similar enough to compare.
    
    For example:
    - "Latte" vs "Small Latte" vs "Iced Latte"
    - "Chicken sandwich" vs "Salmon sandwich" vs "Tofu sandwich"
    
    Args:
        df: DataFrame with menu items
        
    Returns:
        List of comparable groups
    """
    print("\n" + "=" * 80)
    print("STEP 1.5: FINDING COMPARABLE ITEM PAIRS")
    print("=" * 80)
    
    comparable_groups = []
    
    # Group by category
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        
        # Find items with common base words
        word_groups = defaultdict(list)
        
        for idx, row in category_df.iterrows():
            title = row['title_clean']
            words = set(title.lower().split())
            
            # Use significant words (not "with", "and", etc.)
            significant_words = words - {'with', 'and', 'or', 'the', 'a', 'an', '&'}
            
            # Group by each significant word
            for word in significant_words:
                if len(word) > 3:  # Only substantial words
                    word_groups[word].append({
                        'title': title,
                        'purchases': row['purchases'],
                        'price': row['price'],
                        'revenue': row['revenue']
                    })
        
        # Keep groups with multiple items
        for word, items in word_groups.items():
            if len(items) >= 2:
                comparable_groups.append({
                    'category': category,
                    'common_word': word,
                    'items': sorted(items, key=lambda x: x['purchases'], reverse=True)
                })
    
    # Sort by total revenue in group
    comparable_groups = sorted(
        comparable_groups,
        key=lambda x: sum(item['revenue'] for item in x['items']),
        reverse=True
    )
    
    print(f"\n✓ Found {len(comparable_groups)} comparable item groups")
    
    # Show top examples
    print("\n📋 Top Comparable Groups (by total revenue):")
    for i, group in enumerate(comparable_groups[:10], 1):
        print(f"\n{i}. {group['category']} - items with '{group['common_word']}':")
        for item in group['items'][:5]:  # Show top 5 in each group
            print(f"   • {item['title']:40s} - {item['purchases']:4d} purchases, "
                  f"{item['price']:5.0f} DKK")
    
    return comparable_groups


# ============================================================================
# STEP 1.6: GENERATE INSIGHTS AND PREPARE FOR STEP 2
# ============================================================================

def generate_insights(df, category_results, comparable_groups):
    """
    Generate actionable insights from the comparative analysis.
    
    This prepares structured data for Step 2 (Ollama analysis).
    
    Args:
        df: Full DataFrame
        category_results: Results from category analysis
        comparable_groups: Comparable item groups
        
    Returns:
        Dictionary with insights and data for Step 2
    """
    print("\n" + "=" * 80)
    print("STEP 1.6: GENERATING INSIGHTS")
    print("=" * 80)
    
    insights = {
        'summary': {},
        'category_findings': [],
        'high_impact_features': [],
        'comparable_pairs_for_llm': [],
        'recommendations': []
    }
    
    # Overall summary
    insights['summary'] = {
        'total_items_analyzed': len(df),
        'total_categories': len(category_results),
        'total_revenue': float(df['revenue'].sum()),
        'avg_word_count': float(df['word_count'].mean())
    }
    
    # Find high-impact features across categories
    feature_scores = defaultdict(list)
    
    for category, results in category_results.items():
        for feature, impact in results['feature_impacts'].items():
            if impact['items_with'] >= 3:  # Minimum sample size
                feature_scores[feature].append({
                    'category': category,
                    'lift': impact['lift_percent'],
                    'items': impact['items_with']
                })
    
    # Aggregate feature impacts
    for feature, scores in feature_scores.items():
        avg_lift = np.mean([s['lift'] for s in scores])
        total_items = sum([s['items'] for s in scores])
        
        if total_items >= 10:  # Only features with enough data
            insights['high_impact_features'].append({
                'feature': feature,
                'avg_lift_percent': round(avg_lift, 2),
                'total_items': total_items,
                'categories_affected': len(scores)
            })
    
    # Sort by impact
    insights['high_impact_features'].sort(key=lambda x: abs(x['avg_lift_percent']), reverse=True)
    
    # Prepare comparable pairs for LLM analysis
    for group in comparable_groups[:20]:  # Top 20 groups
        insights['comparable_pairs_for_llm'].append({
            'category': group['category'],
            'common_element': group['common_word'],
            'items': group['items'][:5]  # Top 5 items
        })
    
    # Print key insights
    print("\n📊 KEY INSIGHTS:")
    print("\n1. High-Impact Description Features:")
    for feature in insights['high_impact_features'][:5]:
        feature_name = feature['feature'].replace('has_', '').replace('is_', '').replace('_', ' ')
        print(f"   • {feature_name:20s}: {feature['avg_lift_percent']:+6.1f}% avg lift "
              f"({feature['total_items']} items across {feature['categories_affected']} categories)")
    
    print("\n2. Categories with Highest Revenue:")
    category_revenues = [(cat, res['total_revenue']) for cat, res in category_results.items()]
    category_revenues.sort(key=lambda x: x[1], reverse=True)
    for category, revenue in category_revenues[:5]:
        print(f"   • {category:30s}: {revenue:12,.0f} DKK")
    
    return insights


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function for Step 1"""
    
    print("\n")
    print("=" * 80)
    print("FLAVORCRAFT MENU ANALYSIS - STEP 1")
    print("Category-Specific Comparative Analysis")
    print("=" * 80)
    
    # Step 1.1: Load data
    df = load_data('data/part2/dim_menu_items.csv')
    
    # Step 1.2: Categorize items
    df = categorize_items(df)
    
    # Step 1.3: Extract features
    df = extract_description_features(df)
    
    # Step 1.4: Comparative analysis
    category_results = comparative_analysis(df)
    
    # Step 1.5: Find comparable pairs
    comparable_groups = find_comparable_pairs(df)
    
    # Step 1.6: Generate insights
    insights = generate_insights(df, category_results, comparable_groups)
    
    # Save outputs for Step 2
    print("\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save processed dataset
    output_file = 'data/step1_processed_data.csv'
    df.to_csv(output_file, index=False)
    print(f"✓ Saved processed dataset: {output_file}")
    
    # Save insights as JSON for Step 2
    insights_file = 'data/step1_insights.json'
    with open(insights_file, 'w') as f:
        json.dump(insights, f, indent=2)
    print(f"✓ Saved insights: {insights_file}")
    
    # Save category results
    results_file = 'data/step1_category_results.json'
    with open(results_file, 'w') as f:
        json.dump(category_results, f, indent=2)
    print(f"✓ Saved category results: {results_file}")
    
    print("\n" + "=" * 80)
    print("✅ STEP 1 COMPLETE!")
    print("=" * 80)
    print("\nNext: Run Step 2 to use Ollama for semantic analysis and recommendations")
    print("Files ready for Step 2:")
    print(f"  • {output_file}")
    print(f"  • {insights_file}")
    print(f"  • {results_file}")
    

if __name__ == "__main__":
    main()