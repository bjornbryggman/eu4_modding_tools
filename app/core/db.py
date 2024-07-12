# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides database functionality for storing and retrieving data.

It utilizes SQLite and SQLModel for database management.
"""

from sqlmodel import Field, SQLModel, create_engine

sqlite_url = "sqlite:///database/SQLite.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)


# =========================================================#
#                Database Model Definitions                #
# =========================================================#


class File(SQLModel, table=True):
    """
    Represents a file in the database.

    Attributes:
    ----------
    - id (int): The primary key of the file.
    - filename (str): The name of the file.
    - path (str): The path to the file.
    """
    id: int | None = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    path: str = Field(index=True)


class Property(SQLModel, table=True):
    """
    Represents a property within a file.

    Attributes:
    ----------
    - id (int): The primary key of the property.
    - name (str): The name of the property (e.g., "x", "y", "width").
    - file_id (int): Foreign key referencing the file this property belongs to.
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    file_id: int = Field(foreign_key="file.id")


class OriginalValue(SQLModel, table=True):
    """
    Represents an original value for a property in a file.

    Attributes:
    ----------
    - id (int): The primary key of the original value.
    - property_id (int): Foreign key referencing the property this value belongs to.
    - value (float): The original value of the property.
    """
    id: int | None = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    value: float = Field(index=True)


class ScalingFactor(SQLModel, table=True):
    """
    Represents a scaling factor for a property at a specific resolution.

    Attributes:
    ----------
    - id (int): The primary key of the scaling factor.
    - property_id (int): Foreign key referencing the property this factor applies to.
    - resolution (str): The resolution (e.g., "2K", "4K").
    - mean (float): The mean scaling factor.
    - median (float): The median scaling factor.
    - std_dev (float): The standard deviation of scaling factors.
    - min (float): The minimum scaling factor.
    - max (float): The maximum scaling factor.
    """
    id: int | None = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")
    resolution: str = Field(index=True)
    mean: float | None = Field(default=None)
    median: float | None = Field(default=None)
    std_dev: float | None = Field(default=None)
    min: float | None = Field(default=None)
    max: float | None = Field(default=None)


# ============================================================#
#                Database Utility Functions                  #
# ============================================================#


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
