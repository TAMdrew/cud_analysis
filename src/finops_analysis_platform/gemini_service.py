import logging
from typing import List, Optional

from google.api_core import exceptions
from google import genai
from google.genai.types import GenerateContentConfig, Tool, Part
from google.protobuf import duration_pb2
import pandas as pd

logger = logging.getLogger(__name__)

# --- Model Constants ---
COMPLEX_MODEL = "gemini-2.5-pro"
SIMPLE_MODEL = "gemini-2.5-flash"
# A simple heuristic for model selection: prompts longer than this are considered "complex"
COMPLEX_PROMPT_THRESHOLD = 1500  # characters

def initialize_gemini(project_id: str, location: str) -> genai.Client:
    """Initializes and returns a Gemini client configured for Vertex AI."""
    return genai.Client(vertexai=True, project=project_id, location=location)

def _get_model_for_prompt(prompt: str) -> str:
    """Selects a cost-effective model based on prompt complexity."""
    if len(prompt) > COMPLEX_PROMPT_THRESHOLD:
        logger.info(f"Prompt is long ({len(prompt)} chars). Using complex model: {COMPLEX_MODEL}")
        return COMPLEX_MODEL
    logger.info(f"Prompt is short ({len(prompt)} chars). Using simple model: {SIMPLE_MODEL}")
    return SIMPLE_MODEL

def create_cached_content_from_df(
    client: genai.Client, model: str, df: pd.DataFrame, ttl_seconds: int = 3600
) -> Optional[str]:
    """
    Creates a cached content resource from a pandas DataFrame.

    Args:
        client: The initialized Gemini client.
        model: The model to use for caching (e.g., 'gemini-2.5-pro').
        df: The pandas DataFrame to cache.
        ttl_seconds: The time-to-live for the cache in seconds.

    Returns:
        The resource name of the created cached content, or None on failure.
    """
    try:
        logger.info(f"Creating cached content from DataFrame with TTL {ttl_seconds}s...")
        # Convert DataFrame to a CSV string to create a Part
        content_part = Part.from_text(df.to_csv(index=False))
        cached_content = client.create_cached_content(
            model=model,
            contents=[content_part],
            ttl=duration_pb2.Duration(seconds=ttl_seconds)
        )
        logger.info(f"Successfully created cached content: {cached_content.name}")
        return cached_content.name
    except (exceptions.GoogleAPICallError, ValueError) as e:
        logger.error(f"Failed to create cached content: {e}")
        return None

def generate_content(
    client: genai.Client,
    prompt: str,
    tools: Optional[List[Tool]] = None,
    model_id: Optional[str] = None,
    cached_content_name: Optional[str] = None
):
    """
    Generates content using the Gemini API with enhanced features.

    Args:
        client: The initialized Gemini client.
        prompt: The prompt to send to the model.
        tools: A list of tools for the model to use.
        model_id: The specific model ID to use. If None, a model is chosen automatically.
        cached_content_name: The resource name of a cached content to use.

    Returns:
        The response object from the Gemini API, or None on failure.
    """
    if model_id is None:
        model_id = _get_model_for_prompt(prompt)

    config = GenerateContentConfig(
        tools=tools or [],
        temperature=0,
    )
    if cached_content_name:
        # Note: When using a cache, tools and system_instructions cannot be used.
        # This is a limitation of the API. The calling code should be aware of this.
        config.cached_content = cached_content_name
        config.tools = [] # Clear tools when using cache
        logger.info(f"Using cached content: {cached_content_name}. Tools will be disabled.")

    try:
        logger.info(f"Generating content with model: {model_id}")
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config,
        )
        return response
    except (exceptions.GoogleAPICallError, ValueError) as e:
        logger.error(f"Gemini API call failed: {e}")
        return None
