# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides database functionality for storing and retrieving data.

It utilizes SQLite and SQLModel for database management.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import structlog
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# Construct the SQLite URL.
sqlite_url = "sqlite:///database/SQLite.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)


# =========================================================#
#                Database Model Definitions                #
# =========================================================#


class Continent(SQLModel, table=True):
    """
    Represents a continent in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the continent.
    - name (str): The name of the continent (e.g., "europe").
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # One-to-many relationships.
    superregions: list["Region"] = Relationship(back_populates="continent")
    regions: list["Region"] = Relationship(back_populates="continent")
    areas: list["Area"] = Relationship(back_populates="continent")
    provinces: list["Province"] = Relationship(back_populates="continent")


class SuperRegion(SQLModel, table=True):
    """
    Represents a super-region in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the super-region.
    - name (str): The name of the super-region (e.g., "europe_superregion").
    - continent_id (int): Foreign key referencing the continent this super-region belongs to.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Foreign keys for relationships.
    continent_id: int | None = Field(default=None, foreign_key="continent.id")

    # One-to-one relationships.
    continent: Continent | None = Relationship(back_populates="superregions")

    # One-to-many relationships.
    regions: list["Region"] = Relationship(back_populates="superregion")
    areas: list["Area"] = Relationship(back_populates="superregion")
    provinces: list["Province"] = Relationship(back_populates="superregion")


class Region(SQLModel, table=True):
    """
    Represents a region in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the region.
    - name (str): The name of the region (e.g., "scandinavia_region").
    - superregion_id (int): Foreign key referencing the super-region this region belongs to.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # e.g., "scandinavia_region"

    # Foreign keys for relationships.
    continent_id: int | None = Field(default=None, foreign_key="continent.id")
    superregion_id: int | None = Field(default=None, foreign_key="superregion.id")

    # One-to-one relationships.
    continent: Continent | None = Relationship(back_populates="superregions")
    superregion: SuperRegion | None = Relationship(back_populates="regions")

    # One-to-many relationships.
    areas: list["Area"] = Relationship(back_populates="region")
    provinces: list["Province"] = Relationship(back_populates="region")


class Area(SQLModel, table=True):
    """
    Represents an area within a region in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the area.
    - name (str): The name of the area (e.g., "svealand_area").
    - region_id (int): Foreign key referencing the region this area belongs to.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Foreign keys for relationships.
    continent_id: int | None = Field(default=None, foreign_key="continent.id")
    superregion_id: int | None = Field(default=None, foreign_key="superregion.id")
    region_id: int | None = Field(default=None, foreign_key="region.id")

    # One-to-one relationships.
    continent: Continent | None = Relationship(back_populates="areas")
    superregion: SuperRegion | None = Relationship(back_populates="areas")
    region: Region | None = Relationship(back_populates="areas")

    # One-to-many relationships.
    provinces: list["Province"] = Relationship(back_populates="area")


class Climate(SQLModel, table=True):
    """
    Represents a climate type in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the climate type.
    - name (str): The name of the climate type (e.g., "tropical", "arid").
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # One-to-many relationships.
    provinces: list["Province"] = Relationship(back_populates="climate")


class Terrain(SQLModel, table=True):
    """
    Represents a terrain type in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the terrain type.
    - name (str): The name of the terrain type (e.g., "farmlands", "mountains").
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # One-to-many relationships.
    provinces: list["Province"] = Relationship(back_populates="terrain")


class Province(SQLModel, table=True):
    """
    Represents a province in EU4.

    Attributes:
    ----------
    - id (int): The primary key of the province (same as the province ID in game files).
    - name (str): The name of the province (e.g., "Stockholm").
    - area_id (int): Foreign key referencing the area this province belongs to.
    - climate_id (int): Foreign key referencing the climate type of this province.
    - terrain_id (int): Foreign key referencing the terrain type of this province.
    - image_path (str): The path to the generated image for this province.
    """

    id: int = Field(primary_key=True)
    name: str
    prompt: str | None = Field(default=None)
    image_url: str | None = Field(default=None)

    # Foreign keys for relationships.
    continent_id: int | None = Field(default=None, foreign_key="continent.id")
    superregion_id: int | None = Field(default=None, foreign_key="superregion.id")
    region_id: int | None = Field(default=None, foreign_key="region.id")
    area_id: int | None = Field(default=None, foreign_key="area.id")
    climate_id: int | None = Field(default=None, foreign_key="climate.id")
    terrain_id: int | None = Field(default=None, foreign_key="terrain.id")

    # One-to-one relationships.
    continent: Continent | None = Relationship(back_populates="provinces")
    superregion: SuperRegion | None = Relationship(back_populates="provinces")
    region: Region | None = Relationship(back_populates="provinces")
    area: Area | None = Relationship(back_populates="provinces")
    climate: Climate | None = Relationship(back_populates="provinces")
    terrain: Terrain | None = Relationship(back_populates="provinces")


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
