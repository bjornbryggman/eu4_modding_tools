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

# Initialize logger for this module
log = structlog.stdlib.get_logger(__name__)

# Create config instances
base_config = BaseConfig()
scaling_config = ScalingConfig()

# ============================================================= #
#                   Image Processing Workflow                   #
# ============================================================= #


# Directory configuration, see config.py for more information.
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


def process_images() -> None:
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """
    log.info("Initiating image processing workflow...")

    # Delete any old files (except input files) before initiating workflow.
    for path in working_directories + output_directories:
        file_utils.delete_directory(path)
        file_utils.create_directory(path)

    # Unzip the contents of any potential .zip files.
    file_utils.unzip_files(base_config.input_dir, base_config.input_dir)

    # Convert DDS and TGA assets to PNG format.
    dds_or_tga_to_png_options = ["-y", "-wiclossless"]
    # Overwrites files and enables lossless conversion to PNG.
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_dds_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "DDS",
        "PNG",
    )
    image_processing.image_conversion(
        base_config.input_dir,
        scaling_config.working_dir_tga_to_png,
        base_config.error_dir,
        dds_or_tga_to_png_options,
        "TGA",
        "PNG",
    )

    # Resize DDS assets.
    image_processing.image_resizing(
        scaling_config.working_dir_dds_to_png, scaling_config.working_dir_dds_4k, "PNG", 2.0, "SINC"
    )
    image_processing.image_resizing(
        scaling_config.working_dir_dds_4k, scaling_config.working_dir_dds_2k, "PNG", 0.6, "SINC"
    )

    # Resize TGA assets.
    image_processing.image_resizing(
        scaling_config.working_dir_tga_to_png, scaling_config.working_dir_tga_4k, "PNG", 2.0, "SINC"
    )
    image_processing.image_resizing(
        scaling_config.working_dir_tga_4k, scaling_config.working_dir_tga_2k, "PNG", 0.6, "SINC"
    )

    # Convert PNG assets to DDS format.
    png_to_dds_options = ["-y", "-dx10"]
    # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        scaling_config.working_dir_dds_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_dds_options,
        "PNG",
        "DDS",
    )
    image_processing.image_conversion(
        scaling_config.working_dir_dds_2k,
        scaling_config.output_dir_2k,
        base_config.error_dir,
        png_to_dds_options,
        "PNG",
        "DDS",
    )

    # Convert PNG assets to TGA format.
    png_to_tga_options = ["-y", "-tga20"]
    # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.image_conversion(
        scaling_config.working_dir_tga_4k,
        scaling_config.output_dir_4k,
        base_config.error_dir,
        png_to_tga_options,
        "PNG",
        "TGA",
    )
    image_processing.image_conversion(
        scaling_config.working_dir_tga_2k,
        scaling_config.output_dir_2k,
        base_config.error_dir,
        png_to_tga_options,
        "PNG",
        "TGA",
    )

    # Delete working directories after finishing workflow.
    for path in working_directories:
        file_utils.delete_directory(path)
    Path.rmdir(scaling_config.working_dir)

    # Removes error directory if empty.
    with contextlib.suppress(OSError):
        Path.rmdir(base_config.error_dir)


# ============================================================ #
#                   Text Processing Workflow                   #
# ============================================================ #


def text_positional_value_scaling() -> None:
    """
    Scales positional values in text GUI files.

    This function applies a specific scaling factor to positional values in the
    targeted input files and writes the scaled content to the output directory.
    """
    log.info("Initiating GUI scaling workflow...")

    # Scale positional values GUI text files (for 2K monitors).
    text_processing.scale_positional_values(base_config.input_dir, scaling_config.output_dir_2k, "GUI", 1.2)


if __name__ == "__main__":
    logging_utils.init_logger(base_config.log_level, base_config.log_dir)
    process_images()
    log.info("Image processing workflow completed successfully.")
    text_positional_value_scaling()
    log.info("Text processing workflow completed successfully.")
