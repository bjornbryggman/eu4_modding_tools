# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"something."

# ====================================================#
#                     File Utilities                  #
# ====================================================#

import base64
import shutil
from pathlib import Path

import structlog

log = structlog.stdlib.get_logger(__name__)

# ====================================================#
#                 Read file content                   #
# ====================================================#


def read_file(file_path: Path) -> str:
    """
    Reads the content of a file.

    Args:
    ----
    ----
    file_path (Path): The path to the file to read.

    Returns:
    -------
    -------
    str: The content of the file.

    """
    try:
        with file_path.open("r") as file:
            file.read()

    except FileNotFoundError as error:
        log.exception("No file found.", exc_info=error)
    except PermissionError as error:
        log.exception("Permission denied", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


# ====================================================#
#                Write file content                   #
# ====================================================#


def write_file(file_path: Path, content: str) -> None:
    """
    Writes content to a file.

    Args:
    ----
    file_path (Path): The path to the file to write.
    content (str): The content to write to the file.

    Raises:
    ------
    OSError: If an I/O error occurs while writing to the file.
    """
    try:
        with file_path.open("w") as file:
            file.write(content)

    except PermissionError as error:
        log.exception("Permission denied", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


def preprocess_text_formatting(prefix: str, file_path: str, suffix: str) -> str:
    string = str
    read_file(file_path)
    write_file(string, read_file)

    content = f"""{prefix}{string}{suffix}"""

    return content


def get_base64_encoded_image(file_path):
    with open(file_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode("utf-8")

    return base64_string


def create_directory(directory) -> None:
    log.debug("Checking if directory %s exists.", directory)

    try:
        directory.mkdir(parents=True, exist_ok=True)
        log.debug("Directory %s exists or has been created.", directory)

    except PermissionError as error:
        log.exception("Permission denied", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)


def delete_directory(directory) -> None:
    log.debug("Deleting %s directory.", directory)

    try:
        if directory.exists():
            shutil.rmtree(directory)
            log.debug("Deleted the %s directory.", directory)

    except PermissionError as error:
        log.exception("Permission denied", exc_info=error)
    except OSError as error:
        log.exception("I/O error occurred.", exc_info=error)
    except Exception as error:
        log.exception("An unexpected error occurred.", exc_info=error)
