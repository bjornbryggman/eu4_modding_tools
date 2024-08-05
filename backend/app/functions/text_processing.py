# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides functions for scaling positional values in text files and calculating scaling factors.

This module offers functionalities for scaling positional values in text files based on
pre-calculated scaling factors stored in a database. It also provides functions for
calculating scaling factors by comparing original text files with their scaled
versions (2K and 4K). The module utilizes multiprocessing to speed up these operations
by running them in parallel.
"""

import multiprocessing
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import mean, median, stdev

import structlog
from sqlmodel import Session, select

from app.database.models import File, OriginalValue, Property, ScalingFactor, engine
from app.utils import file_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# =============================== #
#        Utility Functions        #
# =============================== #


def apply_scaling_factors(content: str, original_values: dict[str, list[float]], resolution: str) -> str:
    """
    Apply scaling factors to positional values within text content.

    Process:
    -------
    -------
        - Retrieves scaling factors from the database based on the target resolution and properties present in the content.
        - Iterates through each positional value in the content.
        - Applies scaling to the value if a corresponding scaling factor exists and the original value is not '-1', contains '%', '@', or '10s'.
        - Returns the updated content with scaled positional values.

    Args:
    ----
    ----
        - content (str): The content of the text file to be processed.
        - original_values (dict[str, list[float]]): A dictionary containing the original positional values for the file.
        - resolution (str): The target resolution for scaling (e.g., "2K", "4K").

    Returns:
    -------
    -------
        - str: The content with scaled positional values, or the original content if an error occurs.

    Exceptions:
    ----------
    ----------
        - ValueError: Raised if an invalid scaling factor is provided.
        - Exception: Raised if an error occurs during database interaction or other unexpected errors.
    """
    pattern = r"(\b(?:x|y|width|height|maxWidth|maxHeight|size|borderSize|spacing|position|pos_x)\b)\s*=\s*({[^}]+}|-?\d+(?:\.\d+)?%?|[^}\n]+)"

    scaling_factors = {}

    try:
        with Session(engine) as session:
            # Prefetch scaling factors for properties present in the file.
            properties = original_values.keys()
            scaling_factors_query = (
                session.exec(ScalingFactor.mean, Property.name)
                .join(Property, ScalingFactor.property_id == Property.id)
                .filter(ScalingFactor.resolution == resolution, Property.name.in_(properties))
            )
            scaling_factors = {name: mean for mean, name in scaling_factors_query}

        # Apply scaling to content.
        def replacer(match: re.Match) -> str:
            prop_name = match.group(1).lower()
            if prop_name in scaling_factors:
                return scale_values(match, scaling_factors[prop_name])
            return match.group(0)

        updated_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)

    # Return original content if an error occurs.
    except ValueError as error:
        log.exception("Invalid scaling factor provided.", exc_info=error)
        return content
    except Exception as error:
        log.exception("An unexpected error occurred while applying scaling factors.", exc_info=error)
        return content

    return updated_content


def calculate_property_scaling(
    original: dict[str, list[float]], scaled: dict[str, list[float]]
) -> dict[str, dict[str, float]]:
    """
    Calculate scaling factors for individual properties based on original and scaled positional values.

    Process:
    -------
    -------
        - Iterates through each property in the original values.
        - Checks if the property exists in both original and scaled values and if they have the same length.
        - Calculates scaling factors by dividing scaled values by corresponding original values, excluding cases where the original value is 0.
        - Calculates statistical measures (mean, median, standard deviation, minimum, maximum) for the scaling factors if they are found.
        - If no scaling factors are found for a property, sets all statistics to None.

    Args:
    ----
    ----
        - original (dict[str, list[float]]): Positional values from the original file.
        - scaled (dict[str, list[float]]): Positional values from the scaled file.

    Returns:
    -------
    -------
        - dict[str, dict[str, float]]: A dictionary where keys are property names and values are dictionaries containing scaling factor statistics (mean, median, standard deviation, minimum, maximum).

    Exceptions:
    ----------
    ----------
        - None.
    """
    scaling = {}
    for prop, original_values in original.items():
        # Check if the property exists in both original and scaled values.
        if prop in scaled and len(original_values) == len(scaled[prop]):
            # Calculate scaling factors for each property.
            factors = [s / o for o, s in zip(original_values, scaled[prop], strict=True) if o != 0]

            # If factors are found, calculate statistics.
            if factors:
                scaling[prop] = {
                    "mean": mean(factors),
                    "median": median(factors),
                    "std_dev": stdev(factors) if len(factors) > 1 else 0,
                    "min": min(factors),
                    "max": max(factors),
                }

            # Otherwise, set all statistics to None.
            else:
                scaling[prop] = {"mean": None, "median": None, "std_dev": None, "min": None, "max": None}
    return scaling


def extract_positional_values(file_path: Path) -> dict[str, list[float]]:
    """
    Extract positional values from a text file.

    Process:
    -------
    -------
        - Reads the content of the specified file.
        - Uses a regular expression to find property-value pairs matching positional properties.
        - Extracts property names and numeric values, converting them to floats.
        - Stores the extracted values in a dictionary, grouping them by property name.

    Args:
    ----
    ----
        - file_path (Path): The path to the text file containing positional values.

    Returns:
    -------
    -------
        - dict[str, list[float]]: A dictionary where keys are property names and values are lists of corresponding positional values.

    Exceptions:
    ----------
    ----------
        - None.
    """
    values = {}
    pattern = r"(\b(?:x|y|width|height|maxWidth|maxHeight|size|borderSize|spacing|position|pos_x)\b)\s*=\s*({[^}]+}|-?\d+(?:\.\d+)?%?|[^}\n]+)"

    content = file_utils.read_file(file_path)
    if content is None:
        return None

    for match in re.finditer(pattern, content, flags=re.IGNORECASE):
        # Extract property name and value.
        prop, value = match.groups()
        # If value is a digit, add it to the dictionary.
        if value.isdigit():
            if prop not in values:
                values[prop] = []
            values[prop].append(float(value))
    return values


def scale_values(match: re.Match, scale_factor: float) -> str:
    """
    Scales a matched value according to the scaling factor.

    Process:
    -------
    -------
        - Extracts the property and value from the regex match object.
        - Determines if the value should be scaled based on specific conditions.
        - If scaling is required, applies the scaling factor to the value.
        - Handles both simple and complex size formats.
        - Returns the scaled value in the format "property = scaled_value".

    Args:
    ----
    ----
        - match (re.Match): A regex match object containing the property and value.
        - scale_factor (float): The scaling factor to apply.

    Returns:
    -------
    -------
        - str: A string with the scaled value in the format "property = scaled_value",
            or the original string if the value should not be scaled.

    Exceptions:
    ----------
    ----------
        - None.
    """
    prop = match.group(1)
    value = match.group(2).strip()

    # Return the original string if value contains '%', '@', '10s', or is "-1".
    if any(x in value for x in ["%", "@", "10s"]) or value == "-1":
        return f"{prop} = {value}"

    # Handle complex size format, e.g.: size = {x = 5 y = 5}.
    if value.startswith("{"):
        return f"{prop} = " + re.sub(
            r"([\w_]+)\s*=\s*(-?\d+(?:\.\d+)?)",
            lambda m: f"{m.group(1)} = {
                m.group(2)
                if m.group(2) == "-1" or any(x in m.group(2) for x in ["%", "@", "10s"])
                else round(float(m.group(2)) * scale_factor)
            }",
            value,
        )

    # Handle simple size format, e.g.: size = 17.
    try:
        scaled_value = round(float(value) * scale_factor)

    # Return original if not a number.
    except ValueError:
        return f"{prop} = {value}"
    else:
        return f"{prop} = {scaled_value}"


def store_scaling_factors_in_database(
    original_file: Path,
    original_values: dict[str, list[float]],
    scale_2k: dict[str, dict[str, float]],
    scale_4k: dict[str, dict[str, float]],
) -> None:
    """
    Stores original values and scaling factors in the database for a given file.

    Process:
    -------
    -------
        - Creates or retrieves a File record in the database based on the provided file path.
        - Iterates through the original values and scaling factors for each property.
        - Creates or retrieves Property records for each property.
        - Stores original values as OriginalValue records associated with the corresponding Property.
        - Stores scaling factors for 2K resolution as ScalingFactor records associated with the corresponding Property.
        - Stores scaling factors for 4K resolution as ScalingFactor records associated with the corresponding Property.

    Args:
    ----
    ----
        - original_file (Path): Path to the original text file.
        - original_values (dict[str, list[float]]): Original positional values for the file.
        - scale_2k (dict[str, dict[str, float]]): Scaling factors for 2K resolution.
        - scale_4k (dict[str, dict[str, float]]): Scaling factors for 4K resolution.

    Returns:
    -------
    -------
        - None
    """
    with Session(engine) as session:
        # Create or get the File record.
        file_record = session.exec(select(File).where(File.path == str(original_file))).first()
        if not file_record:
            file_record = File(filename=original_file.name, path=str(original_file))
            session.add(file_record)
            session.commit()
            session.refresh(file_record)

        # Store original values and scaling factors for each property.
        original_value_records = []
        scaling_factor_2k_records = []
        scaling_factor_4k_records = []
        for prop, values in original_values.items():
            property_record = _create_or_get_property(session, prop, file_record.id)

            # Store original values
            original_value_records.extend([
                OriginalValue(property_id=property_record.id, value=value) for value in values
            ])

            # Store 2K scaling factors
            if prop in scale_2k:
                scaling_factor_2k_records.append(
                    ScalingFactor(property_id=property_record.id, resolution="2K", **scale_2k[prop])
                )

            # Store 4K scaling factors
            if prop in scale_4k:
                scaling_factor_4k_records.append(
                    ScalingFactor(property_id=property_record.id, resolution="4K", **scale_4k[prop])
                )

        session.add_all(original_value_records)
        session.add_all(scaling_factor_2k_records)
        session.add_all(scaling_factor_4k_records)
        session.commit()


def _create_or_get_property(session: Session, prop: str, file_id: int) -> Property:
    """
    Create or retrieve a Property record in the database.

    Process:
    -------
    -------
        - Queries the database for an existing Property record with the given name and file ID.
        - If a record is found, it is returned.
        - If no record is found, a new Property record is created, added to the session, committed, and refreshed.
        - The newly created or retrieved Property record is returned.

    Args:
    ----
    ----
        - session (Session): The database session.
        - prop (str): The property name.
        - file_id (int): The ID of the File record.

    Returns:
    -------
    -------
        - Property: The Property record.

    Exceptions:
    ----------
    ----------
        - None.
    """
    property_record = session.exec(select(Property).where(Property.name == prop, Property.file_id == file_id)).first()
    if not property_record:
        property_record = Property(name=prop, file_id=file_id)
        session.add(property_record)
        session.commit()
        session.refresh(property_record)
    return property_record


# =========================================================== #
#        Worker function for scaling positional values        #
# =========================================================== #


def scale_positional_values_worker(args: tuple[Path, Path, Path, str]) -> None:
    """
    Scales positional values in a text file based on stored scaling factors.

    Process:
    -------
    -------
        - Reads the content of the input file.
        - Extracts positional values from the file.
        - Applies scaling factors based on the resolution.
        - Writes the scaled content to the output file.

    Args:
    ----
    ----
        - args (tuple[Path, Path, Path, str]): A tuple containing the input directory, output directory, input file path, and target resolution.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: If an error occurs during file processing or database interaction.
    """
    input_directory, output_directory, input_file, resolution = args
    try:
        # Read the content of a file.
        content = file_utils.read_file(input_file)

        if content is not None:
            # Extract positional values from the file.
            original_values = extract_positional_values(input_file)

            # Apply scaling factors to the values and return them.
            scaled_content = apply_scaling_factors(content, original_values, resolution)

            if scaled_content is not None:
                # Calculate the relative output path to maintain directory structure.
                relative_path = input_file.relative_to(input_directory)
                output_path = output_directory / relative_path.parent

                # Write the scaled content to the output file
                output_path.mkdir(parents=True, exist_ok=True)
                output_file = output_path / input_file.name
                file_utils.write_file(output_file, scaled_content)
                log.debug("Updated %s with scaled values.", output_file.name)

            else:
                log.debug(" No changes have been made to %s.", input_file.name)

        # Skip to the next file if no content is found.
        log.error("No content found in file: %s", input_file)

    except Exception as error:
        log.exception("An unexpected error occurred while scaling file: %s", input_file, exc_info=error)
        raise


# =========================================================== #
#        Caller function for scaling positional values        #
# =========================================================== #


def scale_positional_values(input_directory: Path, output_directory: Path, input_format: str, resolution: str) -> None:
    """
    Scales positional values in text files according to a specified scaling factor.

    Process:
    -------
    -------
        - Iterates through text files in the input directory.
        - For each file, applies a scaling factor to specific positional attributes.
        - Writes the modified content to the output directory.
        - Uses a ProcessPoolExecutor to parallelize the processing of files.

    Args:
    ----
    ----
        - input_directory (Path): The directory containing the text files to process.
        - output_directory (Path): The directory to output processed files.
        - input_format (str): The file extension of input text files (e.g., 'xml', 'ui').
        - resolution (str): The target resolution (e.g., "2K", "4K").

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If no text files are found in the input directory.
        - ValueError: If an invalid scaling factor is provided.
        - Exception: If an unexpected error occurs during the process execution.
    """
    log.info("Scaling positional values in text files for %s resolution...", resolution)

    try:
        # Use a ProcessPoolExecutor to run the worker function in parallel.
        input_files = list(input_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [(input_directory, output_directory, input_file, resolution) for input_file in input_files]
            results = list(executor.map(scale_positional_values_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions.
            for _ in results:
                pass

    except FileNotFoundError as error:
        log.exception("No %s files found in %s.", input_format.upper(), input_directory, exc_info=error)
        sys.exit()
    except ValueError as error:
        log.exception("Value error, check the scaling factor.", exc_info=error)
        sys.exit()
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


# ============================================================= #
#        Worker function for comparing positional values        #
# ============================================================= #


def calculate_scaling_factors_worker(args: tuple[Path, Path, Path]) -> None:
    """
    Worker function for calculating scaling factors and storing them in the database.

    Process:
    -------
    -------
        - Checks if all input files exist. Skips processing if any are missing.
        - Extracts positional values from the original and scaled files.
        - Skips processing if any extracted values are None.
        - Calculates scaling factors for 2K and 4K resolutions based on the extracted values.
        - Stores the calculated scaling factors in the database.

    Args:
    ----
    ----
        - args (tuple[Path, Path, Path]): A tuple containing:
            - original_file (Path): Path to the original text file.
            - scaled_2k_file (Path): Path to the 2K scaled version of the file.
            - scaled_4k_file (Path): Path to the 4K scaled version of the file.

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - Exception: If an error occurs during file processing or calculation.
    """
    original_file, scaled_2k_file, scaled_4k_file = args

    try:
        # Check if all relevant files exist, skip if any are missing.
        if not all(file.exists() for file in [original_file, scaled_2k_file, scaled_4k_file]):
            log.warning("Skipping %s due to missing files.", original_file.name)
            return

        # Extract positional values from each file.
        original_values = extract_positional_values(original_file)
        scaled_2k_values = extract_positional_values(scaled_2k_file)
        scaled_4k_values = extract_positional_values(scaled_4k_file)

        # Check if any content is None, skip if so.
        if any(values is None for values in [original_values, scaled_2k_values, scaled_4k_values]):
            log.warning("Skipping file %s due to missing content in one or more versions.", original_file)
            return

        # Calculate scaling factors for 2K and 4K resolutions.
        scale_2k = calculate_property_scaling(original_values, scaled_2k_values)
        scale_4k = calculate_property_scaling(original_values, scaled_4k_values)

        # Store results in the database
        store_scaling_factors_in_database(original_file, original_values, scale_2k, scale_4k)

        log.info("Stored scaling factors for %s in the database.", original_file.name)

    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
        raise


# ============================================================= #
#        Caller function for comparing positional values        #
# ============================================================= #


def calculate_scaling_factors(
    original_directory: Path, scaled_2k_directory: Path, scaled_4k_directory: Path, input_format: str
) -> None:
    """
    Calculate scaling factors for text files by comparison with 2K and 4K counterparts.

    Process:
    -------
    -------
        - Iterates through original text files in the provided directory.
        - For each file, it retrieves its 2K and 4K scaled versions.
        - Calculates scaling factors for individual properties and overall scaling factors for each resolution.
        - Stores the calculated scaling factors in a SQLite database.

    Args:
    ----
    ----
        - original_directory (Path): The directory containing the original GUI files.
        - scaled_2k_directory (Path): The directory containing the 2K scaled GUI files.
        - scaled_4k_directory (Path): The directory containing the 4K scaled GUI files.
        - input_format (str): The file extension of input GUI files (e.g., 'gui', 'xml').

    Returns:
    -------
    -------
        - None

    Exceptions:
    ----------
    ----------
        - FileNotFoundError: If no matching files are found in the directories.
        - Exception: If an unexpected error occurs during processing.
    """
    log.info("Calculating scaling factors for %s files...", input_format.lower())

    try:
        # Use a ProcessPoolExecutor to run the worker function in parallel.
        original_files = list(original_directory.rglob(f"*.{input_format.lower()}"))
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            args = [
                (
                    original_file,
                    scaled_2k_directory / original_file.relative_to(original_directory),
                    scaled_4k_directory / original_file.relative_to(original_directory),
                )
                # Only include files that have both 2K and 4K scaled versions.
                for original_file in original_files
                if (scaled_2k_directory / original_file.relative_to(original_directory)).exists()
                and (scaled_4k_directory / original_file.relative_to(original_directory)).exists()
            ]
            results = list(executor.map(calculate_scaling_factors_worker, args, chunksize=10))

            # Consume the iterator to trigger any exceptions.
            for _ in results:
                pass

        log.info("Scaling factors calculated and stored in the database.")

    except FileNotFoundError as error:
        log.exception("No matching %s files found in the directories.", input_format.upper(), exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred while calculating scaling factors.", exc_info=error)
