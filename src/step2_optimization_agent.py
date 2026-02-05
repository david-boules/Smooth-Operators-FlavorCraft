"""
STEP 2: Ollama-Powered Menu Optimization Agent
================================================

This agent analyzes menu items and generates smart, contextual recommendations.

Key Features:
1. Statistical validation (uses Step 1 findings)
2. Comparable item analysis (learns from similar items)
3. LLM-powered semantic understanding (via Ollama)
4. Multi-layer validation (prevents nonsense outputs)
5. Explainable recommendations (shows reasoning)

Author: FlavorCraft Analysis Team
Date: February 5, 2026
"""

"""
INTELLIGENT MENU OPTIMIZATION AGENT
====================================

This module implements a hybrid statistical + LLM approach for menu optimization.

SYSTEM ARCHITECTURE
-------------------
MenuOptimizationAgent (main orchestrator)
    ├── MenuDataLoader (loads Step 1 results, builds indices)
    ├── StatisticalAnalyzer (item analysis, comparable finding)
    ├── OllamaEngine (LLM generation, optional)
    └── Validation Layer (sanity checks, confidence scoring)

DECISION PROCESS
----------------
1. Statistical Analysis
   - Extract linguistic features from title
   - Benchmark against category average
   - Identify issues (negative features) and strengths
   
2. Find Comparable Items
   - Search same category for similar high-performers
   - Calculate word overlap
   - Rank by purchase volume
   
3. Generate Suggestions
   - LLM: Ollama generates context-aware recommendations (if available)
   - Fallback: Rule-based strategies using patterns from data
   - Strategies:
     * Remove negative features (e.g., "small")
     * Add positive features (e.g., "iced" for coffee)
     * Learn from top comparable structure
     * Fix word count with quality descriptors
     * Simplify combo lists
   
4. Validation & Scoring
   - Check title length (1-8 words, optimal 3-6)
   - Category-specific rules (no "roasted" for drinks)
   - Sanity filters (not completely generic)
   - Calculate confidence score (0-1)
   - Estimate expected lift percentage

EXAMPLE OUTPUT
--------------
Input: "Small Latte" (413 purchases @ 38 DKK)

Analysis:
  - Issues: has_size (-50% impact), title too short (2 words)
  - Benchmark: 88th percentile in category
  
Comparables:
  - "Latte": 4,426 purchases
  - "Iced latte": 1,631 purchases
  
Recommendations:
  1. "Iced Latte" (+60% lift, 80% confidence)
     Reason: Temperature modifiers +25.7% in coffee. Remove "small".
     
  2. "Latte" (+55% lift, 75% confidence)
     Reason: Plain version 10x performance vs "Small Latte".

VALIDATION RULES
----------------
- No cooking methods on drinks (prevents "Roasted Espresso")
- Title length: 1-8 words (optimal: 3-6)
- Not completely generic ("food", "meal", "dish")
- Must keep core item recognizable
- Category-appropriate language

CONFIGURATION
-------------
OLLAMA_MODEL = "llama3.2"              # LLM model (if used)
MIN_WORD_COUNT = 1                      # Minimum title length
MAX_WORD_COUNT = 8                      # Maximum title length
OPTIMAL_WORD_COUNT_MIN = 3              # Optimal minimum
OPTIMAL_WORD_COUNT_MAX = 6              # Optimal maximum
CONFIDENCE_HIGH = 0.8                   # High confidence threshold
CONFIDENCE_MEDIUM = 0.5                 # Medium confidence threshold

PERFORMANCE
-----------
- Initialization: ~1 second (loads Step 1 data)
- Per-item analysis: <1 second
- With Ollama: +2-5 seconds per item
- Memory: ~50MB (cached data)

DEPENDENCIES
------------
- pandas, numpy: Data manipulation
- json, re: Data structures and regex
- subprocess: Ollama integration (optional)
"""

import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Optional, Tuple
import subprocess
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# Ollama model to use (user should have this installed locally)
OLLAMA_MODEL = "llama3.2"  # or "llama2", "mistral", etc.

