"""Provides a service layer for interacting with the Google Gemini API.

This module includes functions for client initialization, model selection,
content generation, and managing cached content for performance optimization.
It is designed to work with the google-genai SDK for Vertex AI.
"""

import logging
from typing import List, Optional

import pandas as pd
from google import genai
from google.api_core import exceptions
from google.genai import types

logger = logging.getLogger(__name__)

# --- Model Constants ---
COMPLEX_MODEL = "gemini-2.5-pro"
SIMPLE_MODEL = "gemini-2.5-flash"
# A simple heuristic for model selection
COMPLEX_PROMPT_THRESHOLD = 1500  # characters


def initialize_gemini(project_id: str, location: str) -> Optional[genai.Client]:
    """Initializes and returns a Gemini client configured for Vertex AI."""
    if not project_id:
        logger.warning("Gemini client not initialized due to missing project_id.")
        return None
    return genai.Client(vertexai=True, project=project_id, location=location)


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


def create_cached_content_from_df(
    client: genai.Client, model: str, df: pd.DataFrame, ttl_seconds: int = 3600
) -> Optional[str]:
    """
    Creates a cached content resource from a pandas DataFrame.

    Args:
        client: The initialized Gemini client.
        model: The model name to associate with the cache.
        df: The pandas DataFrame to cache.
        ttl_seconds: The time-to-live for the cache in seconds.

    Returns:
        The resource name of the created cached content, or None on failure.
    """
    try:
        logger.info(
            "Creating cached content from DataFrame with TTL %ds...", ttl_seconds
        )
        csv_data = df.to_csv(index=False)
        content_part = types.Part.from_text(text=csv_data)
        config = types.CreateCachedContentConfig(
            contents=[types.Content(parts=[content_part], role="user")],
            ttl=f"{ttl_seconds}s",
        )

        cached_content = client.caches.create(model=model, config=config)
        logger.info("Successfully created cached content: %s", cached_content.name)
        return cached_content.name
    except (exceptions.GoogleAPICallError, ValueError) as e:
        logger.error("Failed to create cached content: %s", e)
        return None


def generate_content(
    client: genai.Client,
    prompt: str,
    tools: Optional[List[types.Tool]] = None,
    model_id: Optional[str] = None,
    cached_content_name: Optional[str] = None,
):
    """
    Generates content using the Gemini API with enhanced features.

    Args:
        client: The initialized Gemini client.
        prompt: The prompt to send to the model.
        tools: A list of tools for the model to use.
        model_id: The specific model ID to use. If None, one is chosen.
        cached_content_name: The resource name of a cached content to use.

    Returns:
        The response object from the Gemini API, or None on failure.
    """
    if model_id is None:
        model_id = _get_model_for_prompt(prompt)

    generation_config = types.GenerateContentConfig(temperature=0)
    if cached_content_name:
        # Note: When using a cache, tools cannot be used.
        generation_config.cached_content = cached_content_name
        logger.info(
            "Using cached content: %s. Tools will be disabled.", cached_content_name
        )
    else:
        generation_config.tools = tools or []

    try:
        logger.info("Generating content with model: %s", model_id)
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            generation_config=generation_config,
        )
        return response
    except (exceptions.GoogleAPICallError, ValueError) as e:
        logger.error("Gemini API call failed: %s", e)
        return None
