"""Provides a service layer for interacting with the Google Gemini API.

This module uses the unified `google-generativeai` SDK and provides a clear
initialization function to configure it for use with Vertex AI.
"""

import logging
from typing import List, Optional

import google.generativeai as genai
from google.api_core import exceptions
from google.generativeai.types import GenerationConfig, Tool

logger = logging.getLogger(__name__)

# --- Model Constants ---
COMPLEX_MODEL = "gemini-1.5-pro-preview-0409"
SIMPLE_MODEL = "gemini-1.5-flash-preview-0514"
COMPLEX_PROMPT_THRESHOLD = 1500  # characters


def initialize_gemini(project_id: str, location: str) -> bool:
    """Initializes and configures the Gemini SDK to use Vertex AI.

    This function must be called before `generate_content`.

    Args:
        project_id: The Google Cloud project ID.
        location: The Google Cloud location (e.g., 'us-central1').

    Returns:
        True if initialization was successful, False otherwise.
    """
    try:
        genai.configure(project=project_id, location=location)
        logger.info(
            "Gemini SDK configured for Vertex AI in project '%s' and location '%s'",
            project_id,
            location,
        )
        return True
    except (ValueError, TypeError, exceptions.GoogleAPICallError) as e:
        logger.error("Failed to configure Gemini SDK for Vertex AI: %s", e)
        return False


def _get_model_for_prompt(prompt: str) -> str:
    """Selects a cost-effective model based on prompt complexity."""
    if len(prompt) > COMPLEX_PROMPT_THRESHOLD:
        return COMPLEX_MODEL
    return SIMPLE_MODEL


def generate_content(
    prompt: str,
    tools: Optional[List[Tool]] = None,
    model_id: Optional[str] = None,
) -> Optional[genai.types.GenerateContentResponse]:
    """Generates content using the configured Gemini API client.

    Args:
        prompt: The prompt to send to the model.
        tools: A list of tools for the model to use.
        model_id: The specific model ID to use.

    Returns:
        The response object from the Gemini API, or None on failure.
    """
    if model_id is None:
        model_id = _get_model_for_prompt(prompt)

    generation_config = GenerationConfig(temperature=0)

    try:
        model = genai.GenerativeModel(
            model_id,
            system_instruction="You are a helpful financial analyst specialized in Google Cloud.",
        )
        logger.info("Generating content with model: %s", model_id)
        response = model.generate_content(
            contents=prompt,
            generation_config=generation_config,
            tools=tools,
        )
        return response
    except (exceptions.GoogleAPICallError, ValueError, TypeError, Exception) as e:
        logger.error("Gemini API call failed: %s", e)
        return None
