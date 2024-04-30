import structlog
from litellm import validate_environment, completion, stream_chunk_builder, OpenAIError
from requests import RequestException

log = structlog.stdlib.get_logger(__name__)

def validate_environment_variables_for_litellm(specific_model: str):
    """
    Validates the environment variables for a given LiteLLM model.

    Args:
    - specific_model (str): The specific LiteLLM model to validate.
    - api_key (str): The API key for the LiteLLM model.
    """
    try:
        env_validation = validate_environment(specific_model)
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

        except OpenAIError as error:
            log.error(f"Error: {error}. OpenAIError occurred while interacting with the LiteLLM model.")
        except RequestException as error:
            log.error(f"Error: {error}. Request to the LiteLLM API failed.")

        chunks = []
        for part in response:
            chunks.append(part)
            
        final_response = stream_chunk_builder(chunks, messages=messages)
        log.debug("litellm.completion() call successful. Final response: %s", final_response)

    except ValueError as error:
        log.error(f"Error: {error}. Invalid input parameter provided.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")
