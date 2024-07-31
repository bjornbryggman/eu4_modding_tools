# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 60 characters).

Insert more descriptive explanation of the module here, max 4 rows, max 100 characters per row.
"""

from pathlib import Path

import structlog

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ================================================================== #
#                   Directory Configuration Classes                  #
# ================================================================== #


class BaseConfig:
    """
    Configuration class for basic directory paths.

    Attributes:
    ----------
    - ROOT_PATH (Path):
    - INPUT_DIR (Path): Path to the directory that contains the input files.
    - ERROR_DIR (Path): Path to the directory that stores error files.

    - LOG_DIR (Path): Path to the directory for storing log files.
    - LOG_LEVEL (str): Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    """

    def __init__(self) -> None:
        "Initializes the BaseConfig with values from environment variables."
        # Base directories.
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.INPUT_DIR = self.ROOT_PATH / "resources" / "input_directory"
        self.ERROR_DIR = self.ROOT_PATH / "resources" / "error_directory"

        # Logging configuration.
        self.LOG_DIR = self.ROOT_PATH / "log_directory"
        self.LOG_LEVEL = "DEBUG"


class ScalingConfig:
    """
    Configuration class for directory paths used in the 'scaling_script.py'.

    Attributes:
    ----------
    - WORKING_DIR_DDS (Path):
    - WORKING_DIR_DDS_TO_PNG (Path):
    - WORKING_DIR_DDS_4K (Path):
    - WORKING_DIR_DDS_2k (Path):

    - WORKING_DIR_TGA (Path):
    - WORKING_DIR_TGA_TO_PNG (Path):
    - WORKING_DIR_TGA_4K (Path):
    - WORKING_DIR_TGA_2k (Path):

    - TEXT_COMPARISON_ORIGINAL_DIR (Path): Path to the directory containing original files
        for scaling factor comparison.
    - TEXT_COMPARISON_DIR_2K (Path): Path to the directory containing 2K files
        for scaling factor comparison.
    - TEXT_COMPARISON_DIR_4K (Path): Path to the directory containing 4K files
        for scaling factor comparison.

    - OUTPUT_DIR_2K (Path): Path to the output directory for 2K files.
    - OUTPUT_DIR_4K (Path): Path to the output directory for 4K files.
    """

    def __init__(self) -> None:
        "Initializes the ScalingConfig."
        # Working directories.
        # DDS files.
        self.WORKING_DIR_DDS = BaseConfig.ROOT_PATH / "resources" / "working_directory" / "dds"
        self.WORKING_DIR_DDS_TO_PNG = self.WORKING_DIR_DDS / "dds_png"
        self.WORKING_DIR_DDS_4K = self.WORKING_DIR_DDS / "dds_png_4k"
        self.WORKING_DIR_DDS_2K = self.WORKING_DIR_DDS / "dds_png_2k"

        # TGA files.
        self.WORKING_DIR_TGA = BaseConfig.ROOT_PATH / "resources" / "working_directory" / "tga"
        self.WORKING_DIR_TGA_TO_PNG = self.WORKING_DIR_TGA / "tga_png"
        self.WORKING_DIR_TGA_4K = self.WORKING_DIR_TGA / "tga_png_4k"
        self.WORKING_DIR_TGA_2K = self.WORKING_DIR_TGA / "tga_png_2k"

        # Text directories.
        self.TEXT_COMPARISON_DIR = BaseConfig.ROOT_PATH / "resources" / "text_comparison_directory"
        self.TEXT_COMPARISON_ORIGINAL_DIR = self.TEXT_COMPARISON_DIR / "text_files_original"
        self.TEXT_COMPARISON_DIR_4K = self.TEXT_COMPARISON_DIR / "text_files_4k"
        self.TEXT_COMPARISON_DIR_2K = self.TEXT_COMPARISON_DIR / "text_files_2k"

        # Output directories.
        self.OUTPUT_DIR = BaseConfig.ROOT_PATH / "resources" / "output_directory"
        self.OUTPUT_DIR_4K = self.OUTPUT_DIR / "output_4k"
        self.OUTPUT_DIR_2K = self.OUTPUT_DIR / "output_2k"


class GeographyConfig:
    """
    Configuration class for directory paths used in the 'terrain_script.py'.

    Attributes:
    ----------
    - POSITIONS_TXT (Path):
    - AREA_TXT (Path):
    - REGION_TXT (Path):
    - SUPERREGION_TXT (Path):
    - CONTINENT_TXT (Path):

    - CLIMATE_TXT (Path):
    - TERRAIN_TXT (Path):
    """

    def __init__(self) -> None:
        "Initializes the TerrainConfig."
        # Text files containing geographical entities.
        self.POSITIONS_TXT = BaseConfig.INPUT_DIR / "map" / "positions.txt"
        self.AREA_TXT = BaseConfig.INPUT_DIR / "map" / "area.txt"
        self.REGION_TXT = BaseConfig.INPUT_DIR / "map" / "region.txt"
        self.SUPERREGION_TXT = BaseConfig.INPUT_DIR / "map" / "superregion.txt"
        self.CONTINENT_TXT = BaseConfig.INPUT_DIR / "map" / "continent.txt"

        # Text files containing weather & terrain information.
        self.CLIMATE_TXT = BaseConfig.INPUT_DIR / "map" / "climate.txt"
        self.TERRAIN_TXT = BaseConfig.INPUT_DIR / "map" / "terrain.txt"
