# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 80 characters).

Insert more descriptive explanation of the module here, max 3 rows,
max 100 characters per row (less is more, be concise and to the point).
"""

import re
from pathlib import Path

import structlog

from app.core.config import BaseConfig
from app.utils import file_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# Create config instances
base_config = BaseConfig()


def search_text_files(search_string: str, input_format: str, input_directory: Path, output_file: Path) -> None:
    """
    Searches through text files recursively for a given string using regex and logs matches.

    Process:
    -------
    -------
        - Recursively identifies all text files in the input directory.
        - Creates a regex pattern from the input search string.
        - Searches each file for matches using the regex pattern.
        - Writes matches to an output file, including file path and matched content.

    Args:
    ----
    ----
        - search_string (str): The string to search for in the text files.
        - input_directory (Path): The directory containing the files to be searched.
        - output_file (Path): The file where the search results will be written.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If the input directory doesn't exist.
        - PermissionError: If there are permission issues with reading files or writing to the output file.
        - Exception: For any other unexpected errors during the search process.
    """
    try:
        # Create a more flexible regex pattern
        pattern = re.compile(re.escape(search_string), re.IGNORECASE)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Ensure output_file is not a directory
        if output_file.is_dir():
            output_file = output_file / "search_results.txt"
            log.warning("Output file was a directory. Changed to: %s", output_file)

        with output_file.open("w", encoding="utf-8") as out_file:
            input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
            for input_file in input_files:
                content = file_utils.read_file(input_file)
                matches = pattern.findall(content)
                if matches:
                    out_file.write(f"File: {input_file}\n")
                    for match in matches:
                        out_file.write(f"Match: {match}\n")
                    out_file.write("\n")

        log.info("Search completed. Results written to %s.", output_file)

    except FileNotFoundError as error:
        log.exception("Input directory not found.", exc_info=error)
    except PermissionError as error:
        log.exception("Permission error.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


# Example usage


if __name__ == "__main__":
    search_text_files("GFX_expedition_ongoing_bg", "txt", base_config.input_dir, base_config.input_dir)
