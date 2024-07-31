# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 60 characters).

Insert more descriptive explanation of the module here, max 4 rows, max 100 characters per row.
"""

import re
from pathlib import Path

import structlog

from app.utils.file_utils import read_file, write_file

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


def modify_terrain_file(
    input_file: Path, regex_pattern: str, terrain_data: dict[str, dict]
) -> None:
    """
    Modifies the terrain override information in the terrain.txt file.

    This function modifies the terrain.txt file by replacing the terrain
    override information for each terrain type with the updated values
    from the processed terrain data.

    Args:
    ----
    - input_file (Path): The path to the terrain.txt file.
    - regex_pattern (str): The regular expression pattern to match entity definitions.
    - terrain_data (dict[str, dict]): A dictionary mapping terrain names
      to their properties, including updated terrain overrides.

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
        categories_start, categories_content, categories_end = categories_match.groups()

        for terrain_name, terrain_info in terrain_data.items():
            terrain_match = re.search(
                rf"({terrain_name}\s*=\s*{{)([^}}]+)(}})", categories_content, re.DOTALL
            )
            if terrain_match:
                terrain_start, terrain_content, terrain_end = terrain_match.groups()
                terrain_override = terrain_info["terrain_override"]
                updated_terrain_content = re.sub(
                    r"terrain_override\s*=\s*{[^}]*}",
                    f"terrain_override = {terrain_override}",
                    terrain_content,
                )
                categories_content = categories_content.replace(
                    terrain_match.group(0), f"{terrain_start}{updated_terrain_content}{terrain_end}"
                )
        updated_content = f"{categories_start}{categories_content}{categories_end}"
        write_file(input_file, updated_content)

    except (Exception, OSError, PermissionError, ValueError) as error:
        log.exception("Error processing %s.", input_file, exc_info=error)
        raise
    else:
        log.debug("Updated terrain information for %s provinces.", len(categories_match))