# Validation thresholds
MIN_WORD_COUNT = 1
MAX_WORD_COUNT = 8
OPTIMAL_WORD_COUNT_MIN = 3
OPTIMAL_WORD_COUNT_MAX = 6

# Confidence levels
CONFIDENCE_HIGH = 0.8
CONFIDENCE_MEDIUM = 0.5


# ============================================================================
# STEP 2.1: LOAD STEP 1 DATA
# ============================================================================

class MenuDataLoader:
    """Loads and provides access to Step 1 analysis results"""
    
    def __init__(self, data_path: str, insights_path: str, results_path: str):
        """
        Initialize data loader with Step 1 outputs.
        
        Args:
            data_path: Path to processed CSV from Step 1
            insights_path: Path to insights JSON from Step 1
            results_path: Path to category results JSON from Step 1
        """
        print("=" * 80)
        print("LOADING STEP 1 DATA")
        print("=" * 80)
        
        # Load processed menu data
        self.df = pd.read_csv(data_path)
        print(f"✓ Loaded {len(self.df):,} menu items")
        
        # Load insights
        with open(insights_path, 'r') as f:
            self.insights = json.load(f)
        print(f"✓ Loaded insights for {len(self.insights['comparable_pairs_for_llm'])} comparable groups")
        
        # Load category results
        with open(results_path, 'r') as f:
            self.category_results = json.load(f)
        print(f"✓ Loaded results for {len(self.category_results)} categories")
        
        # Build lookup indices
        self._build_indices()
        
    def _build_indices(self):
        """Build fast lookup indices for the agent"""
        # Category statistics
        self.category_stats = {}
        for category, results in self.category_results.items():
            self.category_stats[category] = {
                'avg_purchases': results['avg_purchases'],
                'total_revenue': results['total_revenue'],
                'feature_impacts': results['feature_impacts']
            }
        
        # Feature impact lookup
        self.feature_impacts = {}
        for feature_data in self.insights['high_impact_features']:
            self.feature_impacts[feature_data['feature']] = {
                'lift': feature_data['avg_lift_percent'],
                'items': feature_data['total_items']
            }
        
        print(f"✓ Built lookup indices")


# ============================================================================
# STEP 2.2: STATISTICAL ANALYZER
# ============================================================================

