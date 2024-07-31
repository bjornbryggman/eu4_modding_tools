# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Insert succinct one-liner here (no more than 60 characters).

Insert more descriptive explanation of the module here, max 4 rows, max 100 characters per row.
"""

import structlog
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.database.models import Province
from app.utils import db_utils

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


# ================================================================= #
#             Database Relationship Management Functions            #
# ================================================================= #


def set_geographical_relationships() -> None:
    """
    Sets relationships between geographical entities in the database.

    This function iterates through all provinces in the database and sets up
    proper relationships between provinces, areas, regions, superregions and
    continents based on their respective foreign keys.

    Args:
    ----
    - None.

    Returns:
    -------
    - None.

    Raises:
    ------
    - Exception: If an unexpected error occurs.
    - SQLAlchemyError: If there's an issue with database operations.
    """
    try:
        with db_utils.session_scope() as session:
            # Fetch all provinces.
            provinces = session.exec(select(Province)).all()

            for province in provinces:
                if province.area:
                    # Set Region and SuperRegion for Province.
                    province.region = province.area.region
                    province.superregion = province.area.region.superregion

                    # Set Continent for Area, Region, and SuperRegion if missing.
                    if province.area and not province.area.continent:
                        province.area.continent = province.continent
                    if province.region and not province.region.continent:
                        province.region.continent = province.continent
                    if province.superregion and not province.superregion.continent:
                        province.superregion.continent = province.continent

                    # Set SuperRegion for Area if missing.
                    if province.area and not province.area.superregion:
                        province.area.superregion = province.superregion

    except SQLAlchemyError as error:
        log.exception("Database error.", exc_info=error)
        raise
    except Exception as error:
        log.exception("An unexpected error occured.", exc_info=error)
        raise

    log.info("Database relationships set successfully.")
