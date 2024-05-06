from pathlib import Path

import structlog
from wand.exceptions import CorruptImageError, FileOpenError, WandError
from wand.image import Image

from backend.api.replicate_image_generation import image_generation

log = structlog.stdlib.get_logger(__name__)

# ====================================================#
#          Functions for processing images           #
# ====================================================#


def convert_images(input_directory: Path, output_directory: Path, input_format: str, output_format: str) -> None:
    """
    Converts images from one format to another.

    Args:
    ----
        input_directory (Path): The directory containing the input images to convert.
        output_directory (Path): The directory where the converted images will be stored.
        input_format (str): The format of the input images (e.g., "dds", "png").
        output_format (str): The format of the output images (e.g., "png", "dds").

    Raises:
    ------
        FileNotFoundError: If no images are found in the input directory.
        FileOpenError: If an image cannot be opened.
        CorruptImageError: If an image is corrupted.
        WandError: If a Wand library error occurs.
        PermissionError: If permission is denied.
        OSError: If an I/O error occurs.
        Exception: If an unexpected error occurs.

    Returns:
    -------
        None.
    """
    try:
        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError(f"No {input_format.upper()} files found in the input directory.")

        log.debug(
            f"Converting all {input_format.upper()} files in {input_directory} to {output_format.upper()} format..."
        )
        for input_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / (input_file.stem + f".{output_format}")

            with Image(filename=str(input_file)) as img:
                img.format = output_format
                img.save(filename=str(output_path))
            log.debug(f"Converted {input_file.name} to {output_format.upper()}.")
        log.debug(
            f"Conversion completed. The converted {output_format.upper()} files and stored in {output_directory}."
        )

    except FileNotFoundError as error:
        log.error(f"Error: {error}. No images found in input directory.")
    except FileOpenError as error:
        log.error(f"Error: {error}. Failed to open file.")
    except CorruptImageError as error:
        log.error(f"Error: {error}. Corrupt image file.")
    except WandError as error:
        log.error(f"Error: {error}. Wand library error occurred.")
    except PermissionError as error:
        log.error(f"Error: {error}. Permission denied.")
    except OSError as error:
        log.error(f"Error: {error}. I/O error occurred.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred.")


def upscale_images(
    input_directory: Path, output_directory: Path, input_format: str, replicate_upscaling_model: str
) -> None:
    """
    Upscales images using the Replicate API.

    This function takes in a directory of images, an output directory, an input format, and a Replicate API upscaling model.
    It then uses the Replicate API to upscale the images and saves them to the output directory.

    Args:
    ----
        input_directory (Path): The directory containing the images to be upscaled.
        output_directory (Path): The directory where the upscaled images will be stored.
        input_format (str): The input image format.
        replicate_upscaling_model (str): The Replicate API upscaling model to use.

    Raises:
    ------
        FileNotFoundError: If no images are found in the input directory.
        FileOpenError: If an image cannot be opened.
        CorruptImageError: If an image is corrupted.
        ValueError: If an invalid input parameter is provided.
        TypeError: If an invalid data type is provided.
        OSError: If an I/O error occurs while processing the file.
        Exception: If an unexpected error occurs during the process execution.

    Returns:
    -------
        None.
    """
    try:
        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError("No images found in the input directory.")

        log.debug(f"Upscaling all {input_format.upper()} files in {input_directory}...")
        for file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / file.name

            with open(file, "rb") as image_file:
                input_params = {"image": image_file, "scale": 2, "face_enhance": False}
                image_generation(replicate_upscaling_model, input_params, output_path)
        log.debug(
            f"Upscaling operation finished. The upscaled {input_format.upper()} files can be found in {output_directory}."
        )

    except FileNotFoundError as error:
        log.error(f"Error: {error}. No images found in the input directory.")
    except FileOpenError as error:
        log.error(f"Error: {error}. Failed to open file.")
    except CorruptImageError as error:
        log.error(f"Error: {error}. Corrupt image file.")
    except ValueError as error:
        log.error(f"Error: {error}. An invalid input parameter was provided.")
    except TypeError as error:
        log.error(f"Error: {error}. An invalid data type was provided.")
    except OSError as error:
        log.error(f"Error: {error}. An I/O error occurred during the process execution.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred during the process execution.")


def resize_images(input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float) -> None:
    """
    Resizes images in the input directory with a specified scaling factor.

    Args:
    ----
        input_directory (Path): The directory containing the images to be resized.
        output_directory (Path): The directory where the resized images will be saved.
        input_format (str): The file format of the images.
        scaling_factor (float): The factor by which images are resized.

    Raises:
    ------
        FileNotFoundError: If no images are found in the input directory.
        FileOpenError: If an image cannot be opened.
        CorruptImageError: If an image is corrupted.
        WandError: If a Wand library error occurs.
        PermissionError: If permission is denied.
        ValueError: If an invalid scaling factor is provided.
        OSError: If an I/O error occurs.
        Exception: If an unexpected error occurs.

    Returns:
    -------
        None.
    """
    try:
        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError(f"No {input_format.upper()} files found in the input directory.")

        log.debug(f"Resizing all {input_format.upper()} files in {input_directory} by {scaling_factor}...")
        for upscaled_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / upscaled_file.name
            with Image(filename=str(upscaled_file)) as img:
                img.resize(int(img.width * scaling_factor), int(img.height * scaling_factor))
                img.save(filename=str(output_path))
            log.debug(f"Resized {upscaled_file.name} with a factor of {scaling_factor}")
        log.debug(f"Resizing completed. The resized {input_format.upper()} files can be found in {output_directory}.")

    except FileNotFoundError as error:
        log.error(f"Error: {error}. No images found in input directory.")
    except FileOpenError as error:
        log.error(f"Error: {error}. Failed to open file.")
    except CorruptImageError as error:
        log.error(f"Error: {error}. Corrupt image file.")
    except WandError as error:
        log.error(f"Error: {error}. Wand library error occurred.")
    except PermissionError as error:
        log.error(f"Error: {error}. Permission denied.")
    except ValueError as error:
        log.error(f"Error: {error}. Invalid scaling factor.")
    except OSError as error:
        log.error(f"Error: {error}. I/O error occurred.")
    except Exception as error:
        log.error(f"Error: {error}. An unexpected error occurred.")