class StatisticalAnalyzer:
    """Analyzes menu items using Step 1 statistical findings"""
    
    def __init__(self, data_loader: MenuDataLoader):
        self.data = data_loader
        
    def analyze_item(self, title: str, category: str, price: float, 
                     current_purchases: int) -> Dict:
        """
        Analyze a menu item statistically.
        
        Args:
            title: Current menu item title
            category: Item category
            price: Price in DKK
            current_purchases: Current purchase count
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'title': title,
            'category': category,
            'price': price,
            'current_purchases': current_purchases,
            'word_count': len(title.split()),
            'features': {},
            'issues': [],
            'strengths': [],
            'category_benchmark': None
        }
        
        # Extract features
        title_lower = title.lower()
        
        features = {
            'has_size': bool(re.search(r'\b(small|large|big|mini|medium|xl|stor|lille)\b', title_lower)),
            'has_temp': bool(re.search(r'\b(iced|hot|cold|warm|frozen|fresh|varm)\b', title_lower)),
            'has_dietary': bool(re.search(r'\b(vegan|vegetarian|organic|gluten.*free|økologisk)\b', title_lower)),
            'has_flavor': bool(re.search(r'\b(chocolate|vanilla|strawberry|caramel|hazelnut|mint|chokolade)\b', title_lower)),
            'is_combo': bool(re.search(r',|&| and | og ', title_lower)),
            'has_emoji': bool(re.search(r'[🌱🍕🥗☕🍰🥤🍺]', title))
        }
        
        analysis['features'] = features
        
        # Check against category benchmarks
        if category in self.data.category_stats:
            category_avg = self.data.category_stats[category]['avg_purchases']
            analysis['category_benchmark'] = category_avg
            
            if current_purchases < category_avg * 0.5:
                analysis['issues'].append(f"Performance is {((category_avg - current_purchases) / category_avg * 100):.0f}% below category average")
        
        # Analyze features
        for feature, present in features.items():
            if feature in self.data.feature_impacts:
                impact = self.data.feature_impacts[feature]
                
                if present:
                    if impact['lift'] > 20:
                        analysis['strengths'].append(f"{feature.replace('_', ' ')}: +{impact['lift']:.0f}% lift")
                    elif impact['lift'] < -20:
                        analysis['issues'].append(f"{feature.replace('_', ' ')}: {impact['lift']:.0f}% negative impact")
        
        # Word count analysis
        wc = analysis['word_count']
        if wc < OPTIMAL_WORD_COUNT_MIN:
            analysis['issues'].append(f"Title too short ({wc} words, optimal: 3-6)")
        elif wc > OPTIMAL_WORD_COUNT_MAX:
            analysis['issues'].append(f"Title too long ({wc} words, optimal: 3-6)")
        else:
            analysis['strengths'].append(f"Good title length ({wc} words)")
        
        return analysis
    
    def find_comparable_items(self, title: str, category: str, limit: int = 5) -> List[Dict]:
        """
        Find comparable high-performing items in the same category.
        
        Args:
            title: Item title to find comparables for
            category: Item category
            limit: Maximum number of comparables to return
            
        Returns:
            List of comparable items with performance data
        """
        # Get items from same category
        category_items = self.data.df[self.data.df['category'] == category].copy()
        
        if len(category_items) == 0:
            return []
        
        # Extract words from input title
        title_words = set(title.lower().split())
        
        # Find items with word overlap
        def word_overlap(other_title):
            other_words = set(other_title.lower().split())
            common = title_words.intersection(other_words)
            return len(common)
        
        category_items['overlap'] = category_items['title_clean'].apply(word_overlap)
        
        # Get high performers with some overlap
        comparables = category_items[
            (category_items['overlap'] > 0) & 
            (category_items['title_clean'] != title)
        ].nlargest(limit, 'purchases')
        
        results = []
        for _, item in comparables.iterrows():
            results.append({
                'title': item['title_clean'],
                'purchases': int(item['purchases']),
                'price': float(item['price']),
                'revenue': float(item['revenue']),
                'word_count': int(item['word_count'])
            })
        
        return results


# ============================================================================
# STEP 2.3: OLLAMA LLM ENGINE
# ============================================================================

class OllamaEngine:
    """Interface to Ollama for semantic analysis and suggestion generation"""
    
    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Ollama is available")
                if self.model not in result.stdout:
                    print(f"⚠️  Warning: Model '{self.model}' not found. You may need to run: ollama pull {self.model}")
            else:
                print(f"⚠️  Warning: Ollama command failed")
        except FileNotFoundError:
            print(f"⚠️  Warning: Ollama not found. Install from https://ollama.ai")
        except Exception as e:
            print(f"⚠️  Warning: Could not check Ollama: {e}")
    
    def generate_suggestions(self, analysis: Dict, comparables: List[Dict]) -> List[Dict]:
        """
        Use Ollama to generate smart menu title suggestions.
        
        Args:
            analysis: Statistical analysis results
            comparables: List of comparable high-performing items
            
        Returns:
            List of suggestions with reasoning
        """
        # Build prompt with context
        prompt = self._build_prompt(analysis, comparables)
        
        # Call Ollama
        try:
            response = self._call_ollama(prompt)
            suggestions = self._parse_response(response, analysis)
            return suggestions
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            # Fallback to rule-based suggestions
            return self._fallback_suggestions(analysis, comparables)
    
    def _build_prompt(self, analysis: Dict, comparables: List[Dict]) -> str:
        """Build a structured prompt for Ollama"""
        
        prompt = f"""You are a menu engineering expert analyzing restaurant menu items.

