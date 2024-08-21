# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides functions for scaling positional values in text files.

This module offers utilities for scaling positional values (e.g., x, y, width, height)
in text files based on a specified scaling factor. It uses regular expressions to identify
and modify these values, and leverages multiprocessing for parallel processing to improve performance.
"""

import multiprocessing
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import structlog

from app.utils import file_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# =============================== #
#        Utility Functions        #
# =============================== #


def apply_scaling_factors(pattern: re, content: str, scaling_factor: str) -> str:
    """
    Apply scaling factors to positional values within text content.

    Process:
    -------
    -------
        - Applies a scaling factor to positional values in the content that match the given pattern.
        - Uses a replacer function to scale individual matches.

    Args:
    ----
    ----
        - pattern (re): A compiled regular expression pattern to match positional values.
        - content (str): The text content to apply scaling to.
        - scaling_factor (str): The factor by which to scale the matched values.

    Returns:
    -------
    -------
        - str: The updated content with scaled values, or the original content if an error occurs.

    Exceptions:
    ----------
    ----------
        - ValueError: If an invalid scaling factor is provided.
        - Exception: For any other unexpected errors during the scaling process.
    """
    try:
        # Apply scaling to content
        def replacer(match: re.Match) -> str:
            return scale_values(match, scaling_factor)

        updated_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)

    # Return original content if an error occurs
    except ValueError as error:
        log.exception("Invalid scaling factor provided.", exc_info=error)
        return content
    except Exception as error:
        log.exception("An unexpected error occurred while applying scaling factors.", exc_info=error)
        return content

    return updated_content


def scale_values(match: re.Match, scale_factor: float) -> str:
    """
    Scales a matched value according to the scaling factor.

    Process:
    -------
    -------
        - Extracts the property and value from the regex match.
        - Handles special cases (percentages, '@', '10s', '-1').
        - Scales complex size formats (e.g., {x = 5 y = 5}).
        - Scales simple numeric values.

    Args:
    ----
    ----
        - match (re.Match): A regex match object containing the property and value to scale.
        - scale_factor (float): The factor by which to scale the value.

    Returns:
    -------
    -------
        - str: A string representation of the scaled property and value.

    Exceptions:
    ----------
    ----------
        - ValueError: If the value cannot be converted to a float for scaling.
    """
    try:
        prop = match.group(1)
        value = match.group(2).strip()

        # Return the original string if value contains '%', '@', '10s', is "-1", or if scale_factor is None
        if any(x in value for x in ["%", "@", "10s"]) or value == "-1" or scale_factor is None:
            return f"{prop} = {value}"

        # Handle complex size format, e.g.: size = {x = 5 y = 5}
        if value.startswith("{"):
            return f"{prop} = " + re.sub(
                r"([\w_]+)\s*=\s*(-?\d+(?:\.\d+)?)",
                lambda m: f"{m.group(1)} = {
                    m.group(2)
                    if m.group(2) == "-1" or any(x in m.group(2) for x in ["%", "@", "10s"])
                    else round(float(m.group(2)) * scale_factor)
                }",
                value,
            )

        # Check if the value is numeric, return original if not
        if not value.replace(".", "", 1).replace("-", "", 1).isdigit():
            return f"{prop} = {value}"

        # Handle simple size format, e.g.: size = 17
        scaled_value = round(float(value) * scale_factor)

    except ValueError:
        log.exception("Value error occured during scaling.")
        raise
    else:
        return f"{prop} = {scaled_value}"


# =========================== #
#        Worker Function      #
# =========================== #


def scale_positional_values_worker(args: tuple[Path, Path, Path, str]) -> None:
    """
    Scales positional values in a text file based on a specified scaling factor.

    Process:
    -------
    -------
        - Reads the content of the input file.
        - Applies a specified scaling factor to positional values.
        - Writes the scaled content to the output file if changes were made.
        - Maintains the directory structure in the output.

    Args:
    ----
    ----
        - args (tuple[Path, Path, Path, str]): A tuple containing the input directory, output directory,
          input file path, and scaling factor.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: If an error occurs during file processing or scaling.
    """
    input_directory, output_directory, input_file, scaling_factor = args
    pattern = r"(\b(?:x|y|width|height|maxWidth|maxHeight|size|borderSize|spacing|position|pos_x)\b)\s*=\s*({[^}]+}|-?\d+(?:\.\d+)?%?|[^}\n]+)"

    try:
        # Read the content of a file
        content = file_utils.read_file(input_file)

        if content is not None:
            # Apply scaling factors to the content and return the updated content
            scaled_content = apply_scaling_factors(pattern, content, scaling_factor)

            if scaled_content != content:
                # Calculate the relative output path to maintain directory structure
                relative_path = input_file.relative_to(input_directory)
                output_path = output_directory / relative_path.parent

                # Write the scaled content to the output file
                output_path.mkdir(parents=True, exist_ok=True)
                output_file = output_path / input_file.name
                file_utils.write_file(output_file, scaled_content)
                log.debug("Updated %s with scaled values.", output_file.name)

            else:
                log.debug(" No changes have been made to %s.", input_file.name)

        else:
            # Skip to the next file if no content is found
            log.error("No content found in file: %s", input_file)

    except Exception as error:
        log.exception("An unexpected error occurred while scaling file: %s", input_file, exc_info=error)
        raise


# =========================== #
#        Caller Function      #
# =========================== #


def scale_positional_values(
    input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float
) -> None:
    """
    Scales positional values in text files according to a specified scaling factor.

    Process:
    -------
    -------
        - Identifies all files of the specified format in the input directory.
        - Uses a ProcessPoolExecutor to parallelize the scaling process.
        - Applies scaling to each file using the scale_positional_values_worker function.
        - Handles exceptions and logs errors if they occur.

    Args:
    ----
    ----
        - input_directory (Path): The directory containing the files to be processed.
        - output_directory (Path): The directory where the processed files will be saved.
        - input_format (str): The file format of the input files.
        - scaling_factor (float): The factor by which to scale the positional values.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If no files of the specified format are found in the input directory.
        - ValueError: If an invalid scaling factor is provided.
        - Exception: For any other unexpected errors during the scaling process.
    """
    log.info("Scaling positional values in %s files with a factor of %s.", input_format, scaling_factor)

    try:
        # Use a ProcessPoolExecutor to run the worker function in parallel
        input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [(input_directory, output_directory, input_file, scaling_factor) for input_file in input_files]
            results = list(executor.map(scale_positional_values_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions
            for _ in results:
                pass

    except FileNotFoundError as error:
        log.exception("No %s files found in %s.", input_format.upper(), input_directory, exc_info=error)
        sys.exit()
    except ValueError as error:
        log.exception("Value error, check the scaling factor.", exc_info=error)
        sys.exit()
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
