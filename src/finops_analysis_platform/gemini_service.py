import os
from google import genai
from google.genai.types import GenerateContentConfig, Tool, ToolCodeExecution

def initialize_gemini(project_id, location):
    """Initializes the Gemini client."""
    return genai.Client(vertexai=True, project=project_id, location=location)

def generate_with_code_execution(client, model_id, prompt):
    """
    Generates content with code execution using the Gemini API.

    Args:
        client: The Gemini client.
        model_id: The ID of the Gemini model to use.
        prompt: The prompt to send to the model.

    Returns:
        The response from the Gemini API.
    """
    code_execution_tool = Tool(code_execution=ToolCodeExecution())

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[code_execution_tool],
            temperature=0,
        ),
    )
    return response

def stream_with_code_execution(client, model_id, prompt):
    """
    Generates content with code execution in a streaming fashion.

    Args:
        client: The Gemini client.
        model_id: The ID of the Gemini model to use.
        prompt: The prompt to send to the model.

    Yields:
        Chunks of the response from the Gemini API.
    """
    code_execution_tool = Tool(code_execution=ToolCodeExecution())

    for chunk in client.models.generate_content_stream(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[code_execution_tool],
            temperature=0,
        ),
    ):
        yield chunk
