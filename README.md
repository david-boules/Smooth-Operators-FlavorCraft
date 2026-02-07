# Smooth-Operators-FlavorCraft
AI-powered menu optimization platform that leverages the FlavorCraft data to generate actionable pricing and profitability insights | Deloitte x AUC Hackathon

---

## 📖 Table of Contents
- [Executive Summary](#-executive-summary)
- [Team & Contributions](#-team--contributions)
- [Project Architecture](#-project-architecture)
  - [1. Behavioral Analytics (Data)](#1-behavioral-analytics-data)
  - [2. Menu Matrix Classification (ML)](#2-menu-matrix-classification-ml)
  - [3. Price Optimization (Math)](#3-price-optimization-math)
  - [4. Semantic Optimization (AI)](#4-semantic-optimization-ai)
  - [5. The "Menu Doctor" System (Engineering)](#5-the-menu-doctor-system-engineering)
- [Installation & Usage](#-installation--usage)
- [Technical Stack](#-technical-stack)
  

---

## 🚀 Executive Summary

**Smooth Operators** solves the disconnect between *analyzing* a menu and *fixing* it. We built a unified platform that integrates customer behavior patterns, mathematical price optimization, and Generative AI to autonomously re-engineer FlavorCraft's menu.

Our solution answers four critical business questions through a multi-disciplinary approach:
1.  **Diagnostics:** Identifying hidden customer buying patterns.
2.  **Classification:** Categorizing items into Stars, Plowhorses, Puzzles, and Dogs.
3.  **Optimization:** Mathematically determining the perfect price point.
4.  **Action:** Using AI to rewrite descriptions for maximum conversion.

---

Our team operated as a specialized Menu Engineering department, with each member leading a specific technical domain:

| Team Member | Role | Key Contribution |
|:-----------|:-----|:------------------|
| **Wassim** | **Data Analysis Lead** | • **Hidden Patterns:** Conducted deep-dive segmentation to find "Whale" customers and basket affinities.<br>• Uncovered the "Loyalty Gap" and purchasing triggers. |
| **Basel Morsy** | **ML Engineer** | • **Menu Matrix:** Built the classification engine that segments items into *Stars, Plowhorses, Puzzles,* and *Dogs*.<br>• Worked with Marwan to design the logic for "Promote, Re-engineer, Eliminate" decisions. |
| **Abdelrahman** | **Mathematical Modeler** | • **Profitability Logic:** Developed the mathematical models to adjust pricing for maximum margin without sacrificing volume.<br>• Calculated price elasticity and optimal price points. |
| **David Boules** | **AI Researcher** | • **Semantic Analysis:** Analyzed thousands of menu descriptions to quantify the impact of specific words (e.g., "Organic" = +122% lift).<br>• Defined the "Power Words" for the AI to use. |
| **Marwan** | **AI Engineering Lead** | • **Generative System:** Architected the LLM agent that ingests the insights from Basel and David to autonomously rewrite the menu.<br>• Built the "Menu Doctor" persona and prompt engineering. |
| **Yaseen** | **Full Stack Engineer** | • **System Integration:** Built the unified Streamlit interface that links all Python files and SQL queries.<br>• Created the seamless user experience connecting Data, ML, and AI modules. |

---

## 🏗 Project Architecture (Solution Components)

### 1. Behavioral Analytics (Data)
**Owner: Wassim** *The Foundation.* Before changing anything, we analyzed 42.6M DKK of transaction data to understand *who* is buying.
* **Key Insight:** Detected "Cannibalization" where low-margin items steal sales from premium ones.
* **Basket Affinity:** Mapped which items are frequently bought together to drive bundle recommendations.

### 2. Menu Matrix Classification (ML)
**Owner: Basel Morsy** *The Triage.* This module ingests sales and cost data to categorize every menu item:
* 🐕 **Dogs:** Low Profit / Low Popularity → *Action: Eliminate.*
* 🧩 **Puzzles:** High Profit / Low Popularity → *Action: Re-engineer (Marketing).*
* 🐴 **Plowhorses:** Low Profit / High Popularity → *Action: Price Increase.*
* ⭐ **Stars:** High Profit / High Popularity → *Action: Promote.*

### 3. Price Optimization (Math)
**Owner: Abdelrahman** *The Revenue Engine.* For "Plowhorses" (items that sell well but lose money), this module calculates the exact price increase needed to flip them into "Stars" using elasticity modeling.

### 4. Semantic Optimization (AI)
**Owner: David Boules** *The Psychology.* We didn't just guess what words work; we proved it.
* **Discovery:** Identified that "Size" indicators (e.g., "Small Latte") negatively impact sales by -50%.
* **Strategy:** Replacing size indicators with "Experience" descriptors (e.g., "Classic Latte") maximizes conversion.

### 5. The "Menu Doctor" System (Engineering)
**Owners: Marwan (AI) & Yaseen (Integration)** *The Solution.* This is the interactive application where it all comes together.
* **The AI Agent:** Marwan built a Gemini-powered agent that takes a "Puzzle" item and rewrites it using David's semantic rules and Abdelrahman's pricing logic.
* **The Interface:** Yaseen built a robust Streamlit dashboard that allows store managers to visualize Basel's matrix and "Click-to-Fix" any failing menu item in real-time.


#### Technical Implementation

**Data Processing Pipeline:**
```
Raw Menu Data (30,407 items)
    ↓
Filter & Clean (10,945 active items with ≥5 purchases)
    ↓
Feature Extraction (size, temperature, dietary, flavor, etc.)
    ↓
Category Assignment (10 categories using keyword matching)
    ↓
Comparative Analysis (within-category performance metrics)
    ↓
Statistical Validation (feature impact quantification)
```

**Agent Decision Process:**
```
Input: Menu Item Details
    ↓
1. Statistical Analysis (extract features, benchmark vs category)
    ↓
2. Find Comparables (similar high-performers in category)
    ↓
3. Generate Suggestions (LLM or rule-based strategies)
    ↓
4. Validation Layer (sanity checks, word count, category rules)
    ↓
Output: Ranked Recommendations with Expected Lift
```

#### Running the Solution

**Prerequisites:**
```bash
pip install -r requirements.txt
```

**Execute Analysis:**
```bash
# Step 1: Generate insights from menu data
python src/step1_category_analysis.py

# Step 2: Optimize a specific menu item
python -c "
from src.step2_optimization_agent import MenuOptimizationAgent
agent = MenuOptimizationAgent(
    data_path='data/step1_processed_data.csv',
    insights_path='data/step1_insights.json',
    results_path='data/step1_category_results.json',
    use_ollama=False
)
result = agent.optimize('Small Latte', 'Coffee & Espresso', 38.0, 413)
print(f\"Top recommendation: {result['recommendations'][0]['title']}\")
print(f\"Expected lift: +{result['recommendations'][0]['expected_lift']}%\")
"

# Step 3: Launch interactive demo
streamlit run src/step3_interactive_demo.py
```

**Using the CLI Interface:**
```bash
python main.py step1                           # Run full analysis
python main.py step2 "Small Latte" "Coffee & Espresso" 38 413
python main.py demo                            # Launch Streamlit
```

#### Business Impact

**Quantified Opportunities:**
- 11,227 items require optimization (68% of menu)
- Average expected lift: +30% per optimized item
- Estimated total impact: 1.48M+ DKK additional annual revenue
- Implementation cost: Zero (description changes only)

**Scalability:**
- Works for any menu item in any category
- Self-improving (learns from new data)
- Can be deployed as API or web service
- Applicable beyond FlavorCraft (any food service business)

#### Files & Outputs

**Source Code:**
- `src/step1_category_analysis.py` - Statistical discovery engine (606 lines)
- `src/step2_optimization_agent.py` - Main optimization agent (782 lines)
- `src/step3_interactive_demo.py` - Streamlit UI (237 lines)
- `main.py` - CLI interface

**Generated Data:**
- `data/step1_processed_data.csv` - Processed menu items with features
- `data/step1_insights.json` - Structured findings for agent
- `data/step1_category_results.json` - Per-category analysis

**Documentation:**
- Analysis methodology and findings
- Usage examples and API reference
- Business impact calculations

---

Required packages:
- pandas >= 2.0.0
- numpy >= 1.24.0
- streamlit >= 1.28.0

### Optional: Ollama Integration
For enhanced LLM capabilities, install Ollama locally:
1. Download from https://ollama.ai
2. Install and run: `ollama pull llama3.2`
3. Set `use_ollama=True` in agent initialization

### Dataset Setup
The full dataset files are not included in this repository due to size constraints.

**To run the analysis:**
1. Download dataset from hackathon release page
2. Extract to `data/part2/` directory
3. Ensure `dim_menu_items.csv` is at: `data/part2/dim_menu_items.csv`

**Pre-processed data IS included:**
- `data/step1_processed_data.csv` - Ready for agent use
- `data/step1_insights.json` - Agent can run immediately
- `data/step1_category_results.json` - Category benchmarks

---

## Usage

### Menu Description Optimization

**Option 1: Run Complete Analysis**
```bash
python src/step1_category_analysis.py
```
Outputs insights to `data/` directory (~30 seconds runtime)

**Option 2: Optimize Specific Items**
```python
from src.step2_optimization_agent import MenuOptimizationAgent

agent = MenuOptimizationAgent(
    data_path='data/step1_processed_data.csv',
    insights_path='data/step1_insights.json',
    results_path='data/step1_category_results.json'
)

result = agent.optimize(
    title="Small Latte",
    category="Coffee & Espresso",
    price=38.0,
    current_purchases=413
)

# View recommendations
for rec in result['recommendations']:
    print(f"{rec['title']}: +{rec['expected_lift']}% lift")
    print(f"Reason: {rec['reason']}")
```

**Option 3: Interactive Web Interface**
```bash
streamlit run src/step3_interactive_demo.py
```
Opens browser at http://localhost:8501

**Option 4: Command Line Interface**
```bash
python main.py step1                                    # Analyze full menu
python main.py step2 "Item Name" "Category" 50 100     # Optimize one item
python main.py demo                                     # Launch web UI
```

### [Additional Solutions Usage]
[To be completed by teammates]

---

## Technical Stack

### Core Technologies
- **Python 3.12** - Primary development language
- **pandas** - Data manipulation and analysis
- **numpy** - Statistical computations
- **Streamlit** - Interactive web interface

### Optional Components
- **Ollama** - Local LLM for semantic understanding (llama3.2)
- **Git LFS** - Large file storage (if needed for datasets)

### Development Tools
- **VS Code / Cursor** - IDE
- **Git** - Version control
- **Virtual Environment** - Dependency isolation

---

## Project Structure

```
## 📂 Repository Structure

| Folder | Description |
| :--- | :--- |
| `src/frontend` | Streamlit UI components and tab layouts. |
| `src/services` | Core business logic (Analytics, AI Optimizer, Database). |
| `src/workflows` | The 3-step menu engineering pipeline. |
| `notebooks/` | Exploratory Data Analysis (EDA) and initial findings. |
| `tests/` | Unit and Integration tests for system reliability. |
| `data/` | Raw transaction and menu datasets. |
| `docs/` | Final Report PDF and Roadmap. |
```

### Technical Skills
- Advanced data analysis and feature engineering
- Statistical validation and hypothesis testing
- AI/ML integration (LLM + rule-based hybrid)
- System architecture and modular design
- Production-quality code with documentation

### Business Value
- Direct answer to business question with quantified impact
- Scalable solution applicable to any menu
- Zero-cost implementation (pure profit potential)
- Clear ROI calculations (e.g., +119% for "Small Latte" → "Iced Latte")

### AI/ML Integration
- Hybrid approach: statistical baseline + LLM semantic understanding
- Multi-layer validation prevents hallucinations
- Context-aware recommendations (not generic templates)
- Fallback strategies ensure reliability

### Innovation
- Novel combination of statistical analysis + LLM validation
- Comparable item analysis (learning from actual high performers)
- Explainable AI (every recommendation shows reasoning)
- Category-specific intelligence (coffee ≠ sandwiches)

### Team Collaboration
- Well-documented codebase for collaboration
- Modular architecture (teammates can add components)
- Clear separation of concerns (data/analysis/presentation)
- Comprehensive README for knowledge transfer

---

## Repository Statistics

- **Total Lines of Code:** ~1,600 lines (Python)
- **Data Processed:** 10,945 menu items, 42.6M DKK revenue
- **Categories Analyzed:** 10 distinct menu categories
- **Features Extracted:** 7 linguistic features per item
- **Comparable Groups Found:** 2,084 groups for analysis
- **Test Cases Validated:** 3 primary examples with strong results
  
---
## 💻 Installation & Usage

### Prerequisites
* Python 3.10+
* Google Gemini API Key

### Setup
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Environment
# Rename .env.example to .env and add your GEMINI_API_KEY


### Dependencies
```bash
pip install -r requirements.txt
```

---

## License & Attribution

**Created for:** Deloitte x AUC Hackathon 2026  
**Challenge:** FlavorCraft Menu Engineering  
**Team:** Smooth Operators  

This project was developed as part of the hackathon challenge. All data used is provided by the hackathon organizers.

---

## Contact & Support

For questions about the menu description optimization solution:
- Review code documentation in `src/` directory
- Check analysis outputs in `data/` directory
- Run interactive demo for hands-on exploration

For questions about other solution components:
- [To be added by teammates]

---

**Status:** Production-ready | Demo-ready | Documented  
**Last Updated:** February 5, 2026
