# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Replicate API client module.

Asynchronous client for interacting with OpenRouter models.
"""

import replicate
import structlog
from replicate.exceptions import ReplicateError
from requests import RequestException

log = structlog.stdlib.get_logger(__name__)


# ====================================================#
#                    Main function                    #
# ====================================================#


async def image_generation(image_model: str, input_params: dict) -> str:
    """
    Generates or modifies an existing image using the Replicate API.

    Args:
    ----
    ----
        - image_model (str): The name of the image model to use.
        - input_params (dict): The input parameters for the image model.

    Returns:
    -------
    -------
        - str: The URL of the generated or modified image.

    Raises:
    ------
    ------
        - RequestException: If an error occurs while making the API request.
        - ReplicateError: If an error occurs while interacting with the API.
        - ValueError: If an invalid input parameter is provided.
        - TypeError: If an invalid data type is provided.
        - OSError: If an I/O error occurs while processing the file.
        - Exception: If an unexpected error occurs during the process execution.

    """
    try:
        log.debug("Calling the Replicate API...")

        # Make an asynchronous API call.
        output = await replicate.async_run(image_model, input=input_params)

        # Extract the URL from the output.
        output_url = output if isinstance(output, str) else output["url"]

        log.debug("Replicate request successful: %s.", output_url)

    except RequestException as error:
        log.exception("HTTP Request to Replicate failed.", exc_info=error)
    except ReplicateError as error:
        log.exception("There was a problem with the Replicate API.", exc_info=error)
    except ValueError as error:
        log.exception("Invalid input parameter provided.", exc_info=error)
    except TypeError as error:
        log.exception("Invalid data type provided.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred during the process execution.", exc_info=error)

    else:
        if not output_url.startswith(("http:", "https:")):
            raise ValueError

        return output_url
