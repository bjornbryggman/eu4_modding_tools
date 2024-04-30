import shutil
import structlog

log = structlog.stdlib.get_logger("./utils/file_utils.py")

def read_file(file_path):
    """
    Reads the content of a file.

    Parameters:
    - file_path: The path to the file to read.

    Returns:
    - The content of the file as a string.

    Raises:
    - FileNotFoundError: If the file does not exist.
    - PermissionError: If permission is denied to read the file.
    - UnicodeError: If a Unicode error occurs during file reading.
    - OSError: If an operating system error occurs during file reading.
    - Exception: If an unexpected error occurs.
    """

    try:
        with file_path.open('r') as file:
            return file.read()
        
    except FileNotFoundError as e:
        log.error(f"File '{file_path}' not found: {str(e)}")
    except PermissionError as e:
        log.error(f"Permission denied to access file '{file_path}': {e}")
    except UnicodeError as e:
        log.error(f"An error occurred while decoding file '{file_path}' content: {str(e)}")
    except OSError as e:
        log.error(f"An operating system error occurred while reading file {file_path}: {str(e)}")
    except Exception as e:
        log.error(f"An unexpected error occurred when handling '{file_path}': {str(e)}")



def write_file(file_path, content):
    """
    Writes content to a file.

    Parameters:
    - file_path: The path to the file to write.
    - content: The content to write to the file.

    Returns:
    - None.

    Raises:
    - OSError: If an I/O error occurs while writing to the file.
    """
    try:
        with file_path.open('w') as file:
            file.write(content)
    except OSError as e:
        log.error(f"An I/O error occurred while writing to file '{file_path}': {str(e)}")


def create_directory(directory):
    """
    Checks if a directory exists; if not, creates it.

    Parameters:
    - directory: The path to the directory to check or create.

    Returns:
    - None.

    Raises:
    - PermissionError: If permission is denied to create the directory.
    - OSError: If an operating system error occurs during directory creation.
    - Exception: If an unexpected error occurs.
    """
    
    log.debug(f"Checking if directory {directory} exists.")
    
    try:
        directory.mkdir(parents=True, exist_ok=True)
        log.debug(f"Directory {directory} exists or has been created.")

    except PermissionError as e:
        log.error(f"Permission denied to create directory {directory}: {str(e)}")
    except OSError as e:
        log.error(f"An operating system error occurred while creating directory {directory}: {str(e)}")
    except Exception as e:
        log.error(f"An unexpected error occurred while creating directory {directory}: {str(e)}")


def delete_directory(directory):
    """
    Deletes the directory if it exists.

    Parameters:
    - directory: The directory to delete.

    Returns:
    - None

    Raises:
    - PermissionError: If permission is denied to delete the directory.
    - OSError: If an operating system error occurs during directory deletion.
    - Exception: If an unexpected error occurs.
    """
    
    log.debug(f"Deleting {directory} directory.")

    try:    
        if directory.exists():
                shutil.rmtree(directory)
                log.debug(f"Deleted the {directory} directory.")

    except PermissionError as e:
        log.error(f"Permission denied to delete directory {directory}: {str(e)}")

    except OSError as e:
        log.error(f"An operating system error occurred while deleting directory {directory}: {str(e)}")

    except Exception as e:
        log.error(f"An unexpected error occurred while deleting directory {directory}: {str(e)}")


