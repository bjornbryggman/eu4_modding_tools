# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 80 characters).

Insert more descriptive explanation of the module here, max 3 rows,
max 100 characters per row (less is more, be concise and to the point).
"""

import os

import structlog
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import GeographyConfig
from app.database import relationships
from app.database.models import Area, Climate, Continent, Province, Region, SuperRegion
from app.functions import data_extraction, data_modification
from app.utils import db_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# Load environment variables.
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")
os.environ["OPENROUTER_API_TOKEN"] = os.getenv("OPENROUTER_API_KEY")
specific_model = os.getenv("OPENROUTER_TEXT_META_LLAMA-3_70B_NITRO")


# ======================================================= #
#                   Regular Expressions                   #
# ======================================================= #


PARSE_POSITIONS_REGEX = r"#([^\n]+)\n(\d+)=\{([^}]+)\}"
PARSE_ENTITY_REGEX = r"(\w+)\s*=\s*{([^}]+)}"
PARSE_REGION_REGEX = r"(\w+)\s*=\s*{\s*areas\s*=\s*{([^}]+)}"
PARSE_TERRAIN_REGEX = r"categories\s*=\s*{([^}]+)}"
UPDATE_TERRAIN_REGEX = r"(categories\s*=\s*{)([^}]+)(})"


# ============================================== #
#                   Main script                  #
# ============================================== #


def populate_database() -> None:
    """
    Populates the database with geographical data from EU4 game files.

    This function calls various parsing functions to read different game files
    and populate the database with Continents, SuperRegions, Regions, Areas,
    Provinces, Climates, and Terrains.

    The function should be called in the order specified to ensure proper
    relationship creation between different geographical entities.

    Args:
    ----
    - None.

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - OSError: If an error occurs during file operations.
    - PermissionError: If there's a permission issue when accessing files.
    - SQLAlchemyError: If there's an issue with database operations.
    - ValueError: If there's an issue with data processing or unexpected data format.
    """
    try:
        db_utils.create_database()
        log.info("Database created.")

        data_extraction.parse_positions_file(GeographyConfig.POSITIONS_TXT, PARSE_POSITIONS_REGEX)
        log.info("Provinces parsed.")

        data_extraction.parse_entity_file(GeographyConfig.AREA_TXT, PARSE_ENTITY_REGEX, Area, Province)
        log.info("Areas parsed.")

        data_extraction.parse_entity_file(GeographyConfig.REGION_TXT, PARSE_REGION_REGEX, Region, Area, True, "_area")
        log.info("Regions parsed.")

        data_extraction.parse_entity_file(
            GeographyConfig.SUPERREGION_TXT, PARSE_ENTITY_REGEX, SuperRegion, Region, True, "_region"
        )
        log.info("Superregions parsed.")

        data_extraction.parse_entity_file(GeographyConfig.CONTINENT_TXT, PARSE_ENTITY_REGEX, Continent, Province)
        log.info("Continents parsed.")

        data_extraction.parse_entity_file(GeographyConfig.CLIMATE_TXT, PARSE_ENTITY_REGEX, Climate, Province)
        log.info("Climates parsed.")

        terrain_data = data_extraction.parse_terrain_file(
            GeographyConfig.TERRAIN_TXT, PARSE_TERRAIN_REGEX, PARSE_ENTITY_REGEX
        )
        log.info("Terrains parsed.")

        data_modification.modify_terrain_file(GeographyConfig.TERRAIN_TXT, UPDATE_TERRAIN_REGEX, terrain_data)
        log.info("'terrain.txt' has been updated.")

        relationships.set_geographical_relationships()
        log.info("Relationships set.")

    except (Exception, OSError, PermissionError, SQLAlchemyError, ValueError) as error:
        log.exception("An error occured while populating the database.", exc_info=error)
    else:
        log.info("Database population completed.")


if __name__ == "__main__":
    populate_database()
