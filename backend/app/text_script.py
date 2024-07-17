# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Script for scaling GUI files.

This module provides functions for processing text files used in
graphical user interfaces (GUIs) to scale their positional values
for different resolutions.

It leverages comparison between original, 2K, and 4K versions of
text files to determine appropriate scaling factors.
"""

import structlog

from app.core.config import DirectoryConfig
from app.functions import text_processing
from app.utils import logging_utils

log = structlog.stdlib.get_logger(__name__)

# Directory configuration, see config.py for more information.
config = DirectoryConfig()


# Used to derive an appropriate scaling factor by comparing how other mods
# (e.g., "Proper 2K UI") did it.
def text_positional_value_comparison() -> None:
    """
    Calculates proper scaling factors for each property in the text files.

    It compares original, 2K, and 4K versions of text files to determine
    the appropriate scaling factor for each property in each file.
    """
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating text processing (scaling) workflow...")

    # Compares positional values between text files (for 4K monitors).
    text_processing.calculate_scaling_factors(
        config.TEXT_COMPARISON_ORIGINAL_DIR,
        config.TEXT_COMPARISON_DIR_2K,
        config.TEXT_COMPARISON_DIR_4K,
        "GUI",
    )


def text_positional_value_scaling() -> None:
    """
    Scales positional values in text GUI files based.

    It retrieves the appropriate scaling factors from the database based
    on the resolution, then applies the scaling factors to the files and
    writes the scaled content to the output directory.
    """
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating text processing (scaling) workflow...")

    # Scale positional values in GUI text files (for 4K monitors).
    text_processing.scale_positional_values(
        config.INPUT_DIR, config.OUTPUT_DIR_4K, "GUI", "4K"
    )

    # Scale positional values GUI text files (for 2K monitors).
    text_processing.scale_positional_values(
        config.INPUT_DIR, config.OUTPUT_DIR_2K, "GUI", "2K"
    )


if __name__ == "__main__":
    text_positional_value_comparison()
    text_positional_value_scaling()