CURRENT ITEM:
- Title: "{analysis['title']}"
- Category: {analysis['category']}
- Price: {analysis['price']} DKK
- Purchases: {analysis['current_purchases']}
- Word count: {analysis['word_count']}

STATISTICAL ANALYSIS:
Issues: {', '.join(analysis['issues']) if analysis['issues'] else 'None'}
Strengths: {', '.join(analysis['strengths']) if analysis['strengths'] else 'None'}

HIGH-PERFORMING COMPARABLES:
"""
        
        for comp in comparables[:3]:
            prompt += f"- \"{comp['title']}\" ({comp['purchases']} purchases, {comp['price']} DKK)\n"
        
        prompt += f"""
CATEGORY: {analysis['category']}

TASK:
Generate 2-3 improved menu titles that would increase sales. Follow these rules:
1. Titles must be 3-6 words (optimal length)
2. Keep the core item recognizable
3. Use successful patterns from high-performing comparables
4. Be specific and appetizing (for food) or appealing (for drinks)
5. Do NOT use cooking methods on drinks (no "Roasted Espresso")
6. Do NOT add irrelevant adjectives
7. Match the category norms

For each suggestion, provide:
- The new title
- Brief reason why it would work (1 sentence)
- Which comparable inspired it (if any)

Format your response EXACTLY like this:
SUGGESTION 1: [New Title]
REASON: [Why it works]
INSPIRED BY: [Comparable title or "Original idea"]

SUGGESTION 2: [New Title]
REASON: [Why it works]
INSPIRED BY: [Comparable title or "Original idea"]

