import base64
import shutil

import structlog

log = structlog.stdlib.get_logger(__name__)


def read_file(file_path):
    """
    Reads the content of a file.

    Args:
    ----
    - file_path: The path to the file to read.

    Returns:
    -------
    - The content of the file as a string.

    """
    try:
        with file_path.open("r") as file:
            return file.read()

    except FileNotFoundError as error:
        log.error(f"File '{file_path}' not found: {error!s}")
    except PermissionError as error:
        log.error(f"Permission denied to access file '{file_path}': {error}")
    except UnicodeError as error:
        log.error(f"An error occurred while decoding file '{file_path}' content: {error!s}")
    except OSError as error:
        log.error(f"An operating system error occurred while reading file {file_path}: {error!s}")
    except Exception as error:
        log.error(f"An unexpected error occurred when handling '{file_path}': {error!s}")


def write_file(file_path, content):
    """
    Writes content to a file.

    Args:
    ----
    - file_path: The path to the file to write.
    - content: The content to write to the file.

    """
    try:
        with file_path.open("w") as file:
            file.write(content)

    except OSError as error:
        log.error(f"An I/O error occurred while writing to file '{file_path}': {error!s}")


def preprocess_text_formatting(prefix: str, file_path: str, suffix: str):
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


def create_directory(directory):
    """
    Checks if a directory exists; if not, creates it.

    Args:
    ----
    - directory: The path to the directory to check or create.

    Returns:
    -------
    - None.

    """
    log.debug(f"Checking if directory {directory} exists.")

    try:
        directory.mkdir(parents=True, exist_ok=True)
        log.debug(f"Directory {directory} exists or has been created.")

    except PermissionError as error:
        log.error(f"Permission denied to create directory {directory}: {error!s}")
    except OSError as error:
        log.error(f"An operating system error occurred while creating directory {directory}: {error!s}")
    except Exception as error:
        log.error(f"An unexpected error occurred while creating directory {directory}: {error!s}")


def delete_directory(directory):
    """
    Deletes the directory if it exists.

    Args:
    ----
    - directory: The directory to delete.

    Returns:
    -------
    - None
    """
    log.debug(f"Deleting {directory} directory.")

    try:
        if directory.exists():
            shutil.rmtree(directory)
            log.debug(f"Deleted the {directory} directory.")

    except PermissionError as error:
        log.error(f"Permission denied to delete directory {directory}: {error!s}")
    except OSError as error:
        log.error(f"An operating system error occurred while deleting directory {directory}: {error!s}")
    except Exception as error:
        log.error(f"An unexpected error occurred while deleting directory {directory}: {error!s}")
