# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides a client for interacting with the OpenRouter API.

It includes functions for making completion requests to the OpenRouter API and
querying the cost of those requests.
"""

import openai
import requests
import structlog
from openai import OpenAI

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ====================================================#
#                    Main function                    #
# ====================================================#


def completion_request(prompt: list[dict], model: str, api_key: str, stream: bool) -> tuple:
    """
    Makes a completion request to the OpenRouter API and returns the response.

    Args:
    ----
        - prompt (list[dict]): The input prompt for the completion request.
        - model (str): The name of the model to use for the completion request.
        - api_key (str): The API key for OpenRouter.
        - stream (bool): Whether to stream the output as chunks or not.

    Returns:
    -------
        - A tuple containing the response text and the cost of the API call.

    Raises:
    ------
        - openai.OpenAIError: If an error occurs while interacting
            with the OpenRouter model.
        - requests.RequestException: If an error occurs while making
            the request to the OpenRouter API.
        - ValueError: If an invalid input parameter is provided.
        - Exception: If an unexpected error occurs during the process execution.

    """
    try:
        log.debug("Calling the OpenRouter API...")

        # Make an asynchronous completion request using the OpenAI client.
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=prompt,
            stream=stream,
            max_tokens=500,
            extra_query={"transforms": {}, "min_p": {"value": 0.1}},
        )

        # Stream the output as chunks if stream = True.
        if stream:
            chunks = []
            for chunk in completion:
                if not hasattr(completion, "id"):
                    completion.id = chunk.id
                part = chunk.choices[0].delta.content
                chunks.append(part)
            cohesive_text = "".join(chunks)

        # Filter the response into a readable format.
        else:
            cohesive_text = completion.choices[0].message.content

        # Calculate the cost of the API call.
        cost_and_stats = query_cost_and_stats(completion.id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"

        log.debug("OpenRouter completion request successful: %s", completion)
        log.debug("Cost for API call: %s", formatted_string)

    except openai.OpenAIError as error:
        log.exception(
            "APIError occurred while interacting with the OpenRouter model.", exc_info=error
        )
    except requests.RequestException as error:
        log.exception("Request to the OpenRouter API failed.", exc_info=error)
    except ValueError as error:
        log.exception("Invalid input parameter provided.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred during the process execution.", exc_info=error)

    else:
        return (cohesive_text, formatted_string)


# ====================================================#
#                   Helper function                   #
# ====================================================#


def query_cost_and_stats(generation_id: str, api_key: str) -> dict:
    """
    Queries the cost for a given generation ID from OpenRouter.

    Args:
    ----
    ----
        - generation_id (str): The ID of the generation to query.
        - api_key (str): The API key for OpenRouter.

    Returns:
    -------
    -------
        - A dictionary containing the cost for the generation.

    Raises:
    ------
    ------
        - requests.RequestException: If an error occurs while making
            the request to the OpenRouter API.

    """
    # Construct the API URL with the generation ID.
    api_url = f"https://openrouter.ai/api/v1/generation?id={generation_id}"

    # Set up the headers with the API key.
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        # Make a GET request to the OpenRouter API.
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract the data from the JSON response.
        data = response.json().get("data")

    except requests.exceptions.RequestException:
        log.exception("HTTP Request to OpenRouter failed.")

    else:
        # Return a dictionary with the total cost.
        return {"total_cost": data.get("total_cost")}
