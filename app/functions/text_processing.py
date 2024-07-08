# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides functionality for processing text files and scaling their positional values.

It includes a main function to process text files in a given directory, applying a scaling factor
to specific positional attributes and utilizing multiprocessing to speed up operations.
"""

import multiprocessing
import re
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import structlog

from app.utils.file_utils import read_file, write_file

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ======================================================#
#        Worker function for parallel processing        #
# ======================================================#


def scale_positional_values_worker(args: tuple) -> None:
    """
    Worker function for scaling positional values in text files.

    Args:
    ----
    - args (tuple): A tuple containing the following arguments:
        - input_file (Path): The input GUI file.
        - input_directory (Path): The directory containing the input GUI files.
        - output_directory (Path): The directory to output processed files.
        - scale_factor (float): The scaling factor to apply to positional values.

    Returns:
    -------
    - None

    Raises:
    ------
    - PermissionError: If there's a permission issue when accessing files.
    - OSError: If there's an operating system related error.
    - Exception: For any other unexpected errors during processing.
    """
    input_file, input_directory, output_directory, scale_factor = args

    def scale_value(match: re.Match) -> str:
        """
        Scales a matched value according to the scaling factor.

        Args:
        ----
            match (re.Match): A regex match object containing the property and value.

        Returns:
        -------
            str: A string with the scaled value in the format "property = scaled_value".
        """
        prop = match.group(1)
        value = match.group(2).strip()

        if value.startswith("{"):
            # Handle complex size format, e.g.: size = {x = 5 y = 5}
            return f"{prop} = " + re.sub(
                r"(\w+)\s*=\s*(\d+(?:\.\d+)?)",
                lambda m: f"{m.group(1)} = {round(float(m.group(2)) * scale_factor)}",
                value,
            )

        # Handle simple size format, e.g.: size = 17
        scaled_value = round(float(value) * scale_factor)
        return f"{prop} = {scaled_value}"

    def process_content(content: str) -> str:
        """
        Scales specific values in the content according to the scaling factor.

        Args:
        ----
        - content (str): The content of a text file.

        Returns:
        -------
        - str: The content with scaled positional values.
        """
        pattern = (
            r"(\b(?:x|y|maxWidth|maxHeight|size|slotsize|borderSize|spacing|position)\b)\s*=\s*({[^}]+}|\d+(?:\.\d+)?)"
        )
        return re.sub(pattern, scale_value, content)

    try:
        # Calculate the relative output path to maintain directory structure.
        relative_path = input_file.relative_to(input_directory)
        output_path = output_directory / relative_path.parent
        output_path.mkdir(parents=True, exist_ok=True)

        # Copy the original file to the output directory.
        output_file = output_path / input_file.name
        shutil.copy(input_file, output_file)

        # Read the content of the copied file.
        content = read_file(output_file)
        if content is not None:
            # Process the content, scaling positional values.
            updated_content = process_content(content)
            if content != updated_content:
                write_file(output_file, updated_content)
                log.debug("Updated %s with scaled values.", output_file.name)
            else:
                log.debug("No changes have been made to %s.", output_file.name)

        else:
            # Skip to the next file if no content is found.
            log.error("No content found in file: %s", output_file)

    except PermissionError as error:
        log.exception("Permission denied when accessing file: %s", input_file, exc_info=error)
        sys.exit()
    except OSError as error:
        log.exception("OS error while processing file: %s", input_file, exc_info=error)
    except Exception as error:
        log.exception("Unexpected error while processing file: %s", input_file, exc_info=error)


# ====================================================#
#           Function for processing text files        #
# ====================================================#


def scale_positional_values(
    input_directory: Path, output_directory: Path, input_format: str, scale_factor: float
) -> None:
    """
    Scales relevant positional values in text files according to a specified scaling factor.

    This function reads text files from the input directory, applies a scaling factor to
    specific positional attributes, and writes the modified content to the output directory.

    Args:
    ----
    - input_directory (Path): The directory containing the GUI files to process.
    - output_directory (Path): The directory to output processed files.
    - input_format (str): The file extension of input GUI files (e.g., 'xml', 'ui').
    - scale_factor (float): The scaling factor to apply to positional values.

    Returns:
    -------
    - None

    Raises:
    ------
    - FileNotFoundError: If no images are found in the input directory.
    - ValueError: If an invalid scaling factor is provided.
    - Exception: If an unexpected error occurs.
    """
    log.info(
        "Scaling positional values in text files with a scale factor of %s...",
        scale_factor,
    )

    try:
        # Use a ProcessPoolExecutor to run the worker function in parallel.
        input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [
                (input_file, input_directory, output_directory, scale_factor)
                for input_file in input_files
            ]
            futures = list(executor.map(scale_positional_values_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions.
            for _ in futures:
                pass

    except FileNotFoundError as error:
        log.exception("No %s files found in %s.", input_format.upper(), input_directory, exc_info=error)
        sys.exit()
    except ValueError as error:
        log.exception("'%s' is not a valid scaling factor.", scale_factor, exc_info=error)
        sys.exit()
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
        raise

