# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This script converts image files from DDS to PNG format, then resizes and converts them back to DDS format.

It also adjusts any relevant positional values in GUI files by an appropriate scaling factor.
"""

import contextlib
import os
from pathlib import Path

import structlog
from dotenv import load_dotenv

from app.core.config import DirectoryConfig
from app.functions import image_processing, text_processing_backup
from app.utils import file_utils, logging_utils

log = structlog.stdlib.get_logger(__name__)

load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")
os.environ["OPENROUTER_API_TOKEN"] = os.getenv("OPENROUTER_API_KEY")
specific_model = os.getenv("OPENROUTER_TEXT_META_LLAMA-3_70B_NITRO")

# Directory configuration, see config.py for more information.
config = DirectoryConfig()
working_directories = [
    config.WORKING_DIR_DDS,
    config.WORKING_DIR_TGA,
    config.WORKING_DIR_DDS_TO_PNG,
    config.WORKING_DIR_DDS_4K,
    config.WORKING_DIR_DDS_2K,
    config.WORKING_DIR_TGA_TO_PNG,
    config.WORKING_DIR_TGA_4K,
    config.WORKING_DIR_TGA_2K,
]
output_directories = [config.ERROR_DIR, config.OUTPUT_DIR_4K, config.OUTPUT_DIR_2K]


def process_images() -> None:
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating image processing workflow...")

    # Delete any old files (except input files) before initiating workflow.
    for path in working_directories and output_directories:
        file_utils.delete_directory(path)
        file_utils.create_directory(path)

    # Unzip the contents of any potential .zip files.
    file_utils.unzip_files(config.INPUT_DIR, config.INPUT_DIR)

    # Convert DDS and TGA assets to PNG format.
    dds_or_tga_to_png_options = ["-y", "-wiclossless"]  # Overwrites files and enables lossless conversion to PNG.
    image_processing.image_conversion(
        config.INPUT_DIR, config.WORKING_DIR_DDS_TO_PNG, config.ERROR_DIR, dds_or_tga_to_png_options, "DDS", "PNG"
    )
    image_processing.image_conversion(
        config.INPUT_DIR, config.WORKING_DIR_TGA_TO_PNG, config.ERROR_DIR, dds_or_tga_to_png_options, "TGA", "PNG"
    )

    # Resize DDS assets.
    image_processing.image_resizing(config.WORKING_DIR_DDS_TO_PNG, config.WORKING_DIR_DDS_4K, "PNG", 2.0, "SINC")
    image_processing.image_resizing(config.WORKING_DIR_DDS_4K, config.WORKING_DIR_DDS_2K, "PNG", 0.6667, "SINC")

    # Resize TGA assets.
    image_processing.image_resizing(config.WORKING_DIR_TGA_TO_PNG, config.WORKING_DIR_TGA_4K, "PNG", 2.0, "SINC")
    image_processing.image_resizing(config.WORKING_DIR_TGA_4K, config.WORKING_DIR_TGA_2K, "PNG", 0.6667, "SINC")

    # Convert PNG assets to DDS format.
    png_to_dds_options = ["-y", "-dx10"]  # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        config.WORKING_DIR_DDS_4K, config.OUTPUT_DIR_4K, config.ERROR_DIR, png_to_dds_options, "PNG", "DDS"
    )
    image_processing.image_conversion(
        config.WORKING_DIR_DDS_2K, config.OUTPUT_DIR_2K, config.ERROR_DIR, png_to_dds_options, "PNG", "DDS"
    )

    # Convert PNG assets to TGA format.
    png_to_tga_options = ["-y", "-tga20"]  # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        config.WORKING_DIR_TGA_4K, config.OUTPUT_DIR_4K, config.ERROR_DIR, png_to_tga_options, "PNG", "TGA"
    )
    image_processing.image_conversion(
        config.WORKING_DIR_TGA_2K, config.OUTPUT_DIR_2K, config.ERROR_DIR, png_to_tga_options, "PNG", "TGA"
    )
    # Delete working directories after finishing workflow.
    for path in working_directories:
        file_utils.delete_directory(path)

    # Removes error directory if empty.
    with contextlib.suppress(OSError):
        Path.rmdir(config.ERROR_DIR)

    log.info("Image processing pipeline completed successfully.")


def text_positional_value_scaling() -> None:
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating text processing (scaling) workflow...")

    # Scale positional values in GUI and GFX text files (for 4K monitors).
    text_processing_backup.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_4K, "GUI", 1.4)
    text_processing_backup.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_4K, "GFX", 1.4)

    # Scale positional values in GUI and GFX text files (for 2K monitors).
    text_processing_backup.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_2K, "GUI", 1.2)
    text_processing_backup.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_2K, "GFX", 1.2)


# Used to derive an appropriate scaling factor by comparing how other mods (e.g., "Proper 2K UI") did it.
def text_positional_value_comparison() -> None:
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating text processing (scaling) workflow...")

    # Compares positional values between text files (for 4K monitors).
    text_processing_backup.calculate_scaling_factors(
        config.TEXT_COMPARISON_ORIGINAL_DIR, config.TEXT_COMPARISON_DIR_2K, config.TEXT_COMPARISON_DIR_4K, "GUI"
    )


if __name__ == "__main__":
    text_positional_value_comparison()
