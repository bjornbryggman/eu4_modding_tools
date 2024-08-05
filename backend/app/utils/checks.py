# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Provides utility functions for checking the availability of external dependencies.

This module contains functions to check if the required external tools and libraries
are available in the system.
"""

import importlib
import shutil

import structlog

log = structlog.stdlib.get_logger(__name__)


# ========================================= #
#                 Texconv                   #
# ========================================= #


def check_for_texconv_path() -> bool:
    """
    Check if the 'texconv' executable is available in the system PATH.

    Process:
    -------
    -------
        - Uses `shutil.which` to locate the 'texconv' executable in the system PATH.
        - If found, returns True.
        - If not found, logs an error message and returns False.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - bool: True if 'texconv' is found in the PATH, False otherwise.

    Exceptions:
    ----------
    ----------
        - None.
    """
    texconv_path = shutil.which("texconv")

    if not texconv_path:
        log.error("Texconv not found in PATH. Please ensure it's correctly installed.")
        return False

    return True


# =================================================== #
#                 ImageMagick (Wand)                  #
# =================================================== #


def check_for_wand_package() -> bool:
    """
    Check if the 'wand' package is installed.

    Process:
    -------
    -------
        - Attempts to import the 'wand' module.
        - If successful, returns True, indicating the package is installed.
        - If an ImportError is raised, logs an error message and returns False.

    Args:
    ----
    ----
        - None.

    Returns:
    -------
    -------
        - bool: True if the 'wand' package is installed, False otherwise.

    Exceptions:
    ----------
    ----------
        - ImportError: Raised if the 'wand' package is not found.
    """
    try:
        importlib.import_module("wand")

    except ImportError as error:
        log.exception("Wand library not found. Please ensure it's correctly installed.", exc_info=error)
        return False

    else:
        return True
