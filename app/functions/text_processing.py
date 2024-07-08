# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides functionality for processing GUI files and scaling their positional values.

It includes a main function to process GUI files in a given directory, applying a scaling factor
to specific positional attributes.
"""

import re
import shutil
from pathlib import Path

import structlog

from app.utils.file_utils import read_file, write_file

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


def process_gui_files(input_directory: Path, output_directory: Path, input_format: str, scale_factor: float) -> None:
    """
    Processes GUI files and scales their relevant positional values according to a specified scaling factor.

    This function reads GUI files from the input directory, applies a scaling factor to specific
    positional attributes (x, y, maxWidth, maxHeight), and writes the modified content to the
    output directory.

    Args:
    ----
        input_directory (Path): The directory containing the GUI files to process.
        output_directory (Path): The directory to output processed files.
        input_format (str): The file extension of input GUI files (e.g., 'xml', 'ui').
        scale_factor (float): The scaling factor to apply to positional values.

    Returns:
    -------
        None

    Raises:
    ------
        PermissionError: If there's a permission issue when accessing files.
        ValueError: If there's an issue with value conversion during processing.
        re.error: If there's an error in the regular expression operations.
        OSError: If there's an operating system related error.
        Exception: For any other unexpected errors during processing.
    """
    log.info("Processing GUI files in %s with scale factor %s...", input_directory, scale_factor)

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
        prop, value = match.group(1), float(match.group(2))
        scaled_value = round(value * scale_factor)
        return f"{prop} = {scaled_value}"

    def process_content(content: str) -> str:
        """
        Scales values in the content according to the scaling factor.

        Args:
        ----
            content (str): The content of a GUI file.

        Returns:
        -------
            str: The content with scaled positional values.
        """
        # Regular expression to match positional properties and their values.
        pattern = r"(\bx\b|\by\b|maxWidth|maxHeight) *= *(-?\d+(?:\.\d+)?)"
        return re.sub(pattern, scale_value, content)

    try:
        # Iterate through all files with the specified format in the input directory.
        for gui_file in input_directory.rglob(f"*.{input_format.lower()}"):
            # Calculate the relative output path to maintain directory structure.
            relative_path = gui_file.relative_to(input_directory)
            output_path = output_directory / relative_path.parent
            output_path.mkdir(parents=True, exist_ok=True)

            # Copy the original file to the output directory.
            output_file = output_path / gui_file.name
            shutil.copy(gui_file, output_file)

            # Read the content of the copied file.
            content = read_file(output_file)

            # Process the content, scaling positional values.
            updated_content = process_content(content)

            # Write the updated content if changes were made.
            if content != updated_content:
                write_file(output_file, updated_content)
                log.debug("Updated %s with scaled values.", output_file.name)
            else:
                log.debug("No changes have been made to %s.", output_file.name)

        log.info("Positional values in GUI files have been successfully scaled.")

    except PermissionError as error:
        log.exception("Permission denied when accessing file: %s", gui_file, exc_info=error)
    except ValueError as error:
        log.exception("Value error occurred while processing file: %s", gui_file, exc_info=error)
    except re.error as error:
        log.exception("Regex error while processing file: %s", gui_file, exc_info=error)
    except OSError as error:
        log.exception("OS error while processing file: %s", gui_file, exc_info=error)
    except Exception as error:
        log.exception("Unexpected error while processing file: %s", gui_file, exc_info=error)
