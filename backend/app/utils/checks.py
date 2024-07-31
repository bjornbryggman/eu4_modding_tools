# Copyright 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Something.

Soosklkads.
"""

import importlib
import shutil

import structlog

log = structlog.stdlib.get_logger(__name__)


def check_for_texconv_path() -> bool:
    texconv_path = shutil.which("texconv")

    if not texconv_path:
        log.error("Texconv not found in PATH. Please ensure it's correctly installed.")
        return False

    return True


def check_for_wand_package() -> bool:
    try:
        importlib.import_module("wand")

    except ImportError as error:
        log.exception(
            "Wand library not found. Please ensure it's correctly installed.", exc_info=error
        )
        return False

    else:
        return True
