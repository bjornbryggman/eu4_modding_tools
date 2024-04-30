import replicate
import structlog
from pathlib import Path
from replicate.exceptions import ReplicateError
from requests import RequestException
from urllib.request import urlretrieve

log = structlog.stdlib.get_logger(__name__)

def upscale_images(
    input_directory: Path,
    output_directory: Path,
    input_format: str,
    replicate_upscaling_model: str,
):
    """
    Upscales images using the Replicate API.

    Args:
    - input_directory: Path to the directory containing the images to be upscaled.
    - output_directory: Path where the upscaled images will be stored.
    - api_key: API key for the Replicate API.

    Returns:
    - Upscaled PNG images.
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

            except RequestException as error:
                log.error(f"Error: {error}. Request to the Replicate API failed.")
            except ReplicateError as error:
                log.error(f"Failed to upscale {png_file} due to an error with the Replicate API: {error}")
            except ValueError as error:
                log.error(f"Invalid input when upscaling {png_file}: {str(error)}")
            except TypeError as error:
                log.error(f"Invalid data type when upscaling {png_file}: {str(error)}")
            except OSError as error:
                log.error(f"An I/O error occurred while upscaling {png_file}: {str(error)}")

    except Exception as error:
        log.error(f"An unexpected error occurred while upscaling {png_file}: {str(error)}")
