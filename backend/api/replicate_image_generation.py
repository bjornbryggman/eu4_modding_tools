# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Replicate API client module.

Asynchronous client for interacting with OpenRouter models.
"""

import asyncio
from pathlib import Path
from urllib.request import urlretrieve

import replicate
import structlog
from replicate.exceptions import ReplicateError
from requests import RequestException

log = structlog.stdlib.get_logger(__name__)

# ====================================================#
#            Functions for image generation          #
# ====================================================#


def image_generation(image_model: str, input_params: dict, output_path: Path) -> None:
    """
    Generates or modifies an existing image using the Replicate API.

    Args:
    ----
    ----
        - image_model (str): The name of the image model to use.
        - input_params (dict): The input parameters for the image model.
        - output_path (Path): The output path for the generated image.

    Returns:
    -------
    -------
        - None.

    Raises:
    ------
    ------
        - RequestException: If an error occurs while making the request to the Replicate API.
        - ReplicateError: If an error occurs while interacting with the Replicate API.
        - ValueError: If an invalid input parameter is provided.
        - TypeError: If an invalid data type is provided.
        - OSError: If an I/O error occurs while processing the file.
        - Exception: If an unexpected error occurs during the process execution.
    """
    try:
        log.debug("Calling the Replicate API for processing...")
        output = replicate.run(image_model, input=input_params)

        output_url = output if isinstance(output, str) else output["url"]
        urlretrieve(output_url, output_path)
        log.debug(f"Replicate request successful: {output_url}.")

    except RequestException:
        log.exception("Request to the Replicate API failed.")
    except ReplicateError:
        log.exception("There was a problem with the Replicate API.")
    except ValueError:
        log.exception("An invalid input parameter was provided.")
    except TypeError:
        log.exception("An invalid data type was provided.")
    except OSError:
        log.exception("An I/O error occurred during the process execution.")
    except Exception:
        log.exception("An unexpected error occurred during the process execution.")


async def batch_image_generation(image_model: str, prompts: list[str], output_path: Path) -> None:
    """
    Generates batch images using the Replicate API.

    Args:
    ----
    ----
        - image_model (str): The name of the image model to use.
        - prompts (list[str]): A list of prompts for the image model.
        - output_path (Path): The output path for the generated images.

    Raises:
    ------
    ------
        - RequestException: If an error occurs while making the request to the Replicate API.
        - ReplicateError: If an error occurs while interacting with the Replicate API.
        - ValueError: If an invalid input parameter is provided.
        - TypeError: If an invalid data type is provided.
        - OSError: If an I/O error occurs while processing the file.
        - Exception: If an unexpected error occurs during the process execution.
    """
    try:
        log.debug("Calling the Replicate API for batch image generation...")
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(replicate.async_run(image_model, input={"prompt": prompt})) for prompt in prompts]
        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            output_url = result if isinstance(result, str) else result["url"]
            image_path = output_path / f"{i}.png"
            urlretrieve(output_url, image_path)
            log.debug(f"Image generated: {image_path}")

    except RequestException:
        log.exception("Request to the Replicate API failed.")
    except ReplicateError:
        log.exception("There was a problem with the Replicate API.")
    except ValueError:
        log.exception("An invalid input parameter was provided.")
    except TypeError:
        log.exception("An invalid data type was provided.")
    except OSError:
        log.exception("An I/O error occurred during the process execution.")
    except Exception:
        log.exception("An unexpected error occurred during the process execution.")


def replicate_pipeline(image_model: str, input_params: dict) -> bytes:
    """
    Runs a pipeline of Replicate API calls to process an image.

    Sort the list in ascending order and return a copy of the
    result using the bubble sort algorithm.

    Args:
    ----
        image_model (str): The name of the image model to use.
        input_params (dict): The input parameters for the image model.

    Raises:
    ------
        RequestException: If an error occurs while making the request to the Replicate API.
        ReplicateError: If an error occurs while interacting with the Replicate API.
        ValueError: If an invalid input parameter is provided.
        TypeError: If an invalid data type is provided.
        Exception: If an unexpected error occurs during the process execution.

    Returns:
    -------
        The processed image as bytes.
    """
    try:
        log.debug("Calling the Replicate API for processing...")
        laionide = replicate.models.get("afiaka87/laionide-v4").versions.get(
            "b21cbe271e65c1718f2999b038c18b45e21e4fba961181fbfae9342fc53b9e05"
        )
        swinir = replicate.models.get("jingyunliang/swinir").versions.get(
            "660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a"
        )
        image = laionide.predict(prompt="avocado armchair")
        upscaled_image = swinir.predict(image=image)
        log.debug("Replicate request successful.")

    except RequestException:
        log.exception("Request to the Replicate API failed.")
    except ReplicateError:
        log.exception("There was a problem with the Replicate API.")
    except ValueError:
        log.exception("An invalid input parameter was provided.")
    except TypeError:
        log.exception("An invalid data type was provided.")
    except Exception:
        log.exception("An unexpected error occurred during the process execution.")

    else:
        return upscaled_image
