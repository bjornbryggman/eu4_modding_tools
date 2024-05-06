# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This script converts image files from DDS to PNG format, upscales them using AI, resize, and converts back to DDS format.

It also adjusts any relevant GUI files by the appropriate scaling factor.
"""

import os

import structlog
from dotenv import load_dotenv

from backend import gui_file_scaler, image_processing
from backend.api import litellm_text_generation, replicate_image_generation
from backend.core.config import DirectoryConfig
from backend.utils import file_utils, logging_utils

load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")
os.environ["OPENROUTER_API_TOKEN"] = os.getenv("OPENROUTER_API_KEY")
specific_model = os.getenv("OPENROUTER_TEXT_META_LLAMA-3_70B_NITRO")

litellm_text_generation.streaming_text_completion_call(
    "user", "this is a text. write me a funny poem about a famous historical figure", specific_model
)


def main():
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """
    config = DirectoryConfig()
    logging_utils.init_logger(config.LOG_LEVEL, config.LOG_DIRECTORY)
    log = structlog.stdlib.get_logger(__name__)
    log.info("Initiating workflow...")

    try:
        for directory_path in [
            config.PNG_DIRECTORY,
            config.UPSCALED_DIRECTORY,
            config.RESIZED_DIRECTORY,
            config.OUTPUT_DIRECTORY,
        ]:
            file_utils.delete_directory(directory_path)
            file_utils.create_directory(directory_path)

        image_processing.convert_images(config.INPUT_DIRECTORY, config.PNG_DIRECTORY, "DDS", "PNG")
        replicate_image_generation.upscale_images(
            config.PNG_DIRECTORY, config.UPSCALED_DIRECTORY, "PNG", os.getenv("REPLICATE_IMAGE_UPSCALING_MODEL")
        )
        image_processing.resize_images(config.UPSCALED_DIRECTORY, config.RESIZED_DIRECTORY, "PNG", 0.6)
        image_processing.convert_images(config.RESIZED_DIRECTORY, config.OUTPUT_DIRECTORY, "PNG", "DDS")

        for directory_path in [config.PNG_DIRECTORY, config.RESIZED_DIRECTORY, config.UPSCALED_DIRECTORY]:
            file_utils.delete_directory(directory_path)

        gui_file_scaler.process_GUI_files(config.INPUT_DIRECTORY, "GUI", 1.2)

        log.info("Image processing pipeline completed successfully.")

    except Exception as error:
        log.error("An unexpected error occurred during the image processing pipeline:\n%s", str(error))


if __name__ == "__main__":
    main()
