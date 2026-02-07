"""
Module: menu_optimizer
Description: Service layer for interacting with the Google GenAI SDK.
Author: Team Flavor Flow
"""

from google import genai
import streamlit as st
from src.utils.ai_prompts import MENU_REENGINEERING_PROMPT, NAME_ONLY_PROMPT


class MenuOptimizer:
    """
    Encapsulates the logic for GenAI menu engineering.
    """

    def __init__(self):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            st.error(f"Error configuring GenAI client: {str(e)}")
            self.client = None

    def improve_item(self, restaurant_name: str, item_name: str, current_description: str) -> str:
        if not self.client:
            return "Error: AI Service is not initialized. Check API keys."

        context_enhanced_desc = f"Served at {restaurant_name}. Original Description: {current_description}"
        final_prompt = MENU_REENGINEERING_PROMPT.format(
            item_name=item_name,
            item_description=context_enhanced_desc
        )

        try:
            with st.spinner(f"Analyzing {item_name}..."):
                # CHANGED MODEL HERE
                response = self.client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=final_prompt
                )
                return response.text
        except Exception as e:
            return f"Error executing AI request: {str(e)}"

    def generate_name_ideas(self, restaurant_name: str, item_name: str) -> str:
        if not self.client:
            return "Error: AI Service is not initialized."

        context_name = f"{item_name} (at {restaurant_name})"
        final_prompt = NAME_ONLY_PROMPT.format(item_name=context_name)

        try:
            # CHANGED MODEL HERE
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=final_prompt
            )
            return response.text
        except Exception as e:
            return f"Error executing AI request: {str(e)}"