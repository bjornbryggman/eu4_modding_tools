# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides functions for image conversion and resizing using Texconv and Imagemagick.

This module offers two main functionalities: image conversion and resizing. It leverages
Texconv for image conversion, with Imagemagick as a fallback option. For resizing,
it utilizes the Imagemagick library (through the Wand package). The module utilizes
multiprocessing to speed up these operations by running them in parallel.
"""

import multiprocessing
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import structlog
from wand.exceptions import CorruptImageError, FileOpenError, WandError
from wand.image import FILTER_TYPES, Image

from app.utils.checks import check_for_texconv_path, check_for_wand_package

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# =================================================== #
#        Worker function for converting images        #
# =================================================== #


def image_conversion_worker(args: tuple) -> None:
    """
    Worker function for image conversion using Texconv.

    Process:
    -------
    -------
        - Calculates the relative output path to maintain directory structure.
        - Constructs and runs the Texconv command for image conversion.
        - If Texconv fails, attempts conversion using Imagemagick as a fallback.
        - If both conversion methods fail, copies the problematic file to an error directory.

    Args:
    ----
    ----
        - args (tuple): A tuple containing the following arguments:
            - input_file (Path): The input image file.
            - input_directory (Path): The directory containing the input images.
            - output_directory (Path): The directory where the converted images will be saved.
            - error_directory (Path): The directory where problematic files will be copied.
            - command_options (list): Additional options for the Texconv command.
            - output_format (str): The desired output format.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - subprocess.CalledProcessError: If Texconv encounters an error.
        - PermissionError: If there's a permission issue when accessing files.
        - FileOpenError: If an image cannot be opened.
        - WandError: If a Wand library error occurs.
        - OSError: If an I/O error occurs.
        - CorruptImageError: If the image file is corrupted or unreadable.
        - Exception: If an unexpected error occurs.
    """
    (input_file, input_directory, output_directory, error_directory, command_options, output_format) = args

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
        log.exception("Texconv failed to convert %s. Attempting Imagemagick fallback.", input_file, exc_info=error)

        try:
            # Convert the image using Imagemagick (Wand implementation).
            with Image(filename=str(input_file)) as img:
                img.format = output_format
                img.save(filename=str(output_path))
            log.debug("Successfully converted %s to %s using Imagemagick.", input_file.name, output_format.upper())

        # Copy problematic file to error directory for manual processing as a last resort.
        except CorruptImageError as error:
            log.exception("Failed to read image file %s.", input_file, exc_info=error)

            error_directory.mkdir(parents=True, exist_ok=True)
            error_path = error_directory / relative_path.parent
            error_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(input_file, error_path)

        except Exception as error:
            log.exception("Both Texconv and Imagemagick failed to convert %s.", input_file, exc_info=error)

    except PermissionError as error:
        log.exception("Permission denied when accessing file: %s", input_file, exc_info=error)
        sys.exit()
    except (FileOpenError, WandError, OSError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
    except Exception as error:
        log.exception("Unexpected error processing %s.", input_file, exc_info=error)


# ================================================= #
#        Worker function for resizing images        #
# ================================================= #


def image_resizing_worker(args: tuple) -> None:
    """
    Worker function for image resizing using Imagemagick.

    Process:
    -------
    -------
        - Extracts arguments from the provided tuple.
        - Calculates the relative output path to maintain directory structure.
        - Opens the input image using Wand library.
        - Resizes the image using the specified scaling factor and filter.
        - Saves the resized image to the output directory.

    Args:
    ----
    ----
        - args (tuple): A tuple containing the following arguments:
            - input_file (Path): The input image file.
            - input_directory (Path): The directory containing the input images.
            - output_directory (Path): The directory where the resized images will be saved.
            - scaling_factor (float): The factor by which images are resized.
            - chosen_filter (str): The filter to use for resizing.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - PermissionError: If there's a permission issue when accessing files.
        - CorruptImageError: If an image is corrupted.
        - FileOpenError: If an image cannot be opened.
        - WandError: If a Wand library error occurs.
        - OSError: If an I/O error occurs.
        - Exception: If an unexpected error occurs.

    """
    (input_file, input_directory, output_directory, scaling_factor, chosen_filter) = args

    try:
        # Calculate the relative output path to maintain directory structure.
        relative_path = input_file.relative_to(input_directory)
        output_path = output_directory / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Open the image, resize it, and save it to the output path.
        with Image(filename=str(input_file)) as img:
            img.resize(
                int(img.width * scaling_factor),
                int(img.height * scaling_factor),
                FILTER_TYPES.index(chosen_filter.lower()),
            )
            img.save(filename=str(output_path))

        log.debug("Successfully resized %s by a factor of %s.", input_file.name, scaling_factor)

    except PermissionError as error:
        log.exception("Permission denied when accessing file: %s", input_file, exc_info=error)
        sys.exit()
    except CorruptImageError as error:
        log.exception("Failed to read image file %s.", input_file, exc_info=error)
    except (FileOpenError, WandError, OSError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
    except Exception as error:
        log.exception("Unexpected error processing %s.", input_file, exc_info=error)


# =================================================== #
#        Caller function for converting images        #
# =================================================== #


def image_conversion(
    input_directory: Path,
    output_directory: Path,
    error_directory: Path,
    command_options: list,
    input_format: str,
    output_format: str,
) -> None:
    """
    Converts images between formats using Texconv, with Imagemagick as a fallback.

    Process:
    -------
    -------
        - Checks if Texconv is available.
        - Iterates through all input files in the input directory.
        - Uses a ProcessPoolExecutor to run the image_conversion_worker function in parallel for each file.

    Args:
    ----
    ----
        - input_directory (Path): The directory containing the input images to convert.
        - output_directory (Path): The directory where the converted images will be stored.
        - error_directory (Path): The directory where any problematic files will be copied.
        - command_options (list): Additional options for the Texconv command.
        - input_format (str): The format of the input images (e.g., "dds").
        - output_format (str): The format of the output images (e.g., "png").

    Returns:
    -------
    -------
        - None.

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If no images are found in the input directory.
        - Exception: If an unexpected error occurs.
    """
    if not check_for_texconv_path:
        return

    try:
        log.info(
            "Converting all %s files in %s to %s format...",
            input_format.upper(),
            input_directory,
            output_format.upper(),
        )

        # Use a ProcessPoolExecutor to run the worker function in parallel.
        input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [
                (input_file, input_directory, output_directory, error_directory, command_options, output_format)
                for input_file in input_files
            ]
            futures = list(executor.map(image_conversion_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions.
            for _ in futures:
                pass

    except FileNotFoundError as error:
        log.exception("No %s files found in %s.", input_format.upper(), input_directory, exc_info=error)
        sys.exit()
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


# =================================================== #
#         Caller function for resizing images         #
# =================================================== #


def image_resizing(
    input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float, chosen_filter: str
) -> None:
    """
    Resizes images according to a specified scaling factor using Imagemagick.

    Process:
    -------
    -------
        - Checks if the Wand package is available.
        - Iterates through all images in the input directory.
        - Uses a ProcessPoolExecutor to run the image_resizer_worker function in parallel for each image.

    Args:
    ----
    ----
        - input_directory (Path): The directory containing the images to be resized.
        - output_directory (Path): The directory where the resized images will be saved.
        - input_format (str): The file format of the images.
        - scaling_factor (float): The factor by which images are resized.
        - chosen_filter (str): The filter to use for resizing.

    Returns:
    -------
    -------
        - None.

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If no images are found in the input directory.
        - ValueError: If an invalid scaling factor is provided.
        - Exception: If an unexpected error occurs.
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

        # Use a ProcessPoolExecutor to run the worker function in parallel.
        input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [
                (input_file, input_directory, output_directory, scaling_factor, chosen_filter)
                for input_file in input_files
            ]
            futures = list(executor.map(image_resizing_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions.
            for _ in futures:
                pass

    except FileNotFoundError as error:
        log.exception("No %s files found in %s.", input_format.upper(), input_directory, exc_info=error)
        sys.exit()
    except ValueError as error:
        log.exception("'%s' is not a valid scaling factor.", scaling_factor, exc_info=error)
        sys.exit()
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
