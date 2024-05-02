import openai
import requests
import structlog
from openai import AsyncOpenAI

log = structlog.stdlib.get_logger(__name__)

#====================================================#
#                  Helper functions                  #
#====================================================#

def query_cost_and_stats_openrouter(generation_id=str, api_key=str):
    """
    Queries the cost for a given generation ID from OpenRouter.

    Args:
        generation_id (str): The ID of the generation to query.
        api_key (str): The API key for OpenRouter.

    Returns:
        A dictionary containing the cost for the generation.
    
    Raises:
        requests.RequestException: If an error occurs while making the request to the OpenRouter API.
    """
    api_url = f"https://openrouter.ai/api/v1/generation?id={generation_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data")

        return {"total_cost": data.get("total_cost")}
    
    except requests.exceptions.RequestException as error:
        log.error(f"Error: {error}. HTTP Request to OpenRouter failed.")
        return {}

#====================================================#
#        Functions for vision-based API calls        #
#====================================================#

async def vision_completion(role=str, text_content=str, specific_model=str, image=str, api_key=str):
    """
    Makes an asynchronous completion request to a given OpenRouter vision model using either a URL or a string of base64 encoded image data.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific OpenRouter model to use for processing.
        image (str): Either a URL to an image or a string of base64 encoded image data.
        api_key (str): The API key for OpenRouter, used for cost calculation.

    Returns:
        A tuple containing the final response from the OpenRouter model and the cost of the API call.

    Raises:
        openai.OpenAIError: If an error occurs while interacting with the OpenRouter model.
        requests.RequestException: If an error occurs while making the request to the OpenRouter API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling OpenRouter API for vision completion...")

        client = AsyncOpenAI()
        completion = await client.chat.completions.create(
            model=specific_model,
            messages=[{"role": role, "content": [{"type": "text", "text": text_content}, {"type": "image_url", "image_url": {"url": image}}]}],
            max_tokens=500,
            extra_query = {"transforms": {}, "min_p": {"value": 0.1}})
        filtered_text = completion.choices[0].message.content

        cost_and_stats = query_cost_and_stats_openrouter(completion.id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"

        log.debug(f"OpenRouter vision completion request successful: {completion}")
        log.debug(f"Cost for API call: {formatted_string}")

        return filtered_text, formatted_string

    except openai.APIError as error:
        log.error(f"Error: {error}. APIError occurred while interacting with the OpenRouter model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the OpenRouter API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")

#====================================================#
#         Functions for text-based API calls         #
#====================================================#

async def text_completion(role=str, text_content=str, specific_model=str, api_key=str, **kwargs):
    """
    Makes an asynchronous completion request to a given OpenRouter language model.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific OpenRouter model to use for processing.
        api_key (str): The API key for OpenRouter, used for cost calculation.

    Returns:
        A tuple containing the final response from the OpenRouter model and the cost of the API call.

    Raises:
        openai.APIError: If an error occurs while interacting with the OpenRouter model.
        requests.RequestException: If an error occurs while making the request to the OpenRouter API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling OpenRouter API for completion...")

        client = AsyncOpenAI()
        completion = await client.chat.completions.create(
            model=specific_model,
            messages=[{"role": role, "content": text_content}],
            max_tokens=500,
            extra_query = {"transforms": {}, "min_p": {"value": 0.1}})
        filtered_text = completion.choices[0].message.content

        cost_and_stats = query_cost_and_stats_openrouter(completion.id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"
        
        log.debug(f"OpenRouter completion request successful: {completion}")
        log.debug(f"Cost for API call: {formatted_string}")

        return filtered_text, formatted_string

    except openai.APIError as error:
        log.error(f"Error: {error}. APIError occurred while interacting with the OpenRouter model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the OpenRouter API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")


async def streaming_text_completion(role: str, text_content: str, specific_model: str, api_key: str):
    """
    Makes an asynchronous completion request to a given OpenRouter language model and receives streaming output, which is then combined into a cohesive text at the end.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        model (str): The specific OpenRouter model to use for processing.
        api_key (str): The API key for OpenRouter, used for cost calculation.

    Returns:
        A tuple containing the final response from the OpenRouter model and the cost of the API call.

    Raises:
        openai.OpenAIError: If an error occurs while interacting with the OpenRouter model.
        requests.RequestException: If an error occurs while making the request to the OpenRouter API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling OpenRouter API for completion...")
        log.debug(f"Model: {specific_model}, Role: {role}, Text Content: {text_content}")

        client = AsyncOpenAI()
        completion = await client.chat.completions.create(
            model=specific_model,
            messages=[{"role": role, "content": text_content}],
            stream=True,
            max_tokens=500,
            extra_query={"transforms": {}, "min_p": {"value": 0.1}})

        chunks = []
        async for chunk in completion:
            if not hasattr(completion, 'id'):
                completion.id = chunk.id
            part = chunk.choices[0].delta.content
            chunks.append(part)
        cohesive_text = "".join(chunks)

        cost_and_stats = query_cost_and_stats_openrouter(completion.id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"

        log.debug(f"OpenRouter completion request successful: {chunks}")
        log.debug(f"Cost for API call: {formatted_string}")

        return cohesive_text, formatted_string

    except openai.OpenAIError as error:
        log.error(f"Error: {error}. APIError occurred while interacting with the OpenRouter model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the OpenRouter API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")