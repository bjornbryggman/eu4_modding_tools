# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module defines configuration settings for the text processing application.

It provides settings for input/output directories, logging, and other relevant parameters.
"""

from pathlib import Path

import structlog

log = structlog.stdlib.get_logger(__name__)


class DirectoryConfig:
    """
    Configuration class for directory paths.

    Attributes:
    ----------
    - INPUT_DIR (Path): Path to the directory containing the input files.
    - ERROR_DIR (Path): Path to the directory for storing error files.

    - LOG_DIR (Path): Path to the directory for storing log files.
    - LOG_LEVEL (str): Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").

    - TEXT_COMPARISON_ORIGINAL_DIR (Path): Path to the directory containing original files
        for scaling factor comparison.
    - TEXT_COMPARISON_DIR_2K (Path): Path to the directory containing 2K scaled files
        for scaling factor comparison.
    - TEXT_COMPARISON_DIR_4K (Path): Path to the directory containing 4K scaled files
        for scaling factor comparison.

    - OUTPUT_DIR_2K (Path): Path to the directory for outputting 2K scaled files.
    - OUTPUT_DIR_4K (Path): Path to the directory for outputting 4K scaled files.
    """

    def __init__(self) -> None:
        "Initializes the DirectoryConfig with values from environment variables."
        # Base directories.
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.INPUT_DIR = self.ROOT_PATH / "resources" / "input_files"
        self.ERROR_DIR = self.ROOT_PATH / "resources" / "error_files"

        # Logging configuration.
        self.LOG_DIR = self.ROOT_PATH / "logs"
        self.LOG_LEVEL = "DEBUG"

        # Working directories.
        self.WORKING_DIR_DDS = self.ROOT_PATH / "resources" / "dds_files"
        self.WORKING_DIR_TGA = self.ROOT_PATH / "resources" / "tga_files"

        # DDS files.
        self.WORKING_DIR_DDS_TO_PNG = (
            self.ROOT_PATH / "resources" / "dds_files" / "dds_png_files"
        )
        self.WORKING_DIR_DDS_4K = (
            self.ROOT_PATH / "resources" / "dds_files" / "dds_png_files_4k"
        )
        self.WORKING_DIR_DDS_2K = (
            self.ROOT_PATH / "resources" / "dds_files" / "dds_png_files_2k"
        )

        # TGA files.
        self.WORKING_DIR_TGA_TO_PNG = (
            self.ROOT_PATH / "resources" / "tga_files" / "tga_png_files"
        )
        self.WORKING_DIR_TGA_4K = (
            self.ROOT_PATH / "resources" / "tga_files" / "tga_png_files_4k"
        )
        self.WORKING_DIR_TGA_2K = (
            self.ROOT_PATH / "resources" / "tga_files" / "tga_png_files_2k"
        )

        # Text directories.
        self.TEXT_COMPARISON_DIR = self.ROOT_PATH / "other" / "text_files"
        self.TEXT_COMPARISON_ORIGINAL_DIR = (
            self.ROOT_PATH / "other" / "text_files" / "text_files_original"
        )
        self.TEXT_COMPARISON_DIR_4K = (
            self.ROOT_PATH / "other" / "text_files" / "text_files_4k"
        )
        self.TEXT_COMPARISON_DIR_2K = (
            self.ROOT_PATH / "other" / "text_files" / "text_files_2k"
        )

        # Output directories.
        self.OUTPUT_DIR = self.ROOT_PATH / "resources" / "output_files"
        self.OUTPUT_DIR_4K = (
            self.ROOT_PATH / "resources" / "output_files" / "output_files_4k"
        )
        self.OUTPUT_DIR_2K = (
            self.ROOT_PATH / "resources" / "output_files" / "output_files_2k"
        )
