"""Provides a service layer for interacting with the Google Gemini API.

This module includes functions for client initialization, model selection,
and content generation. It is designed to work with the google-generativeai
SDK configured for use with Vertex AI.
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
# A simple heuristic for model selection
COMPLEX_PROMPT_THRESHOLD = 1500  # characters


def initialize_gemini(project_id: str, location: str) -> bool:
    """Initializes the Gemini client by configuring the SDK for Vertex AI."""
    if not project_id:
        logger.warning("Gemini client not initialized due to missing project_id.")
        return False
    try:
        genai.configure(transport="vertex_ai", project=project_id, location=location)
        logger.info(
            "Gemini SDK configured for Vertex AI in project '%s' and location '%s'",
            project_id,
            location,
        )
        return True
    except (exceptions.GoogleAPICallError, ValueError, ImportError) as e:
        logger.error("Failed to configure Gemini SDK for Vertex AI: %s", e)
        return False


def _get_model_for_prompt(prompt: str) -> str:
    """Selects a cost-effective model based on prompt complexity."""
    if len(prompt) > COMPLEX_PROMPT_THRESHOLD:
        logger.info(
            "Prompt is long (%d chars). Using complex model: %s",
            len(prompt),
            COMPLEX_MODEL,
        )
        return COMPLEX_MODEL
    logger.info(
        "Prompt is short (%d chars). Using simple model: %s", len(prompt), SIMPLE_MODEL
    )
    return SIMPLE_MODEL


def generate_content(
    prompt: str,
    tools: Optional[List[Tool]] = None,
    model_id: Optional[str] = None,
) -> Optional[genai.types.GenerateContentResponse]:
    """
    Generates content using the Gemini API.

    Args:
        prompt: The prompt to send to the model.
        tools: A list of tools for the model to use.
        model_id: The specific model ID to use. If None, one is chosen.

    Returns:
        The response object from the Gemini API, or None on failure.
    """
    if model_id is None:
        model_id = _get_model_for_prompt(prompt)

    generation_config = GenerationConfig(temperature=0)

    try:
        logger.info("Generating content with model: %s", model_id)
        model = genai.GenerativeModel(model_id)
        response = model.generate_content(
            contents=prompt, generation_config=generation_config, tools=tools
        )
        return response
    except (exceptions.GoogleAPICallError, ValueError, TypeError) as e:
        logger.error("Gemini API call failed: %s", e)
        return None