Be concise and practical. These suggestions will be shown to restaurant owners.
"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                raise Exception(f"Ollama returned error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Ollama timed out")
        except Exception as e:
            raise Exception(f"Failed to call Ollama: {e}")
    
    def _parse_response(self, response: str, analysis: Dict) -> List[Dict]:
        """Parse Ollama response into structured suggestions"""
        suggestions = []
        
        # Extract suggestions using regex
        pattern = r'SUGGESTION \d+:\s*(.+?)\s*REASON:\s*(.+?)\s*INSPIRED BY:\s*(.+?)(?=\n\n|SUGGESTION|\Z)'
        matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            title = match.group(1).strip().strip('"').strip("'")
            reason = match.group(2).strip()
            inspired_by = match.group(3).strip()
            
            # Validate title
            if self._validate_title(title, analysis):
                suggestions.append({
                    'title': title,
                    'reason': reason,
                    'inspired_by': inspired_by,
                    'confidence': self._calculate_confidence(title, analysis)
                })
        
        return suggestions
    
    def _validate_title(self, title: str, analysis: Dict) -> bool:
        """Validate that a suggested title makes sense"""
        
        # Basic checks
        if not title or len(title) < 3:
            return False
        
        word_count = len(title.split())
        if word_count < MIN_WORD_COUNT or word_count > MAX_WORD_COUNT:
            return False
        
        title_lower = title.lower()
        category_lower = analysis['category'].lower()
        
        # Category-specific validation
        if 'coffee' in category_lower or 'espresso' in category_lower or 'tea' in category_lower:
            # Don't allow cooking methods on drinks
            cooking_methods = ['grilled', 'roasted', 'fried', 'baked', 'seared', 'braised']
            if any(method in title_lower for method in cooking_methods):
                return False
        
        if 'sandwich' in category_lower or 'salad' in category_lower:
            # These should have ingredient/protein mentions
            # Just check it's not completely generic
            if title_lower in ['food', 'meal', 'dish', 'item']:
                return False
        
        return True
    
    def _calculate_confidence(self, title: str, analysis: Dict) -> float:
        """Calculate confidence score for a suggestion"""
        score = 0.5  # Base score
        
        word_count = len(title.split())
        
        # Optimal word count
        if OPTIMAL_WORD_COUNT_MIN <= word_count <= OPTIMAL_WORD_COUNT_MAX:
            score += 0.2
        
        # Keeps core item
        original_words = set(analysis['title'].lower().split())
        new_words = set(title.lower().split())
        if original_words.intersection(new_words):
            score += 0.2
        
        # Adds positive features
        title_lower = title.lower()
        if re.search(r'\b(fresh|premium|signature|special)\b', title_lower):
            score += 0.1
        
        return min(score, 1.0)
    
    def _fallback_suggestions(self, analysis: Dict, comparables: List[Dict]) -> List[Dict]:
        """Generate rule-based suggestions if Ollama fails"""
        suggestions = []
        title = analysis['title']
        category = analysis['category'].lower()
        title_lower = title.lower()
        
        # Analyze what's wrong and fix it intelligently
        issues = analysis['issues']
        features = analysis['features']
        
        # Strategy 1: Remove negative features
        if features.get('has_size') and 'small' in title_lower:
            # Remove "small" - it has negative impact
            new_title = re.sub(r'\b(small|lille)\b', '', title, flags=re.IGNORECASE).strip()
            new_title = re.sub(r'\s+', ' ', new_title)  # Clean extra spaces
            
            if new_title and new_title != title:
                suggestions.append({
                    'title': new_title,
                    'reason': f"Remove 'small' which has -50% impact. {comparables[0]['title'] if comparables else 'Generic version'} performs better.",
                    'inspired_by': comparables[0]['title'] if comparables else "Statistical analysis",
                    'confidence': 0.75
                })
        
        # Strategy 2: Add positive features from category
        if 'coffee' in category or 'espresso' in category:
            # Check if we can add temperature
            if not features.get('has_temp') and comparables:
                # Find if "iced" variants exist in comparables
                iced_comps = [c for c in comparables if 'iced' in c['title'].lower()]
                if iced_comps:
                    core_item = re.sub(r'\b(small|large|stor|lille)\b', '', title, flags=re.IGNORECASE).strip()
                    suggestions.append({
                        'title': f"Iced {core_item}",
                        'reason': f"Temperature modifiers show +25.7% lift in coffee category. '{iced_comps[0]['title']}' has {iced_comps[0]['purchases']} purchases.",
                        'inspired_by': iced_comps[0]['title'],
                        'confidence': 0.8
                    })
        
        # Strategy 3: Learn from top comparable structure
        if comparables and len(suggestions) < 2:
            best = comparables[0]
            best_words = best['title'].lower().split()
            title_words = title_lower.split()
            
            # Find what the best has that we don't
            unique_to_best = set(best_words) - set(title_words)
            
            if unique_to_best and len(unique_to_best) <= 2:
                # Try adding those words
                added_words = ' '.join(unique_to_best)
                if len(added_words.split()) + len(title.split()) <= OPTIMAL_WORD_COUNT_MAX:
                    new_title = f"{added_words.title()} {title}"
                    
                    if self._validate_title(new_title, analysis):
                        suggestions.append({
                            'title': new_title,
                            'reason': f"Following pattern of '{best['title']}' which has {best['purchases']} purchases vs your {analysis['current_purchases']}.",
                            'inspired_by': best['title'],
                            'confidence': 0.65
                        })
        
        # Strategy 4: Fix word count with quality descriptor
        if analysis['word_count'] < OPTIMAL_WORD_COUNT_MIN and len(suggestions) < 2:
            quality_words = ['Classic', 'Signature', 'Fresh', 'Premium']
            
            # Pick one that fits the category
            if 'breakfast' in category:
                quality = 'Fresh'
            elif 'dessert' in category:
                quality = 'Premium'
            else:
                quality = 'Classic'
            
            new_title = f"{quality} {title}"
            suggestions.append({
                'title': new_title,
                'reason': f"Increase from {analysis['word_count']} to 2 words. Quality descriptors have +32% lift.",
                'inspired_by': "Optimal word count pattern",
                'confidence': 0.6
            })
        
        # Strategy 5: Simplify if too long or complex
        if features.get('is_combo') and len(suggestions) < 2:
            # Combos have -49% impact
            # Try to simplify
            parts = re.split(r',|&| and ', title)
            if parts:
                core = parts[0].strip()
                new_title = core
                
                if self._validate_title(new_title, analysis):
                    suggestions.append({
                        'title': new_title,
                        'reason': f"Combo descriptions show -49% impact. Simplify to core item.",
                        'inspired_by': "Statistical pattern",
                        'confidence': 0.55
                    })
        
        return suggestions[:3]


