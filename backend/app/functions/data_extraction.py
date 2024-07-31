# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Extracts data and populates a database.

This module provides functions for parsing various EU4 game files
and populating a database with the extracted data.
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
    Parses the positions.txt file and updates the database with Province entries.

    This function reads the positions.txt file, which contains province definitions
    including their IDs and names. It creates or updates Province entries in the
    database based on this information.

    Args:
    ----
    - input_file (Path): The path to the positions.txt file.
    - regex_pattern (str): The regular expression pattern to match entity definitions.

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - OSError: If an error occurs during file operations.
    - PermissionError: If there's a permission issue when accessing files.
    - ValueError: If there's an issue with data processing or unexpected data format.
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
    Parses a file containing entity definitions and updates the database.

    This function reads an input file, extracts entity definitions using a regex pattern,
    and creates parent and child entities in the database. It supports both verbose and
    non-verbose modes for child entity identification.

    Args:
    ----
    - input_file (str): The path to the file containing entity definitions.
    - regex_pattern (str): The regular expression pattern to match entity definitions.
    - parent_model (type): The SQLModel class representing the parent entity (e.g., SuperRegion).
    - child_model (type): The SQLModel class representing the child entity (e.g., Region).
    - child_identifier (str): The string pattern to identify child entities (e.g., "_region").

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - OSError: If an error occurs during file operations.
    - PermissionError: If there's a permission issue when accessing files.
    - ValueError: If there's an issue with data processing or unexpected data format.
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


def parse_terrain_file(
    input_file: Path, regex_pattern: str, terrain_types_regex_pattern: str
) -> None:
    """
    Parses the terrain.txt file and updates the database with terrain information.

    This function reads the terrain.txt file, extracts terrain types and their
    properties, creates or updates Terrain entries in the database, and also
    handles terrain overrides for specific provinces.

    Args:
    ----
    - input_file (Path): The path to the terrain.txt file.
    - regex_pattern (str): The regular expression pattern to match entity definitions.
    - terrain_types_regex_pattern (str): The regular expression pattern to match terrain types.
    - update_regex_pattern (str): The regular expression pattern used when updating the terrain.txt.

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - OSError: If an error occurs during file operations.
    - PermissionError: If there's a permission issue when accessing files.
    - ValueError: If there's an issue with data processing or unexpected data format.
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


def process_terrain_types(
    terrain_types: list[tuple[str, str]],
) -> tuple[dict[str, dict], list[Terrain]]:
    """
    Processes terrain types and extracts properties and overrides.

    This function iterates through the extracted terrain types, extracting
    properties and identifying terrain overrides for specific provinces. It
    returns a dictionary of terrain data and a list of custom terrains
    created for overrides.

    Args:
    ----
    - terrain_types (list[tuple[str, str]]): A list of tuples containing
      terrain names and their content from the terrain.txt file.

    Returns:
    -------
    - dict[str, dict]: A dictionary mapping terrain names to their properties.
    - list[Terrain]: A list of custom terrain objects created for overrides.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - ValueError: If there's an issue with data processing or unexpected data format.
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
                        name=custom_terrain_name,
                        original_terrain=terrain_name,
                        properties=custom_properties,
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


def update_database_with_terrain(
    terrain_data: dict[str, dict], custom_terrains: list[Terrain]
) -> None:
    """
    Updates the database with terrain information and overrides.

    This function updates or creates Terrain entries in the database based on
    the processed terrain data and custom terrain overrides. It also links
    custom terrains to their corresponding provinces.

    Args:
    ----
    - terrain_data (dict[str, dict]): A dictionary mapping terrain names
      to their properties.
    - custom_terrains (list[Terrain]): A list of custom terrain objects
      created for overrides.

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - ValueError: If there's an issue with data processing or unexpected data format.
    """
    try:
        with session_scope() as session:
            for terrain_name, properties in terrain_data.items():
                original_terrain = session.exec(
                    select(Terrain).where(Terrain.name == terrain_name)
                ).first()
                if original_terrain:
                    original_terrain.properties = properties
                else:
                    original_terrain = Terrain(
                        name=terrain_name, original_terrain=terrain_name, properties=properties
                    )
                    session.add(original_terrain)

            for custom_terrain in custom_terrains:
                session.add(custom_terrain)
                province_id = int(
                    re.search(r"\d+", custom_terrain.properties["terrain_override"]).group()
                )
                province = session.exec(select(Province).where(Province.id == province_id)).first()
                if province:
                    province.terrain = custom_terrain
                else:
                    log.warning(
                        "Province with id %s not found for custom terrain %s.",
                        province_id,
                        custom_terrain.name,
                    )
    except (Exception, ValueError) as error:
        log.exception("Error updating database with terrain types.", exc_info=error)
        raise
