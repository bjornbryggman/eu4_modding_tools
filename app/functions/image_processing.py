# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

import shutil
import subprocess
import tempfile
from pathlib import Path

import structlog
from wand.exceptions import CorruptImageError, FileOpenError, WandError
from wand.image import FILTER_TYPES, Image

from app.api.replicate_image_generation import image_generation
from app.utils.checks import check_for_texconv_path, check_for_wand_package

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ====================================================#
#          Functions for converting images            #
# ====================================================#


def imagemagick_convert_images(
    input_directory: Path, output_directory: Path, error_directory: Path, input_format: str, output_format: str
) -> None:
    """
    Converts images from one format to another using Imagemagick (Wand implementation).

    Args:
    ----
        input_directory (Path): The directory containing the input images to convert.
        output_directory (Path): The directory where the converted images will be stored.
        error_directory (Path): The directory where problematic images will be copied.
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
    # Check if the Wand package is available.
    if not check_for_wand_package:
        return

    try:
        log.info(
            "Converting all %s files in %s to %s format...",
            input_format.upper(),
            input_directory,
            output_format.upper(),
        )

        # Iterate through all files with the specified format in the input directory.
        for input_file in input_directory.rglob(f"*.{input_format.lower()}"):

            try:
                # Calculate the relative output path to maintain directory structure.
                relative_path = input_file.relative_to(input_directory)
                output_path = output_directory / relative_path.parent
                output_path.mkdir(parents=True, exist_ok=True)

                # Convert the image using Wand.
                with Image(filename=str(input_file)) as img:
                    img.format = output_format
                    img.save(filename=str(output_path))

                log.debug("Successfully converted %s to %s.", input_file.name, output_format.upper())

            # Handle corrupted image files.
            except CorruptImageError as error:
                log.exception(
                    "Failed to read image file %s. It may be corrupted or in an unsupported format.",
                    input_file,
                    exc_info=error,
                )

                # Copy problematic file to error directory for manual processing.
                error_directory.mkdir(parents=True, exist_ok=True)
                error_path = error_directory / relative_path.parent
                error_path.mkdir(parents=True, exist_ok=True)
                shutil.copy(input_file, error_path)
                continue

        log.debug(
            "Conversion complete. The converted %s files can be found in: %s", output_format.upper(), output_directory
        )

    except FileNotFoundError as error:
        log.exception("No images found in input directory.", exc_info=error)
    except FileOpenError as error:
        log.exception("Failed to open file.", exc_info=error)
    except WandError as error:
        log.exception("Wand library error occurred.", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


def texconv_convert_images(
    input_directory: Path,
    output_directory: Path,
    error_directory: Path,
    command_options: list,
    input_format: str,
    output_format: str,
) -> None:
    """
    Converts images from one format to another using Texconv.

    Args:
    ----
        input_directory (Path): The directory containing the input images to convert.
        output_directory (Path): The directory where the converted images will be stored.
        error_directory (Path): The directory where potential problematic files will be copied.
        input_format (str): The format of the input images (e.g., "dds").
        output_format (str): The format of the output images (e.g., "png").

    Raises:
    ------
        FileNotFoundError: If no images are found in the input directory.
        subprocess.CalledProcessError: If Texconv encounters an error.
        OSError: If an I/O error occurs.
        Exception: If an unexpected error occurs.

    Returns:
    -------
        None.
    """
    # Check if Texconv is available.
    if not check_for_texconv_path:
        return

    try:
        log.info(
            "Converting all %s files in %s to %s format using Texconv...",
            input_format.upper(),
            input_directory,
            output_format.upper(),
        )

        # Iterate through all files with the specified format in the input directory.
        for input_file in input_directory.rglob(f"*.{input_format.lower()}"):

            try:
                # Calculate the relative output path to maintain directory structure.
                relative_path = input_file.relative_to(input_directory)
                output_path = output_directory / relative_path.parent
                output_path.mkdir(parents=True, exist_ok=True)

                # Construct Texconv command.
                texconv_command = [
                    "texconv",
                    *command_options,
                    "-ft",
                    output_format.lower(),  # Output file type.
                    "-o",
                    str(output_path),  # Output directory.
                    str(input_file),  # Input file.
                ]

                # Run Texconv command.
                subprocess.run(texconv_command, check=True, capture_output=True, text=True)
                log.debug("Successfully converted %s to %s.", input_file.name, output_format.upper())

            # Fallback to using Imagemagick in case of problems.
            except subprocess.CalledProcessError as error:
                log.exception(
                    "Texconv failed to convert %s. Attempting Imagemagick fallback.", input_file, exc_info=error
                )

                # Create a temporary directory.
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)

                    # Copy the problematic file to the temporary directory.
                    temp_file = temp_dir_path / input_file.name
                    shutil.copy(input_file, temp_file)

                    try:
                        # Call the Imagemagick function.
                        imagemagick_convert_images(
                            input_directory=temp_dir_path,
                            output_directory=output_path,
                            error_directory=error_directory,
                            input_format=input_format,
                            output_format=output_format,
                        )

                        log.debug("Imagemagick successfully converted %s.", input_file.name)

                    except Exception as error:
                        log.exception("Both Texconv and Imagemagick failed to convert %s.", input_file, exc_info=error)
                        continue

        log.debug(
            "Conversion complete. The converted %s files can be found in: %s", output_format.upper(), output_directory
        )

    except FileNotFoundError as error:
        log.exception("No images found in input directory.", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


# ====================================================#
#             Function for resizing images            #
# ====================================================#


def imagemagick_resize_images(
    input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float, chosen_filter: str
) -> None:
    """
    Resizes images according to a specified scaling factor using Imagemagick (Wand implementation).

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
    # Check if the Wand package is available.
    if not check_for_wand_package:
        return

    try:
        log.info(
            "Resizing all %s files in %s by %s, using the %s filter...",
            input_format.upper(),
            input_directory,
            scaling_factor,
            chosen_filter,
        )

        # Iterate through all files with the specified format in the input directory.
        for input_file in input_directory.rglob(f"*.{input_format.lower()}"):

            # Calculate the relative output path to maintain directory structure.
            relative_path = input_file.relative_to(input_directory)
            output_path = output_directory / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # # Open the image, resize it, and save it to the output path.
            with Image(filename=str(input_file)) as img:
                img.resize(
                    int(img.width * scaling_factor),
                    int(img.height * scaling_factor),
                    FILTER_TYPES.index(chosen_filter.lower()),
                )
                img.save(filename=str(output_path))

            log.debug("Successfully resized %s by a factor of %s.", input_file.name, scaling_factor)

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


# ========================================================================#
#         Function for processing images using the Replicate API          #
# ========================================================================#


def replicate_images(
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
        log.info("Upscaling all %s files in %s...", input_format.upper(), input_directory)

        for file in input_directory.glob(f"*.{input_format.lower()}"):
            output_path = output_directory / file.name

            with Path.open(file, "rb") as image_file:
                input_params = {"image": image_file, "scale": 2, "face_enhance": False}
                image_generation(replicate_upscaling_model, input_params, output_path)

            log.debug("Successfully upscaled %s.", file.name)

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
