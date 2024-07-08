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
        file_path (Path): The path to the file to read.

    Returns:
    -------
        str: The content of the file, or None if an error occurred.

    Raises:
    ------
        PermissionError: If the process lacks permission to read the file.
        OSError: If an I/O related error occurs during file reading.
        Exception: For any other unexpected errors during the read operation.
    """
    encodings = ['utf-8', 'latin-1', 'ascii']

    # Use 'utf-8' encoding as a default, with 'latin-1' and 'ascii' as fallbacks.
    for encoding in encodings:
        try:
            with file_path.open("r", encoding=encoding) as file:
                return file.read()

        except UnicodeDecodeError:
            continue
        except PermissionError as error:
            log.exception("Permission denied: %s", file_path, exc_info=error)
        except OSError as error:
            log.exception("I/O error occurred: %s", file_path, exc_info=error)
        except Exception as error:
            log.exception("An unexpected error occurred: %s", file_path, exc_info=error)
        return None

    # If all text encodings fail, try to read as binary.
    try:
        with file_path.open("rb") as file:
            return file.read().decode('utf-8', errors='replace')

    except Exception as error:
        log.exception("Failed to read file even in binary mode: %s", file_path, exc_info=error)
        return None



# ====================================================#
#                Write file content                   #
# ====================================================#


def write_file(file_path: Path, content: str) -> bool:
    """
    Writes content to a file.

    Args:
    ----
        file_path (Path): The path to the file to write.
        content (str): The content to write to the file.

    Returns:
    -------
        bool: True if write was successful, False otherwise.

    Raises:
    ------
        PermissionError: If the process lacks permission to write to the file.
        OSError: If an I/O related error occurs during file writing.
        Exception: For any other unexpected errors during the write operation.
    """
    encodings = ['utf-8', 'latin-1', 'ascii']

    # Use 'utf-8' encoding as a default, with 'latin-1' and 'ascii' as fallbacks.
    for encoding in encodings:
        try:
            with file_path.open("w", encoding=encoding) as file:
                return file.write(content)

        except UnicodeEncodeError:
            continue
        except PermissionError as error:
            log.exception("Permission denied: %s", file_path, exc_info=error)
        except OSError as error:
            log.exception("I/O error occurred: %s", file_path, exc_info=error)
        except Exception as error:
            log.exception("An unexpected error occurred: %s", file_path, exc_info=error)

    # If all text encodings fail, try to write as binary
    try:
        with file_path.open("wb") as file:
            return file.write(content.encode('utf-8', errors='replace'))

    except Exception as error:
        log.exception("Failed to write file even in binary mode: %s", file_path, exc_info=error)


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