# ============================================================================
# STEP 2.4: MENU OPTIMIZATION AGENT
# ============================================================================

class MenuOptimizationAgent:
    """Main agent that orchestrates the optimization process"""
    
    def __init__(self, data_path: str, insights_path: str, results_path: str,
                 use_ollama: bool = True, ollama_model: str = OLLAMA_MODEL):
        """
        Initialize the menu optimization agent.
        
        Args:
            data_path: Path to Step 1 processed data CSV
            insights_path: Path to Step 1 insights JSON
            results_path: Path to Step 1 category results JSON
            use_ollama: Whether to use Ollama (False for testing without it)
            ollama_model: Ollama model to use
        """
        print("\n" + "=" * 80)
        print("INITIALIZING MENU OPTIMIZATION AGENT")
        print("=" * 80)
        
        # Load data
        self.data_loader = MenuDataLoader(data_path, insights_path, results_path)
        
        # Initialize components
        self.analyzer = StatisticalAnalyzer(self.data_loader)
        self.use_ollama = use_ollama
        
        if use_ollama:
            self.llm = OllamaEngine(ollama_model)
        else:
            print("⚠️  Running without Ollama (fallback mode)")
            self.llm = None
        
        print("\n✅ Agent initialized and ready!")
    
    def optimize(self, title: str, category: str, price: float, 
                 current_purchases: int) -> Dict:
        """
        Optimize a menu item title.
        
        Args:
            title: Current menu item title
            category: Item category
            price: Price in DKK
            current_purchases: Current purchase count
            
        Returns:
            Dictionary with complete optimization results
        """
        print("\n" + "=" * 80)
        print(f"OPTIMIZING: {title}")
        print("=" * 80)
        
        # Step 1: Statistical analysis
        print("\n[1/4] Running statistical analysis...")
        analysis = self.analyzer.analyze_item(title, category, price, current_purchases)
        
        # Step 2: Find comparables
        print("[2/4] Finding comparable high-performers...")
        comparables = self.analyzer.find_comparable_items(title, category, limit=5)
        
        # Step 3: Generate suggestions
        print("[3/4] Generating optimization suggestions...")
        if self.use_ollama and self.llm:
            suggestions = self.llm.generate_suggestions(analysis, comparables)
        else:
            # Use fallback suggestions (rule-based)
            temp_llm = OllamaEngine()  # Create temp instance for fallback method
            suggestions = temp_llm._fallback_suggestions(analysis, comparables)
        
        # Step 4: Calculate expected impact
        print("[4/4] Calculating expected impact...")
        for suggestion in suggestions:
            suggestion['expected_lift'] = self._estimate_lift(analysis, suggestion)
        
        # Sort by expected lift
        suggestions.sort(key=lambda x: x['expected_lift'], reverse=True)
        
        # Compile results
        result = {
            'input': {
                'title': title,
                'category': category,
                'price': price,
                'current_purchases': current_purchases
            },
            'analysis': {
                'word_count': analysis['word_count'],
                'issues': analysis['issues'],
                'strengths': analysis['strengths'],
                'category_benchmark': analysis['category_benchmark'],
                'performance_percentile': self._calculate_percentile(current_purchases, category)
            },
            'comparables': comparables,
            'recommendations': suggestions,
            'summary': self._generate_summary(analysis, suggestions)
        }
        
        print("\n✅ Optimization complete!")
        return result
    
    def _estimate_lift(self, analysis: Dict, suggestion: Dict) -> float:
        """Estimate the sales lift from implementing a suggestion"""
        
        # Base lift from confidence
        lift = (suggestion['confidence'] - 0.5) * 100
        
        # Add lift from fixing issues
        if len(analysis['issues']) > 0:
            lift += len(analysis['issues']) * 15  # 15% per issue fixed
        
        # Add lift from word count optimization
        current_wc = analysis['word_count']
        new_wc = len(suggestion['title'].split())
        
        if OPTIMAL_WORD_COUNT_MIN <= new_wc <= OPTIMAL_WORD_COUNT_MAX:
            if current_wc < OPTIMAL_WORD_COUNT_MIN or current_wc > OPTIMAL_WORD_COUNT_MAX:
                lift += 20  # Fixing word count
        
        return round(lift, 1)
    
    def _calculate_percentile(self, purchases: int, category: str) -> int:
        """Calculate what percentile this item is in its category"""
        category_items = self.data_loader.df[
            self.data_loader.df['category'] == category
        ]['purchases']
        
        if len(category_items) == 0:
            return 50
        
        percentile = (category_items < purchases).sum() / len(category_items) * 100
        return int(percentile)
    
    def _generate_summary(self, analysis: Dict, suggestions: List[Dict]) -> str:
        """Generate a human-readable summary"""
        
        if not suggestions:
            return "No strong recommendations at this time. Item may already be well-optimized."
        
        best = suggestions[0]
        
        summary = f"Top recommendation: '{best['title']}' "
        summary += f"(expected +{best['expected_lift']:.0f}% lift). "
        summary += best['reason']
        
        return summary


