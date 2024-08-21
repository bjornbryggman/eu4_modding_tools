# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Scales game assets for different resolutions.

This script automates the process of scaling game assets (images and GUI files)
for different resolutions. It utilizes the functions from the 'image_processing'
and 'text_processing' modules to perform image conversion, resizing, and scaling
of positional values in GUI files.
"""

import contextlib
from pathlib import Path

import structlog

from app.core.config import BaseConfig, ScalingConfig
from app.functions import image_processing, text_processing
from app.utils import file_utils, logging_utils

# Initialize logger for this module
log = structlog.stdlib.get_logger(__name__)

# Create config instances
base_config = BaseConfig()
scaling_config = ScalingConfig()

# =========================================== #
#           Directory Configuration           #
# =========================================== #


# See '/app/core/config.py' for more information
working_directories = [
    scaling_config.working_dir_dds,
    scaling_config.working_dir_tga,
    scaling_config.working_dir_dds_to_png,
    scaling_config.working_dir_dds_4k,
    scaling_config.working_dir_dds_2k,
    scaling_config.working_dir_tga_to_png,
    scaling_config.working_dir_tga_4k,
    scaling_config.working_dir_tga_2k,
]
output_directories = [base_config.error_dir, scaling_config.output_dir_4k, scaling_config.output_dir_2k]


# ===================================================== #
#           1080p -> 1440p -> 2160p  Workflow           #
# ===================================================== #


def fullhd_to_quadhd_to_ultrahd() -> None:
    """
    Scales game assets from 1080p to 1440p and 2160p resolutions.

    Process:
    -------
    -------
        - Deletes any old files (except input files) before initiating workflow.
        - Unzips the contents of any potential .zip files.
        - Converts DDS and TGA assets to PNG format.
        - Upscales 1080p DDS and TGA assets to 2160p.
        - Downscales 2160p DDS and TGA assets to 1440p.
        - Converts 2160p and 1440p PNG assets to DDS and TGA format.
        - Scales positional values in GUI text files (1080p -> 2160p and 1080p -> 1440p).
        - Deletes working directories after finishing workflow.
        - Removes empty directories.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - None.

    Exceptions:
    ----------
    ----------
        - Exception: If an unexpected error occurs during the workflow.
    """
    log.info("Initiating image processing workflow...")

    # Delete any old files (except input files) before initiating workflow
    for path in working_directories + output_directories:
        file_utils.delete_directory(path)
        file_utils.create_directory(path)

    # Unzip the contents of any potential .zip files
    file_utils.unzip_files(base_config.input_dir, base_config.input_dir)

    # Convert DDS assets to PNG format
    dds_or_tga_to_png_options = ["-y", "-wiclossless"]
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_dds_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "DDS",
        "PNG",
    )

    # Convert TGA assets to PNG format
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_tga_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "TGA",
        "PNG",
    )

    # Upscale 1080p DDS assets to 2160p
    image_processing.image_resizing(
        scaling_config.working_dir_dds_to_png, scaling_config.working_dir_dds_4k, "PNG", 2.0, "SINC"
    )

    # Downscale 2160p DDS assets to 1440p
    image_processing.image_resizing(
        scaling_config.working_dir_dds_4k, scaling_config.working_dir_dds_2k, "PNG", 0.6, "SINC"
    )

    # Upscale 1080p TGA assets to 2160p
    image_processing.image_resizing(
        scaling_config.working_dir_tga_to_png, scaling_config.working_dir_tga_4k, "PNG", 2.0, "SINC"
    )

    # Downscale 2160p TGA assets to 1440p
    image_processing.image_resizing(
        scaling_config.working_dir_tga_4k, scaling_config.working_dir_tga_2k, "PNG", 0.6, "SINC"
    )

    # Convert 2160p PNG assets to DDS format
    png_to_dds_options = ["-y", "-dx10"]
    image_processing.image_conversion(
        scaling_config.working_dir_dds_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_dds_options,
        "PNG",
        "DDS",
    )

    # Convert 1440p PNG assets to DDS format
    image_processing.image_conversion(
        scaling_config.working_dir_dds_2k,
        scaling_config.output_dir_2k,
        base_config.error_dir,
        png_to_dds_options,
        "PNG",
        "DDS",
    )

    # Convert 2160p PNG assets to TGA format
    png_to_tga_options = ["-y", "-tga20"]
    image_processing.image_conversion(
        scaling_config.working_dir_tga_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_tga_options,
        "PNG",
        "TGA",
    )

    # Convert 1440p PNG assets to TGA format.
    image_processing.image_conversion(
        scaling_config.working_dir_tga_2k,
        scaling_config.output_dir_2k,
        base_config.error_dir,
        png_to_tga_options,
        "PNG",
        "TGA",
    )

    log.info("Image processing workflow completed successfully.")
    log.info("Initiating text processing workflow...")

    # Scale positional values in GUI text files (1080p -> 2160p).
    text_processing.scale_positional_values(base_config.input_dir, scaling_config.output_dir_4k, "GUI", 1.8)

    # Scale positional values in GUI text files (1080p -> 1440p).
    text_processing.scale_positional_values(base_config.input_dir, scaling_config.output_dir_2k, "GUI", 1.2)

    log.info("Text processing workflow completed successfully.")

    # Delete working directories after finishing workflow
    for path in working_directories:
        file_utils.delete_directory(path)

    # Remove empty directories
    with contextlib.suppress(OSError):
        Path.rmdir(scaling_config.working_dir)
        for empty_directory in output_directories:
            Path.rmdir(empty_directory)


# ============================================ #
#           1440p -> 2160p  Workflow           #
# ============================================ #


def quadhd_to_ultrahd() -> None:
    """
    Scales game assets from 1440p to 2160p resolution.

    Process:
    -------
    -------
        - Deletes any old files (except input files) before initiating workflow.
        - Unzips the contents of any potential .zip files.
        - Converts DDS and TGA assets to PNG format.
        - Upscales 1440p DDS and TGA assets to 2160p.
        - Converts 2160p PNG assets to DDS and TGA format.
        - Scales positional values in GUI text files (1440p -> 2160p).
        - Deletes working directories after finishing workflow.
        - Removes empty directories.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - None.

    Exceptions:
    ----------
    ----------
        - Exception: If an unexpected error occurs during the workflow.
    """
    # Directory configuration, see config.py for more information.
    working_directories = [
        scaling_config.working_dir_dds,
        scaling_config.working_dir_tga,
        scaling_config.working_dir_dds_to_png,
        scaling_config.working_dir_dds_4k,
        scaling_config.working_dir_tga_to_png,
        scaling_config.working_dir_tga_4k,
    ]
    output_directories = [base_config.error_dir, scaling_config.output_dir_4k]

    log.info("Initiating image processing workflow...")

    # Delete any old files (except input files) before initiating workflow
    for path in working_directories + output_directories:
        file_utils.delete_directory(path)
        file_utils.create_directory(path)

    # Unzip the contents of any potential .zip files
    file_utils.unzip_files(base_config.input_dir, base_config.input_dir)

    # Convert DDS assets to PNG format
    dds_or_tga_to_png_options = ["-y", "-wiclossless"]
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_dds_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "DDS",
        "PNG",
    )

    # Convert TGA assets to PNG format
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_tga_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "TGA",
        "PNG",
    )

    # Upscale 1440p DDS assets to 2160p
    image_processing.image_resizing(
        scaling_config.working_dir_dds_to_png, scaling_config.working_dir_dds_4k, "PNG", 1.5, "SINC"
    )

    # Upscale 1440p TGA assets to 2160p
    image_processing.image_resizing(
        scaling_config.working_dir_tga_to_png, scaling_config.working_dir_tga_4k, "PNG", 1.5, "SINC"
    )

    # Convert PNG assets to DDS format
    png_to_dds_options = ["-y", "-dx10"]
    image_processing.image_conversion(
        scaling_config.working_dir_dds_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_dds_options,
        "PNG",
        "DDS",
    )

    # Convert PNG assets to TGA format
    png_to_tga_options = ["-y", "-tga20"]
    image_processing.image_conversion(
        scaling_config.working_dir_tga_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_tga_options,
        "PNG",
        "TGA",
    )

    log.info("Image processing workflow completed successfully.")
    log.info("Initiating text processing workflow...")

    # Scale positional values in GUI text files (1440p -> 2160p)
    text_processing.scale_positional_values(base_config.input_dir, scaling_config.output_dir_4k, "GUI", 1.5)

    log.info("Text processing workflow completed successfully.")

    # Delete working directories after finishing workflow
    for path in working_directories:
        file_utils.delete_directory(path)

    # Remove empty directories
    with contextlib.suppress(OSError):
        Path.rmdir(scaling_config.working_dir)
        for empty_directory in output_directories:
            Path.rmdir(empty_directory)


# =============================== #
#           Main Script           #
# =============================== #


if __name__ == "__main__":
    logging_utils.init_logger(base_config.log_level, base_config.log_dir)
    quadhd_to_ultrahd()
