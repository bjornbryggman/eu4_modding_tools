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

from app.config import DirectoryConfig
from app.functions import image_processing, text_processing
from app.utils import file_utils, logging_utils

log = structlog.stdlib.get_logger(__name__)

load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")
os.environ["OPENROUTER_API_TOKEN"] = os.getenv("OPENROUTER_API_KEY")
specific_model = os.getenv("OPENROUTER_TEXT_META_LLAMA-3_70B_NITRO")


def main() -> None:
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """
    config = DirectoryConfig()
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIR)
    log.info("Initiating workflow...")

    for directory_path in [
        config.WORKING_PNG_DIR,
        config.WORKING_DIR_2160P,
        config.WORKING_DIR_1440P,
        config.ERROR_DIR,
        config.OUTPUT_DIR_1440P,
        config.OUTPUT_DIR_2160P,
    ]:
        file_utils.delete_directory(directory_path)
        file_utils.create_directory(directory_path)

    dds_to_png_options = ["-y", "-wiclossless"]  # Overwrites files and enables lossless conversion to PNG.
    image_processing.texconv_convert_images(
       config.INPUT_DIR, config.WORKING_PNG_DIR, config.ERROR_DIR, dds_to_png_options, "DDS", "PNG"
    )

    image_processing.imagemagick_resize_images(config.WORKING_PNG_DIR, config.WORKING_DIR_2160P, "PNG", 2.0, "SINC")
    image_processing.imagemagick_resize_images(
        config.WORKING_DIR_2160P, config.WORKING_DIR_1440P, "PNG", 0.6667, "SINC"
    )

    png_to_dds_options = ["-y", "-dx10"]  # Overwrites files and forces the use of the "DX10" header extension.
    image_processing.texconv_convert_images(
        config.WORKING_DIR_2160P, config.OUTPUT_DIR_2160P, config.ERROR_DIR, png_to_dds_options, "PNG", "DDS"
    )
    image_processing.texconv_convert_images(
        config.WORKING_DIR_1440P, config.OUTPUT_DIR_1440P, config.ERROR_DIR, png_to_dds_options, "PNG", "DDS"
    )

    text_processing.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_2160P, "GUI", 1.4)
    text_processing.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_2160P, "GFX", 1.4)

    text_processing.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_1440P, "GUI", 1.2)
    text_processing.scale_positional_values(config.INPUT_DIR, config.OUTPUT_DIR_1440P, "GFX", 1.2)

    for directory_path in [config.WORKING_PNG_DIR, config.WORKING_DIR_1440P, config.WORKING_DIR_2160P]:
        file_utils.delete_directory(directory_path)

    # Removes error directory if it's empty.
    with contextlib.suppress(OSError):
        Path.rmdir(config.ERROR_DIR)

    log.info("Image processing pipeline completed successfully.")


if __name__ == "__main__":
    main()
