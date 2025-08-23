import os
from typing import List
from google import genai
from google.genai.types import GenerateContentConfig, Tool, ToolCodeExecution, UrlContext

def initialize_gemini(project_id: str, location: str) -> genai.Client:
    """
    Initializes and returns a Gemini client configured for Vertex AI.

    Args:
        project_id: The Google Cloud project ID.
        location: The Google Cloud location for the client.

    Returns:
        An initialized Gemini client.
    """
    return genai.Client(vertexai=True, project=project_id, location=location)

def generate_content(client: genai.Client, model_id: str, prompt: str, tools: List[Tool]):
    """
    Generates content using the Gemini API with a specified list of tools.

    This function provides a generic interface to the Gemini model, allowing for
    different capabilities like code execution or URL context to be passed dynamically.

    Args:
        client: The initialized Gemini client.
        model_id: The ID of the Gemini model to use (e.g., 'gemini-2.5-pro').
        prompt: The prompt to send to the model.
        tools: A list of tools for the model to use.

    Returns:
        The response object from the Gemini API.
    """
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=tools,
            temperature=0,
        ),
    )
    return response
