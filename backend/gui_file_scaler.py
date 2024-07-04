# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

import re
from pathlib import Path

import structlog

from backend.utils.file_utils import read_file, write_file

log = structlog.stdlib.get_logger(__name__)


class GUIScaler:
    """A class to scale the relevant positional information of GUI files according to a specific scaling factor."""

    def __init__(self, scale_factor: float) -> None:
        """
        Initializes the GUIFileScaler with the appropriate scaling factor.

        Args:
        ----
        - scale_factor: The scaling factor to apply.

        Returns:
        -------
        - None.
        """
        self.scale_factor = scale_factor

    def scale_value(self, match: re.match) -> str:
        """
        Scales a matched value according to the scaling factor.

        Args:
        ----
        - match: The regex match object containing the property name and value.

        Returns:
        -------
        - The scaled value as a string.
        """
        prop, value = match.group(1), float(match.group(2))
        scaled_value = round(value * self.scale_factor)
        return f"{prop} = {scaled_value}"

    def process_content(self, content: str) -> str:
        """
        Scales values in the content according to the scaling factor.

        Args:
        ----
        - content: The content of the GUI file to process.

        Returns:
        -------
        - The processed content with scaled values as a string.
        """
        pattern = r"(\bx\b|\by\b|maxWidth|maxHeight) *= *(-?\d+(?:\.\d+)?)"
        return re.sub(pattern, self.scale_value, content)


def process_gui_files(input_directory: Path, input_format: str, scale_factor: float) -> None:
    """
    Processes GUI files and scales their relevant positional values according to a specified scaling factor.

    Args:
    ----
    - input_directory: The input_directory containing the GUI files to process.
    - scale_factor: The scaling factor to apply.

    Returns:
    -------
    - None.
    """
    log.debug("Processing GUI files in %s with scale factor %s...", input_directory, scale_factor)
    scaler = GUIScaler(scale_factor)
    try:
        for file in input_directory.glob(f"*.{input_format}"):
            try:
                content = read_file(file)
                updated_content = scaler.process_content(content)

                if content != updated_content:
                    write_file(file, updated_content)
                    log.debug("Updated %s with scaled values.", file.name)
                else:
                    log.debug("No changes have been made to %s.", file.name)

            except re.error as error:
                log.exception("Regex error.", exc_info=error)
            except OSError as error:
                log.exception("OS error.", exc_info=error)
            except Exception as error:
                log.exception("Unexpected error.", exc_info=error)

    except FileNotFoundError as error:
        log.exception("File error.", exc_info=error)
