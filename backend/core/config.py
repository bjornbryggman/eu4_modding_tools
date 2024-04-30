import structlog
from pathlib import Path

log = structlog.stdlib.get_logger(__name__)

class DirectoryConfig:
    """
    Represents a configuration object.

    """
    def __init__(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.LOG_DIRECTORY = self.BASE_PATH / "logs"
        self.INPUT_DIRECTORY = self.BASE_PATH / "content" / "input"
        self.PNG_DIRECTORY = self.BASE_PATH / "content" / "converted_files_in_png_format"
        self.UPSCALED_DIRECTORY = self.BASE_PATH / "content" / "upscaled_files"
        self.RESIZED_DIRECTORY = self.BASE_PATH / "content" / "resized_files"
        self.OUTPUT_DIRECTORY = self.BASE_PATH / "content" / "output_dds_files"
        self.LOG_LEVEL = "INFO"
