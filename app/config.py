# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

from pathlib import Path

import structlog

log = structlog.stdlib.get_logger(__name__)


class DirectoryConfig:
    """Represents a configuration object."""

    def __init__(self) -> None:
        # Base directories.
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.LOG_DIR = self.ROOT_PATH / "logs"
        self.LOG_LEVEL = "DEBUG"
        self.INPUT_DIR = self.ROOT_PATH / "resources" / "input"

        # Working directories.
        self.WORKING_PNG_DIR = self.ROOT_PATH / "resources" / "png_files"
        self.WORKING_DIR_2160P = self.ROOT_PATH / "resources" / "2160p_png_files"
        self.WORKING_DIR_1440P = self.ROOT_PATH / "resources" / "1440p_png_files"

        # Output directories.
        self.ERROR_DIR = self.ROOT_PATH / "resources" / "error_files"
        self.OUTPUT_DIR_2160P = self.ROOT_PATH / "resources" / "output_2160p"
        self.OUTPUT_DIR_1440P = self.ROOT_PATH / "resources" / "output_1440p"
