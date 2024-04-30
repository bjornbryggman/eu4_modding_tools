import replicate
import structlog
from pathlib import Path
from replicate.exceptions import ReplicateError
from requests import RequestException
from urllib.request import urlretrieve

log = structlog.stdlib.get_logger("./api/replicate_image_generation.py")

def upscale_images_via_replicate_api(
    input_directory: Path,
    output_directory: Path,
    input_format: str,
    replicate_upscaling_model: str,
):
    """
    Upscales PNG images using the Replicate API.

    Parameters:
    - input_directory: Path to the directory containing the PNG files to be upscaled.
    - output_directory: Path where the upscaled images will be stored.
    - api_key: API key for the Replicate API.

    Returns:
    - Upscaled PNG images.

    Raises:
    - RequestException: If a request to the Replicate API fails.
    - ReplicateError: If an error occurs with the Replicate API.
    - ValueError: If the API key or model is invalid.
    - TypeError: If the input data types are incorrect.
    - OSError: If an OS error occurs while processing the image.
    - Exception: If an unexpected error occurs.
    """

    try:

        for png_file in (input_directory.glob(f"*.{input_format}")):
            output_path = output_directory / png_file.name

            try:
                with open(png_file, "rb") as image_file:
                    output = replicate.run(
                        replicate_upscaling_model,
                        input={
                            "image": image_file,
                            "scale": 2,
                            "face_enhance": False,
                        },
                    )

                    output_url = output if isinstance(output, str) else output["url"]
                    urlretrieve(output_url, output_path)
                log.info(f"Upscaled {png_file} via the Replicate API.")

            except RequestException as e:
                log.error(f"Error: {e}. Request to the Replicate API failed.")
            except ReplicateError as e:
                log.error(f"Failed to upscale {png_file} due to an error with the Replicate API: {str(e)}")
            except ValueError as e:
                log.error(f"Invalid input when upscaling {png_file}: {str(e)}")
            except TypeError as e:
                log.error(f"Invalid data type when upscaling {png_file}: {str(e)}")
            except OSError as e:
                log.error(f"An I/O error occurred while upscaling {png_file}: {str(e)}")
            except Exception:
                raise Exception

    except Exception as e:
        log.error(f"An unexpected error occurred while upscaling {png_file}: {str(e)}")
