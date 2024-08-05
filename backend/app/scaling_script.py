# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 60 characters).

Insert more descriptive explanation of the module here, max 4 rows, max 100 characters per row.
"""

import contextlib
from pathlib import Path

import structlog

from app.core.config import BaseConfig, ScalingConfig
from app.functions import image_processing, text_processing
from app.utils import file_utils, logging_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ============================================================= #
#                   Image Processing Workflow                   #
# ============================================================= #


# Directory configuration, see config.py for more information.
working_directories = [
    ScalingConfig.WORKING_DIR_DDS,
    ScalingConfig.WORKING_DIR_TGA,
    ScalingConfig.WORKING_DIR_DDS_TO_PNG,
    ScalingConfig.WORKING_DIR_DDS_4K,
    ScalingConfig.WORKING_DIR_DDS_2K,
    ScalingConfig.WORKING_DIR_TGA_TO_PNG,
    ScalingConfig.WORKING_DIR_TGA_4K,
    ScalingConfig.WORKING_DIR_TGA_2K,
]
output_directories = [BaseConfig.ERROR_DIR, ScalingConfig.OUTPUT_DIR_4K, ScalingConfig.OUTPUT_DIR_2K]


def process_images() -> None:
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """
    logging_utils.init_logger(BaseConfig.LOG_LEVEL, BaseConfig.LOG_DIR)
    log.info("Initiating image processing workflow...")

    # Delete any old files (except input files) before initiating workflow.
    for path in working_directories and output_directories:
        file_utils.delete_directory(path)
        file_utils.create_directory(path)

    # Unzip the contents of any potential .zip files.
    file_utils.unzip_files(BaseConfig.INPUT_DIR, BaseConfig.INPUT_DIR)

    # Convert DDS and TGA assets to PNG format.
    dds_or_tga_to_png_options = ["-y", "-wiclossless"]
    # Overwrites files and enables lossless conversion to PNG.
    image_processing.image_conversion(
        BaseConfig.INPUT_DIR,
        ScalingConfig.WORKING_DIR_DDS_TO_PNG,
        BaseConfig.ERROR_DIR,
        dds_or_tga_to_png_options,
        "DDS",
        "PNG",
    )
    image_processing.image_conversion(
        BaseConfig.INPUT_DIR,
        ScalingConfig.WORKING_DIR_TGA_TO_PNG,
        BaseConfig.ERROR_DIR,
        dds_or_tga_to_png_options,
        "TGA",
        "PNG",
    )

    # Resize DDS assets.
    image_processing.image_resizing(
        ScalingConfig.WORKING_DIR_DDS_TO_PNG, ScalingConfig.WORKING_DIR_DDS_4K, "PNG", 2.0, "SINC"
    )
    image_processing.image_resizing(
        ScalingConfig.WORKING_DIR_DDS_4K, ScalingConfig.WORKING_DIR_DDS_2K, "PNG", 0.6667, "SINC"
    )

    # Resize TGA assets.
    image_processing.image_resizing(
        ScalingConfig.WORKING_DIR_TGA_TO_PNG, ScalingConfig.WORKING_DIR_TGA_4K, "PNG", 2.0, "SINC"
    )
    image_processing.image_resizing(
        ScalingConfig.WORKING_DIR_TGA_4K, ScalingConfig.WORKING_DIR_TGA_2K, "PNG", 0.6667, "SINC"
    )

    # Convert PNG assets to DDS format.
    png_to_dds_options = ["-y", "-dx10"]
    # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        ScalingConfig.WORKING_DIR_DDS_4K,
        ScalingConfig.OUTPUT_DIR_4K,
        BaseConfig.ERROR_DIR,
        png_to_dds_options,
        "PNG",
        "DDS",
    )
    image_processing.image_conversion(
        ScalingConfig.WORKING_DIR_DDS_2K,
        ScalingConfig.OUTPUT_DIR_2K,
        BaseConfig.ERROR_DIR,
        png_to_dds_options,
        "PNG",
        "DDS",
    )

    # Convert PNG assets to TGA format.
    png_to_tga_options = ["-y", "-tga20"]
    # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        ScalingConfig.WORKING_DIR_TGA_4K,
        ScalingConfig.OUTPUT_DIR_4K,
        BaseConfig.ERROR_DIR,
        png_to_tga_options,
        "PNG",
        "TGA",
    )
    image_processing.image_conversion(
        ScalingConfig.WORKING_DIR_TGA_2K,
        ScalingConfig.OUTPUT_DIR_2K,
        BaseConfig.ERROR_DIR,
        png_to_tga_options,
        "PNG",
        "TGA",
    )

    # Delete working directories after finishing workflow.
    for path in working_directories:
        file_utils.delete_directory(path)

    # Removes error directory if empty.
    with contextlib.suppress(OSError):
        Path.rmdir(BaseConfig.ERROR_DIR)


# ============================================================ #
#                   Text Processing Workflow                   #
# ============================================================ #


# Used to derive an appropriate scaling factor by comparing how other mods
# (e.g., "Proper 2K UI") did it.
def text_positional_value_comparison() -> None:
    """
    Calculates proper scaling factors for each property in the text files.

    It compares original, 2K, and 4K versions of text files to determine
    the appropriate scaling factor for each property in each file.
    """
    logging_utils.init_logger(BaseConfig.LOG_LEVEL, BaseConfig.LOG_DIR)
    log.info("Initiating GUI comparison workflow...")

    # Compares positional values between text files.
    text_processing.calculate_scaling_factors(
        ScalingConfig.TEXT_COMPARISON_ORIGINAL_DIR,
        ScalingConfig.TEXT_COMPARISON_DIR_2K,
        ScalingConfig.TEXT_COMPARISON_DIR_4K,
        "GUI",
    )


def text_positional_value_scaling() -> None:
    """
    Scales positional values in text GUI files based.

    It retrieves the appropriate scaling factors from the database based
    on the resolution, then applies the scaling factors to the files and
    writes the scaled content to the output directory.
    """
    logging_utils.init_logger(BaseConfig.LOG_LEVEL, BaseConfig.LOG_DIR)
    log.info("Initiating GUI scaling workflow...")

    # Scale positional values in GUI text files (for 4K monitors).
    text_processing.scale_positional_values(BaseConfig.INPUT_DIR, ScalingConfig.OUTPUT_DIR_4K, "GUI", "4K")

    # Scale positional values GUI text files (for 2K monitors).
    text_processing.scale_positional_values(BaseConfig.INPUT_DIR, ScalingConfig.OUTPUT_DIR_2K, "GUI", "2K")


if __name__ == "__main__":
    process_images()
    log.info("Image processing workflow completed successfully.")
    text_positional_value_comparison()
    text_positional_value_scaling()
    log.info("Text processing workflow completed successfully.")
