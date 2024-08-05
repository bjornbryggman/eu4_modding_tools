# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides database management functions and utilities for scaling operations.

This module offers functions for interacting with the SQLite database, including
creating the database schema and managing sessions. It also provides functions
for retrieving and generating reports of scaling factors for different resolutions.
"""

import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import structlog
from sqlmodel import Session, SQLModel, create_engine, select

from app.database.models import File, Property, ScalingFactor

# Initialize logger for this module
log = structlog.stdlib.get_logger(__name__)

# Database configuration
sqlite_url = "sqlite:///database/SQLite.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


# ========================================================== #
#                Generic Utility Functions                   #
# ========================================================== #


def create_database() -> None:
    """
    Create the database schema based on the defined SQLModel models.

    Process:
    -------
    -------
        - Uses the SQLModel.metadata.create_all() function to create the database schema based on the defined models.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - None.

    Exceptions:
    ----------
    ----------
        - None.
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Generator[Session, Any, None]:
    """
    Provides a transactional scope around a database session.

    Process:
    -------
    -------
        - Creates a new database session using the provided engine.
        - Yields the session to the caller, allowing for database operations within the context.
        - Automatically commits changes to the database if no exceptions occur.
        - Rolls back any changes if an exception is raised.
        - Closes the session regardless of whether changes were committed or rolled back.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - Generator[Session, Any, None]: A generator that yields a database session within the transactional scope.

    Exceptions:
    ----------
    ----------
        - Exception: If an unexpected error occurs during the session.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ============================================================= #
#             Functions used in 'scaling_script.py'             #
# ============================================================= #


def get_scaling_factors(file_path: str, resolution: str) -> dict[str, float]:
    """

    Retrieve scaling factors for a specific file and resolution from the database.

    Process:
    -------
    -------
        - Queries the database for scaling factors associated with the provided file path and resolution.
        - Returns a dictionary mapping scaling factor names to their mean values.

    Args:
    ----
    ----
        - file_path (str): The path to the file for which scaling factors are required.
        - resolution (str): The resolution for which scaling factors are required.

    Returns:
    -------
    -------
        - dict[str, float]: A dictionary containing scaling factor names as keys and their mean values as values.

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any unexpected errors during database interaction.

    """
    try:
        with session_scope() as session:
            scaling_factors = session.exec(
                select(ScalingFactor.name, ScalingFactor.mean)
                .join(Property)
                .join(File)
                .where(File.path == file_path, ScalingFactor.resolution == resolution)
            ).all()

            return dict(scaling_factors)

    except Exception as error:
        log.exception("An unexpected error occurred while retrieving scaling factors.", exc_info=error)


def generate_scaling_report(resolution: str) -> None:
    """
    Generate a report of scaling factors for a specified resolution.

    Process:
    -------
    -------
        - Queries the database for scaling factors associated with the specified resolution.
        - Organizes the retrieved data into a dictionary, grouping scaling factors by file.
        - Writes the structured report to a JSON file named according to the resolution.

    Args:
    ----
    ----
        - resolution (str): The target resolution for which the report is generated (e.g., "2K", "4K").

    Returns:
    -------
    -------
        - None: The function generates a JSON file and does not return any value.

    Exceptions:
    ----------
    ----------
        - Exception: Raised for any unexpected errors during database interaction or file writing.
    """
    try:
        with session_scope() as session:
            scaling_data = session.exec(
                select(
                    File.filename,
                    Property.name,
                    ScalingFactor.mean,
                    ScalingFactor.median,
                    ScalingFactor.std_dev,
                    ScalingFactor.min,
                    ScalingFactor.max,
                )
                .join(Property)
                .join(ScalingFactor)
                .where(ScalingFactor.resolution == resolution)
            ).all()

            # Create a dictionary to store scaling data for each file.
            report = {}
            for filename, prop_name, mean_factor, median_factor, std_dev, min_factor, max_factor in scaling_data:
                if filename not in report:
                    report[filename] = {}
                report[filename][prop_name] = {
                    "mean": mean_factor,
                    "median": median_factor,
                    "std_dev": std_dev,
                    "min": min_factor,
                    "max": max_factor,
                }

            # Write the report to a file.
            with Path.open(f"{resolution}_scaling_report.json", "w") as f:
                json.dump(report, f, indent=2)

            log.info("Scaling report for %s resolution generated.", resolution)

    except Exception as error:
        log.exception("An unexpected error occurred while generating the scaling report.", exc_info=error)
