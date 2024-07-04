# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

from pathlib import Path

import structlog
from wand.exceptions import CorruptImageError, FileOpenError, WandError
from wand.image import Image

from backend.api.replicate_image_generation import image_generation

log = structlog.stdlib.get_logger(__name__)

# ====================================================#
#          Functions for processing images            #
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
        OSError: If an I/O error occurs.
        Exception: If an unexpected error occurs.

    Returns:
    -------
        None.
    """
    try:
        log.debug(
            "Converting all %s files in %s to %s format...",
            input_format.upper(),
            input_directory,
            output_format.upper(),
        )

        for input_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / (input_file.stem + f".{output_format}")

            with Image(filename=str(input_file)) as img:
                img.format = output_format
                img.save(filename=str(output_path))
            log.debug("Converted %s to %s.", input_file.name, output_format.upper())
        log.debug(
            "Conversion complete. The converted %s files can be found in: %s", output_format.upper(), output_directory
        )

    except FileNotFoundError as error:
        log.exception("No images found in input directory.", exc_info=error)
    except FileOpenError as error:
        log.exception("Failed to open file.", exc_info=error)
    except CorruptImageError as error:
        log.exception("Corrupt image file.", exc_info=error)
    except WandError as error:
        log.exception("Wand library error occurred.", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


def upscale_images(
    input_directory: Path, output_directory: Path, input_format: str, replicate_upscaling_model: str
) -> None:
    """
    Upscales images using the Replicate API.

    This function takes in an input format, input & output directories, and a Replicate API upscaling model.
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
        OSError: If an I/O error occurs while processing the file.
        Exception: If an unexpected error occurs during the process execution.

    Returns:
    -------
        None.
    """
    try:
        log.debug("Upscaling all %s files in %s...", input_format.upper(), input_directory)
        for file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / file.name

            with Path.open(file, "rb") as image_file:
                input_params = {"image": image_file, "scale": 2, "face_enhance": False}
                image_generation(replicate_upscaling_model, input_params, output_path)
        log.debug(
            "Upscaling operation finished. The upscaled %s files can be found in: %s",
            input_format.upper(),
            output_directory,
        )

    except FileNotFoundError as error:
        log.exception("No images found in the input directory.", exc_info=error)
    except FileOpenError as error:
        log.exception("Failed to open file.", exc_info=error)
    except CorruptImageError as error:
        log.exception("Corrupt image file.", exc_info=error)
    except ValueError as error:
        log.exception("An invalid input parameter was provided.", exc_info=error)
    except OSError as error:
        log.exception("An I/O error occurred during the process execution.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred during the process execution.", exc_info=error)


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
        ValueError: If an invalid scaling factor is provided.
        OSError: If an I/O error occurs.
        Exception: If an unexpected error occurs.

    Returns:
    -------
        None.
    """
    try:
        log.debug("Resizing all %s files in %s by %s...", input_format.upper(), input_directory, scaling_factor)
        for upscaled_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / upscaled_file.name
            with Image(filename=str(upscaled_file)) as img:
                img.resize(int(img.width * scaling_factor), int(img.height * scaling_factor))
                img.save(filename=str(output_path))
            log.debug("Resized %s by a factor of %s", upscaled_file.name, scaling_factor)
        log.debug(
            "Resizing operation finished. The resized %s files can be found in %s.",
            input_format.upper(),
            output_directory,
        )

    except FileNotFoundError as error:
        log.exception("No images found in input directory.", exc_info=error)
    except FileOpenError as error:
        log.exception("Failed to open file.", exc_info=error)
    except CorruptImageError as error:
        log.exception("Corrupt image file.", exc_info=error)
    except WandError as error:
        log.exception("Wand library error occurred.", exc_info=error)
    except ValueError as error:
        log.exception("Invalid scaling factor.", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
