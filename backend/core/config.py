# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

from pathlib import Path

import structlog

log = structlog.stdlib.get_logger(__name__)


class DirectoryConfig:
    """Represents a configuration object."""

    def __init__(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.LOG_DIRECTORY = self.BASE_PATH / "logs"
        self.INPUT_DIRECTORY = self.BASE_PATH / "content" / "input"
        self.PNG_DIRECTORY = self.BASE_PATH / "content" / "png_files"
        self.UPSCALED_DIRECTORY = self.BASE_PATH / "content" / "upscaled_files"
        self.RESIZED_DIRECTORY = self.BASE_PATH / "content" / "resized_files"
        self.OUTPUT_DIRECTORY = self.BASE_PATH / "content" / "output"
        self.LOG_LEVEL = "DEBUG"
