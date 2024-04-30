import structlog
from litellm import validate_environment, completion, stream_chunk_builder, OpenAIError
from requests import RequestException

log = structlog.stdlib.get_logger("./api/litellm_text_generation.py")

def validate_environment_variables_for_litellm(specific_model: str):
    """
    Validates the environment variables for a given LiteLLM model.

    Args:
    - specific_model (str): The specific LiteLLM model to validate.
    - api_key (str): The API key for the LiteLLM model.

    Raises:
    - KeyError: If the environment variable for the specific model is missing.
    - ValueError: If the environment variable for the specific model is invalid.
    - OSError: If an operating system error occurs.
    - Exception: If an unexpected error occurs during the validation process.
    """

    try:
        env_validation = validate_environment(specific_model)
        if not env_validation["keys_in_environment"]:
            raise KeyError
        
    except KeyError as e:
        log.error(f"Error: {e}. Please set the environment variable for {specific_model}.")
    except ValueError as e:
        log.error(f"Error: {e}. Invalid environment variable for {specific_model}.")
    except OSError as e:
        log.error(f"Error: {e}. Operating system error occurred.")
    except Exception as e:
        log.error(f"Error: {e}. An unexpected error occurred during the validation process.")


def streaming_completion_response_via_litellm(role = str, content = str, specific_model = str):
    """
    Makes a completion request to a given LiteLLM language model and receives streaming output, which is then combined into a cohesive text.

    Args:
    - role (str): The role to which the content is assigned (e.g. "user" or "assistant").
    - content (str): The text input to process.
    - specific_model (str): The specific LiteLLM model to use for processing.
    - api_key (str): The API key for the LiteLLM model.

    Returns:
    - str: The final response from the LiteLLM model.

    Raises:
    - OpenAIError: If an error occurs while interacting with the LiteLLM model.
    - RequestException: If a request to the LiteLLM API fails.
    - ValueError: If an invalid input parameter is provided.
    - Exception: If an unexpected error occurs during the process execution.
    """
   
    try:
        messages = [{"role": role, "content": content}]

        try:
            log.debug("Calling litellm.completion(streaming=true)")
            response = completion(
                model=specific_model,
                messages=messages,
                stream=True,
            )

        except OpenAIError as e:
            log.error(f"Error: {e}. OpenAIError occurred while interacting with the LiteLLM model.")
        except RequestException as e:
            log.error(f"Error: {e}. Request to the LiteLLM API failed.")

        chunks = []
        for part in response:
            chunks.append(part)
            
        final_response = stream_chunk_builder(chunks, messages=messages)
        log.debug("litellm.completion() call successful. Final response: %s", final_response)

    except ValueError as e:
        log.error(f"Error: {e}. Invalid input parameter provided.")
    except Exception as e:
        log.error(f"Error: {e}. An unexpected error occurred during the process execution.")
