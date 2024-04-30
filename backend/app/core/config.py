import structlog
from pathlib import Path

log = structlog.stdlib.get_logger("./src/config.py")

class DirectoryConfig:
    """
    Represents a configuration object.

    """
    def __init__(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.LOG_DIRECTORY = self.BASE_PATH / "logs"
        self.INPUT_DIRECTORY = self.BASE_PATH / "assets" / "input"
        self.PNG_DIRECTORY = self.BASE_PATH / "assets" / "converted_files_in_png_format"
        self.UPSCALED_DIRECTORY = self.BASE_PATH / "assets" / "upscaled_files"
        self.RESIZED_DIRECTORY = self.BASE_PATH / "assets" / "resized_files"
        self.OUTPUT_DIRECTORY = self.BASE_PATH / "assets" / "output_dds_files"
        self.LOG_LEVEL = "INFO"
