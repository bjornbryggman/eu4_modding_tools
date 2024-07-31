# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 60 characters).

Insert more descriptive explanation of the module here, max 4 rows, max 100 characters per row.
"""

import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import structlog
from sqlmodel import Session, SQLModel, create_engine, select

from app.database.models import File, Property, ScalingFactor

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# Construct the SQLite URL.
sqlite_url = "sqlite:///database/SQLite.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)


# ========================================================== #
#                Generic Utility Functions                   #
# ========================================================== #


def create_database() -> None:
    """
    Creates the database tables if they don't exist.

    Args:
    ----
    - None

    Returns:
    -------
    - None
    """
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Generator[Session, Any, None]:
    """
    Provides a transactional scope around a database session.

    This context manager creates a new database session, yields it to the
    caller, and automatically commits changes or rolls back in case of
    exceptions.

    Args:
    ----
    - None.

    Returns:
    -------
    - Session: A database session within the transactional scope.

    Raises:
    ------
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
    Retrieves scaling factors for a given file and resolution from the database.

    It uses SQLModel's 'select' and 'join' to query the database
    and returns a dictionary of scaling factors.

    Args:
    ----
    - file_path (str): The path to the file.
    - resolution (str): The target resolution (e.g., "2K", "4K").

    Returns:
    -------
    - dict[str, float]: A dictionary where keys are property names and values are
    the corresponding scaling factors for the specified resolution.

    Raises:
    ------
    - Exception: If an error occurs during database interaction.
    """
    try:
        with Session(engine) as session:
            scaling_factors = session.exec(
                select(ScalingFactor.name, ScalingFactor.mean)
                .join(Property)
                .join(File)
                .where(File.path == file_path, ScalingFactor.resolution == resolution)
            ).all()

            return dict(scaling_factors)

    except Exception as error:
        log.exception(
            "An unexpected error occurred while retrieving scaling factors.", exc_info=error
        )


def generate_scaling_report(resolution: str) -> None:
    """
    Generates a report of scaling factors for the specified resolution.

    It queries the database, retrieves the scaling data, and writes it to a JSON file.

    Args:
    ----
    - resolution (str): The target resolution (e.g., "2K", "4K").

    Returns:
    -------
    - None
    """
    try:
        with Session(engine) as session:
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
            for (
                filename,
                prop_name,
                mean_factor,
                median_factor,
                std_dev,
                min_factor,
                max_factor,
            ) in scaling_data:
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
        log.exception(
            "An unexpected error occurred while generating the scaling report.", exc_info=error
        )
