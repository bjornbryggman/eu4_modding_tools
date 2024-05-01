import base64
import httpx
import litellm
import requests
import structlog


log = structlog.stdlib.get_logger(__name__)

#======================================================#
#                   Helper functions                   #
#======================================================#

def validate_environment_variables(specific_model: str):
    """
    Validates the environment variables for a given LiteLLM model.

    Args:
        specific_model (str): The specific LiteLLM model to validate.

    Raises:
        KeyError: If the environment variable for the model is not set.
        ValueError: If the environment variable for the model is invalid.
        OSError: If an operating system error occurs.
    """
    try:
        env_validation = litellm.validate_environment(specific_model)
        if not env_validation["keys_in_environment"]:
            raise KeyError
        
    except KeyError as error:
        log.error(f"Error: {error}. Please set the environment variable for {specific_model}.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid environment variable for {specific_model}.")
    except OSError as error:
        log.error(f"Error: {error}. Operating system error occurred.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the validation process.")

def query_cost_and_stats_openrouter(generation_id, api_key):
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
#         Functions for text-based API calls         #
#====================================================#

def text_completion_call(role = str, text_content = str, specific_model = str, api_key = str):
    """
    Makes a completion request to a given LiteLLM language model.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A tuple containing the final response from the LiteLLM model and the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling litellm.completion()")

        messages = [{"role": role, "content": [{"type": "text", "text": text_content}]}]
        response = litellm.completion(model=specific_model, messages=messages, transforms = [""], response_format = {"type": "json_object"})
        text = response.choices[0].message.content
        
        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"
        
        log.debug(f"litellm.completion() call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")    
        return text, formatted_string
        
    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")


def streaming_text_completion_call(role = str, text_content = str, specific_model = str, api_key = str):
    """
    Makes a completion request to a given LiteLLM language model and receives streaming output, which is then combined into a cohesive text at the end.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A streaming output and a tuple containing the final response from the LiteLLM model, as well as the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling litellm.completions(stream=true)")

        messages = [{"role": role, "content": text_content}]
        response = litellm.completion(model=specific_model, messages=messages, transforms = [""], stream=True)

        chunks = []
        streaming_output = ""

        for part in response:
            if "choices" in part and part["choices"]:
                for choice in part["choices"]:
                    if "delta" in choice and choice["delta"] and "content" in choice["delta"]:
                        readable_chunk = choice["delta"]["content"]
                        if readable_chunk is not None:
                            chunks.append(readable_chunk)
                            streaming_output += f" {readable_chunk}"   

        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"

        final_response = "".join(chunks)
        
        log.debug(f"litellm.completion(stream=true) call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")       
        return final_response, formatted_string

    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")


#===============================================================#
#        Functions for asynchronous text-based API calls        #
#===============================================================#

async def async_text_completion_call(role = str, text_content = str, specific_model = str, api_key = str):
    """
    Makes an asynchronous completion request to a given LiteLLM language model.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A tuple containing the final response from the LiteLLM model and the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling async litellm.completion()")

        messages = [{"role": role, "content": [{"type": "text", "text": text_content}]}]
        response = await litellm.acompletion(model=specific_model, messages=messages, transforms = [""])
        text = response.choices[0].message.content
        
        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"
        
        log.debug(f"Async litellm.completion() call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")    
        return text, formatted_string
        
    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")

async def async_streaming_text_completion_call(role = str, text_content = str, specific_model = str, api_key = str):
    """
    Makes an asynchronous completion request to a given LiteLLM language model and receives streaming output, which is then combined into a cohesive text at the end.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A streaming output and a tuple containing the final response from the LiteLLM model, as well as the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling async litellm.completion(streaming=true)")

        messages = [{"role": role, "content": text_content}]
        response = await litellm.acompletion(model=specific_model, messages=messages, transforms = [""], stream=True)

        chunks = []
        streaming_output = ""

        async for part in response:
            if "choices" in part and part["choices"]:
                for choice in part["choices"]:
                    if "delta" in choice and choice["delta"] and "content" in choice["delta"]:
                        readable_chunk = choice["delta"]["content"]
                        if readable_chunk is not None:
                            chunks.append(readable_chunk)
                            streaming_output += f" {readable_chunk}"   

        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"

        final_response = "".join(chunks)     
        
        log.debug(f"Async litellm.completion(stream=true) call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")       
        return final_response, formatted_string

    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")

#==================================================#
#       Functions for vision-based API calls       #
#==================================================#

def local_vision_completion_call(role=str, base64_string=str, image_format=str, text_content=str, specific_model=str, api_key=str):
    """
    Makes a completion request to a given LiteLLM language model using a local image.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        base64_string (str): The base64 encoded image string.
        image_format (str): The format of the image (e.g. "png" or "jpg").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A tuple containing the final response from the LiteLLM model and the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling litellm.completion(vision)")

        messages = [
            {"role": role,
                "content": [
                    {"type": "image", "source": { "type": "base64", "media_type": f"image/{image_format}", "data": base64_string},},
                    {"type": "text", "text": text_content}
                ]
            }
        ]
        response = litellm.completion(model=specific_model, messages=messages, transforms = [""])

        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"
        
        log.debug(f"litellm.completion(vision) call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")    
        return response, formatted_string
    
    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")

def url_vision_completion_call(role=str, image_url=str, image_format=str, text_content=str, specific_model=str, api_key=str):
    """
    Makes a completion request to a given LiteLLM language model using a URL-based image.

    Args:
        role (str): The role to which the content is assigned (e.g. "user" or "assistant").
        image_url (str): The URL of the image.
        image_format (str): The format of the image (e.g. "png" or "jpg").
        text_content (str): The text input to process.
        specific_model (str): The specific LiteLLM model to use for processing.
        api_key (str): The API key for OpenRouter.

    Returns:
        A tuple containing the final response from the LiteLLM model and the cost of the API call.

    Raises:
        litellm.OpenAIError: If an error occurs while interacting with the LiteLLM model.
        requests.RequestException: If an error occurs while making the request to the LiteLLM API.
        ValueError: If an invalid input parameter is provided.
    """
    try:
        log.debug("Calling litellm.completion(vision)")

        IMAGE_DATA = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
        messages = [
            {
                "role": role,
                "content": [
                    {"type": "image", "source": { "type": "base64", "media_type": f"image/{image_format}", "data": IMAGE_DATA},},
                    {"type": "text", "text": text_content},
                ],
            }
        ]
        response = litellm.completion(model=specific_model, messages=messages, transforms = [""])

        generation_id = response.get("id")
        cost_and_stats = query_cost_and_stats_openrouter(generation_id, api_key)
        total_cost = cost_and_stats.get("total_cost")
        formatted_string = f"${float(total_cost):.10f}"
        
        log.debug(f"litellm.completion(vision) call successful: {response}")
        log.debug(f"Cost for API call: {formatted_string}")    
        return response, formatted_string
   
    except litellm.OpenAIError as error:
        log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
    except requests.RequestException as error:
        log.error(f"Error: {error}. Request to the LiteLLM API failed.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")
