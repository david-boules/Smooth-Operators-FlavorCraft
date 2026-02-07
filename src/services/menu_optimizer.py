"""
Module: menu_optimizer
Description: Service layer for interacting with the Google Gemini API.
             Handles API configuration, context injection, and prompt execution.
Author: Team Flavor Flow
"""

import google.generativeai as genai
import streamlit as st
from src.utils.ai_prompts import MENU_REENGINEERING_PROMPT, NAME_ONLY_PROMPT


class MenuOptimizer:
    """
    Encapsulates the logic for Generative AI menu engineering.
    """

    def __init__(self):
        """
        Initializes the Gemini client using credentials from Streamlit secrets.
        Sets self.model to None if initialization fails to prevent runtime crashes.
        """
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Error configuring GenAI client: {str(e)}")
            self.model = None

    def improve_item(self, restaurant_name: str, item_name: str, current_description: str) -> str:
        """
        Generates improved names and descriptions for a specific menu item.

        Args:
            restaurant_name (str): The name of the restaurant (provides brand context).
            item_name (str): The name of the item to re-engineer.
            current_description (str): The existing description of the item.

        Returns:
            str: The raw text response from the LLM containing analysis and suggestions.
        """
        if not self.model:
            return "Error: AI Service is not initialized. Check API keys."

        # Inject business context into the description to align AI tone with the brand
        context_enhanced_desc = f"Served at {restaurant_name}. Original Description: {current_description}"

        final_prompt = MENU_REENGINEERING_PROMPT.format(
            item_name=item_name,
            item_description=context_enhanced_desc
        )

        try:
            with st.spinner(f"Analyzing {item_name}..."):
                response = self.model.generate_content(final_prompt)
                return response.text
        except Exception as e:
            return f"Error executing AI request: {str(e)}"

    def generate_name_ideas(self, restaurant_name: str, item_name: str) -> str:
        """
        Fallback method for items lacking a description.

        Args:
            restaurant_name (str): The name of the restaurant.
            item_name (str): The name of the item.

        Returns:
            str: AI-generated names and description.
        """
        if not self.model:
            return "Error: AI Service is not initialized."

        context_name = f"{item_name} (at {restaurant_name})"
        final_prompt = NAME_ONLY_PROMPT.format(item_name=context_name)

        try:
            response = self.model.generate_content(final_prompt)
            return response.text
        except Exception as e:
            return f"Error executing AI request: {str(e)}"
