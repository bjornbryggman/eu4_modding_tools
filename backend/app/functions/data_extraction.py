# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Parses game data files and updates the database with extracted information.

This module provides functions for parsing various game data files, including
positions, entities, and terrain information. It extracts relevant data using
regular expressions and updates the corresponding database models.
"""

import re
from pathlib import Path

import structlog
from backend.app.utils.db_utils import session_scope
from sqlmodel import select

from app.database.models import Province, Terrain
from app.utils.file_utils import read_file

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ======================================================#
#          Function for extracting province IDs         #
# ======================================================#


def parse_positions_file(input_file: Path, regex_pattern: str) -> None:
    """
    Parse the positions.txt file and update the database with Province entries.

    Process:
    -------
    -------
        - Reads the positions.txt file and extracts province definitions using a regular expression.
        - Creates or updates Province entries in the database based on the extracted information.

    Args:
    ----
    ----
        - input_file (Path): The path to the positions.txt file to be parsed.
        - regex_pattern (str): The regular expression pattern used to extract province definitions from the file.

    Returns:
    -------
    -------
        - None: This function does not return any value, but updates the database instead.

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any unexpected errors during execution.
        - OSError: Raised when an error occurs while reading the file.
        - PermissionError: Raised when there is no permission to read the file.
        - ValueError: Raised when invalid data is encountered during parsing.
    """
    try:
        content = read_file(input_file)
        provinces = re.findall(regex_pattern, content, re.DOTALL)
        if not provinces:
            log.warning("No provinces found in %s.", input_file)

        with session_scope() as session:
            for province_name, province_id, _province_data in provinces:
                province = Province(id=int(province_id), name=province_name.strip())
                session.add(province)

    except (Exception, OSError, PermissionError, ValueError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
        raise
    else:
        log.debug("Parsed %s provinces from %s.", len(provinces), input_file)


# =============================================#
#         Functions for extracting data        #
# =============================================#


def parse_entity_file(
    input_file: str,
    regex_pattern: str,
    parent_model: type,
    child_model: type,
    verbose: bool = False,
    child_identifier: str | None = None,
) -> None:
    """
    Parse an entity file, extract definitions, and update the database with parent and child entities.

    Process:
    -------
    -------
        - Reads the input file and extracts entity definitions using a provided regex pattern.
        - Creates parent entities in the database.
        - Identifies child entities based on either verbose mode (using a child identifier) or
          non-verbose mode (using IDs).
        - Associates child entities with their respective parent entities in the database.

    Args:
    ----
    ----
        - input_file (str): Path to the file containing entity definitions.
        - regex_pattern (str): Regular expression pattern to extract entity definitions.
        - parent_model (type): Model class for parent entities.
        - child_model (type): Model class for child entities.
        - verbose (bool, optional): Flag to enable verbose mode for child entity identification.
          Defaults to False.
        - child_identifier (str | None, optional): Identifier used in verbose mode to identify
          child entities. Defaults to None.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: General exception for any errors during processing.
        - OSError: Raised for operating system-related errors.
        - PermissionError: Raised for permission-related errors.
        - ValueError: Raised for invalid input values.
    """
    try:
        content = read_file(input_file)
        entities = re.findall(regex_pattern, content, re.DOTALL)
        if not entities:
            log.warning("No entities found in %s.", input_file)

        with session_scope() as session:
            for name, children in entities:
                parent = parent_model(name=name)
                session.add(parent)
                session.flush()

                if verbose:
                    child_names = re.findall(rf"\w+{child_identifier}", children)
                    for child_name in child_names:
                        child = session.get(child_model, str(child_name))
                        setattr(child, f"{parent_model.__name__.lower()}", parent)
                else:
                    child_ids = re.findall(r"\d+", children)
                    for child_id in child_ids:
                        child = session.get(child_model, int(child_id))
                        setattr(child, f"{parent_model.__name__.lower()}", parent)

    except (Exception, OSError, PermissionError, ValueError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
        raise
    else:
        log.debug("Parsed %s entities from %s.", len(entities), input_file)


# ===================================================================#
#          Functions for extracting data from "terrain.txt"          #
# ===================================================================#


def parse_terrain_file(input_file: Path, regex_pattern: str, terrain_types_regex_pattern: str) -> None:
    """
    Parse terrain file and update database with terrain information.

    Process:
    -------
    -------
        - Reads the terrain file and extracts terrain types and properties.
        - Creates or updates Terrain entries in the database.
        - Handles terrain overrides for specific provinces.

    Args:
    ----
    ----
        - input_file (Path): The path to the terrain file to be parsed.
        - regex_pattern (str): The regular expression pattern to match the categories block in the file.
        - terrain_types_regex_pattern (str): The regular expression pattern to match terrain types
          within the categories block.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any unexpected errors during execution.
        - OSError: Raised when an operating system-related error occurs.
        - PermissionError: Raised when a permission-related error occurs.
        - ValueError: Raised when an invalid value is encountered.
    """
    try:
        content = read_file(input_file)
        categories_match = re.search(regex_pattern, content, re.DOTALL)
        if not categories_match:
            log.error("Could not find categories block in %s.", input_file)
        categories_content = categories_match.group(1)

        terrain_types = re.findall(terrain_types_regex_pattern, categories_content, re.DOTALL)
        terrain_data, custom_terrains = process_terrain_types(terrain_types)

        update_database_with_terrain(terrain_data, custom_terrains)

    except (Exception, OSError, PermissionError, ValueError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
        raise
    else:
        log.debug("Parsed %s terrain types from %s.", len(terrain_types), input_file)
        log.debug("Created %s custom terrain types.", len(custom_terrains))
        return terrain_data


def process_terrain_types(terrain_types: list[tuple[str, str]]) -> tuple[dict[str, dict], list[Terrain]]:
    """
    Process terrain types to extract properties and overrides for provinces.

    Process:
    -------
    -------
        - Iterates through terrain types, extracting properties and identifying overrides.
        - Creates custom terrains for province-specific overrides.
        - Returns a dictionary of terrain data and a list of custom terrains.

    Args:
    ----
    ----
        - terrain_types (list[tuple[str, str]]): A list of tuples containing terrain names and their contents.

    Returns:
    -------
    -------
        - tuple[dict[str, dict], list[Terrain]]: A tuple containing a dictionary of terrain data and a list
          of custom terrains.

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any unexpected errors during processing.
        - ValueError: Raised for invalid input parameters.
    """
    terrain_data = {}
    custom_terrains = []

    try:
        for terrain_name, terrain_content in terrain_types:
            properties = {}
            for line in terrain_content.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    properties[key.strip()] = value.strip()

            terrain_override_match = re.search(r"terrain_override\s*=\s*{([^}]+)}", terrain_content)
            if terrain_override_match:
                province_ids = re.findall(r"\d+", terrain_override_match.group(1))
                remaining_province_ids = province_ids.copy()

                for province_id in province_ids:
                    custom_terrain_name = f"custom_{terrain_name}_{province_id}"
                    custom_properties = properties.copy()
                    custom_properties["terrain_override"] = f"{{ {province_id} }}"

                    custom_terrain = Terrain(
                        name=custom_terrain_name, original_terrain=terrain_name, properties=custom_properties
                    )
                    custom_terrains.append(custom_terrain)

                    remaining_province_ids.remove(province_id)

                properties["terrain_override"] = f"{{ {" ".join(remaining_province_ids)} }}"

            terrain_data[terrain_name] = properties

    except (Exception, ValueError) as error:
        log.exception("Error processing terrain types.", exc_info=error)
        raise
    else:
        return terrain_data, custom_terrains


def update_database_with_terrain(terrain_data: dict[str, dict], custom_terrains: list[Terrain]) -> None:
    """
    Update the database with terrain information and overrides.

    Process:
    -------
    -------
        - Iterates through the provided terrain data, updating or creating Terrain entries in the database.
        - For each custom terrain, links it to the corresponding province based on the 'terrain_override' property.

    Args:
    ----
    ----
        - terrain_data (dict[str, dict]): A dictionary containing terrain names and their properties.
        - custom_terrains (list[Terrain]): A list of custom Terrain objects to be added to the database.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any general errors during database operations.
        - ValueError: Raised for specific errors related to data validation or processing.
    """
    try:
        with session_scope() as session:
            for terrain_name, properties in terrain_data.items():
                original_terrain = session.exec(select(Terrain).where(Terrain.name == terrain_name)).first()
                if original_terrain:
                    original_terrain.properties = properties
                else:
                    original_terrain = Terrain(name=terrain_name, original_terrain=terrain_name, properties=properties)
                    session.add(original_terrain)

            for custom_terrain in custom_terrains:
                session.add(custom_terrain)
                province_id = int(re.search(r"\d+", custom_terrain.properties["terrain_override"]).group())
                province = session.exec(select(Province).where(Province.id == province_id)).first()
                if province:
                    province.terrain = custom_terrain
                else:
                    log.warning(
                        "Province with id %s not found for custom terrain %s.", province_id, custom_terrain.name
                    )
    except (Exception, ValueError) as error:
        log.exception("Error updating database with terrain types.", exc_info=error)
        raise