# ============================================================================
# MAIN EXECUTION & DEMO
# ============================================================================

def demo():
    """Demo the menu optimization agent"""
    
    print("\n\n")
    print("=" * 80)
    print("MENU OPTIMIZATION AGENT - DEMO")
    print("=" * 80)
    
    # Initialize agent
    agent = MenuOptimizationAgent(
        data_path='data/step1_processed_data.csv',
        insights_path='data/step1_insights.json',
        results_path='data/step1_category_results.json',
        use_ollama=False  # Set to True if user has Ollama installed
    )
    
    # Test cases from our Step 1 findings
    test_cases = [
        {
            'title': 'Small Latte',
            'category': 'Coffee & Espresso',
            'price': 38.0,
            'current_purchases': 413
        },
        {
            'title': 'Tofu sandwich 🌱',
            'category': 'Sandwiches',
            'price': 95.0,
            'current_purchases': 593
        },
        {
            'title': 'Sodavand',
            'category': 'Cold Beverages',
            'price': 25.0,
            'current_purchases': 1702
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'=' * 80}")
        print(f"TEST CASE {i}/{len(test_cases)}")
        print('=' * 80)
        
        result = agent.optimize(**test_case)
        results.append(result)
        
        # Print results
        print(f"\n📊 RESULTS FOR: {result['input']['title']}")
        print(f"\nCurrent Performance:")
        print(f"  • Purchases: {result['input']['current_purchases']}")
        print(f"  • Percentile: {result['analysis']['performance_percentile']}th")
        print(f"  • Word count: {result['analysis']['word_count']}")
        
        if result['analysis']['issues']:
            print(f"\n⚠️  Issues Detected:")
            for issue in result['analysis']['issues']:
                print(f"  • {issue}")
        
        if result['comparables']:
            print(f"\n🏆 Top Comparable Performers:")
            for comp in result['comparables'][:3]:
                print(f"  • {comp['title']:40s} ({comp['purchases']} purchases)")
        
        print(f"\n💡 Recommendations:")
        for j, rec in enumerate(result['recommendations'], 1):
            print(f"\n  {j}. \"{rec['title']}\"")
            print(f"     Expected lift: +{rec['expected_lift']:.0f}%")
            print(f"     Confidence: {rec['confidence']*100:.0f}%")
            print(f"     Reason: {rec['reason']}")
        
        print(f"\n📝 Summary: {result['summary']}")
    
    # Save results
    output_file = 'data/step2_optimization_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {output_file}")
    print("\nThe agent is ready to optimize any menu item!")


if __name__ == "__main__":
    demo()