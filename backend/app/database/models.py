# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
This module provides database functionality for storing and retrieving data.

It utilizes SQLite and SQLModel for database management.
"""

import structlog
from sqlmodel import Field, Relationship, SQLModel, create_engine

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)

# Construct the SQLite URL.
sqlite_url = "sqlite:///database/SQLite.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)


# ============================================================= #
#               Models used in 'events_script.py'               #
# ============================================================= #

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    origin: str
    title: str = Field(index=True)
    desc: str
    picture: str = Field(index=True)


class OriginalEventLocalisation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="event.id")
    event_title: str
    event_description: str


class GeneratedEventLocalisation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="event.id")
    spellchecked_title: str = Field(default=None)
    spellchecked_description: str = Field(default=None)


class OriginalEventPicture(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="event.id")
    original_picture: str = Field(index=True)


class GeneratedEventPicture(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="event.id")
    prompt: str
    generated_picture: str = Field(index=True)


# =============================================================== #
#               Models used for 'scaling_script.py'               #
# =============================================================== #


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
    - property_id (int): Foreign key referencing the associated property id.
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
    - property_id (int): Foreign key referencing the associated property id.
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


# =============================================================== #
#               Models used for 'terrain_script.py'               #
# =============================================================== #


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
