# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides configuration classes for managing directory paths used in the project.

This module defines several configuration classes that centralize the management
of directory paths used throughout the project. Each class encapsulates paths
related to specific functionalities, such as geography data, scaling operations,
and LLM prompts.
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
        - root_path (Path):
        - input_dir (Path): Path to the directory that contains the input files.
        - error_dir (Path): Path to the directory that stores error files.

        - log_dir (Path): Path to the directory for storing log files.
        - log_level (str): Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    """

    def __init__(self) -> None:
        "Initializes the BaseConfig with values from environment variables."
        # Root directory
        self.root_path = Path(__file__).resolve().parent.parent.parent.parent

        # Input directory
        self.input_dir = self.root_path / "frontend" / "resources" / "input_directory"

        # Error directory
        self.error_dir = self.root_path / "frontend" / "resources" / "error_directory"

        # Database file
        self.database_file = self.root_path / "backend" / "app" / "database" / "SQLite.db"

        # Logging configuration.
        self.log_dir = self.root_path / "frontend" / "log_directory"
        self.log_level = "DEBUG"


class GeographyConfig:
    """
    Configuration class for directory paths used in the 'terrain_script.py'.

    Attributes:
    ----------
        - positions_txt (Path):
        - area_txt (Path):
        - region_txt (Path):
        - superregion_txt (Path):
        - continent_txt (Path):

        - climate_txt (Path):
        - terrain_txt (Path):
    """

    def __init__(self) -> None:
        "Initializes the GeographyConfig."
        # Create an instance of the BaseConfig class.
        self.base_config = BaseConfig()

        # Text files containing geographical entities.
        self.positions_txt = self.base_config.input_dir / "map" / "positions.txt"
        self.area_txt = self.base_config.input_dir / "map" / "area.txt"
        self.region_txt = self.base_config.input_dir / "map" / "region.txt"
        self.superregion_txt = self.base_config.input_dir / "map" / "superregion.txt"
        self.continent_txt = self.base_config.input_dir / "map" / "continent.txt"

        # Text files containing weather & terrain information.
        self.climate_txt = self.base_config.input_dir / "map" / "climate.txt"
        self.terrain_txt = self.base_config.input_dir / "map" / "terrain.txt"


class ScalingConfig:
    """
    Configuration class for directory paths used in the 'scaling_script.py'.

    Attributes:
    ----------
        - working_dir_dds (Path):
        - working_dir_dds_to_png (Path):
        - working_dir_dds_4k (Path):
        - working_dir_dds_2k (Path):

        - working_dir_tga (Path):
        - working_dir_tga_to_png (Path):
        - working_dir_tga_4k (Path):
        - working_dir_tga_2k (Path):

        - text_comparison_original_dir (Path): Path to the directory containing original files
            for scaling factor comparison.
        - text_comparison_dir_2k (Path): Path to the directory containing 2K files
            for scaling factor comparison.
        - text_comparison_dir_4k (Path): Path to the directory containing 4K files
            for scaling factor comparison.

        - output_dir_2k (Path): Path to the output directory for 2K files.
        - output_dir_4k (Path): Path to the output directory for 4K files.
    """

    def __init__(self) -> None:
        "Initializes the ScalingConfig."
        # Create an instance of the BaseConfig class.
        self.base_config = BaseConfig()

        # Working directories.
        resources_path = self.base_config.root_path / "frontend" / "resources"
        self.working_dir = resources_path / "working_directory"

        # DDS files.
        self.working_dir_dds = self.working_dir /  "dds"
        self.working_dir_dds_to_png = self.working_dir_dds / "dds_png"
        self.working_dir_dds_4k = self.working_dir_dds / "dds_png_4k"
        self.working_dir_dds_2k = self.working_dir_dds / "dds_png_2k"

        # TGA files.
        self.working_dir_tga = self.working_dir / "tga"
        self.working_dir_tga_to_png = self.working_dir_tga / "tga_png"
        self.working_dir_tga_4k = self.working_dir_tga / "tga_png_4k"
        self.working_dir_tga_2k = self.working_dir_tga / "tga_png_2k"

        # Output directories.
        self.output_dir = resources_path / "output_directory"
        self.output_dir_4k = self.output_dir / "output_4k"
        self.output_dir_2k = self.output_dir / "output_2k"


class PromptConfig:
    """
    Configuration class for file paths used in LLM prompts.

    Attributes:
    ----------
        - something.
    """

    def __init__(self) -> None:
        "Initializes the PromptConfig."
        # Create an instance of the BaseConfig class.
        self.base_config = BaseConfig()

        # Prompt folder
        prompt_dir = self.base_config.root_path / "backend" / "app" / "robot"
        self.prompt_yaml = prompt_dir / "prompts.yaml"
        self.documentation_yaml = prompt_dir/ "documentation.yaml"
