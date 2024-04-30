import structlog
import re
from pathlib import Path
from backend.utils.file_utils import read_file, write_file

log = structlog.stdlib.get_logger(__name__)

class GUI_UI_Scaler:
    """
    A class to scale the relevant positional information of GUI files according to a specific scaling factor.
    """

    def __init__(self, scale_factor):
        """
        Initializes the GUIFileScaler with the appropriate scaling factor.

        Args:
        - scale_factor: The scaling factor to apply.

        Returns:
        - None.
        """
        self.scale_factor = scale_factor

    def scale_value(self, match):
        """
        Scales a matched value according to the scaling factor.

        Args:
        - match: The regex match object containing the property name and value.

        Returns:
        - The scaled value as a string.
        """
        prop, value = match.group(1), float(match.group(2))
        scaled_value = round(value * self.scale_factor)
        return f'{prop} = {scaled_value}'

    def process_content(self, content):
        """
        Scales values in the content according to the scaling factor.

        Args:
        - content: The content of the GUI file to process.

        Returns:
        - The processed content with scaled values.
        """
        pattern = r'(\bx\b|\by\b|maxWidth|maxHeight) *= *(-?\d+(?:\.\d+)?)'
        return re.sub(pattern, self.scale_value, content)


def process_GUI_files(input_directory: Path, input_format: str, scale_factor: float):
    """
    Processes GUI files in a input_directory and scales their relevant positional values according to the scaling factor.

    Args:
    - input_directory: The input_directory containing the GUI files to process.
    - scale_factor: The scaling factor to apply.

    Returns:
    - None.
    """
    log.debug(f"Processing GUI files in {input_directory} with scale factor {scale_factor}...")

    scaler = GUI_UI_Scaler(scale_factor)
    
    try:

        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError

        for file_path in input_directory.glob(f"*.{input_format}"):
            try:
                content = read_file(file_path)
                updated_content = scaler.process_content(content)
                
                if content != updated_content:
                    write_file(file_path, updated_content)
                    log.debug(f"Updated {file_path.name} with scaled values.")
                else:
                    log.debug(f"No changes have been made to {file_path.name}.")

            except PermissionError as error:
                log.error(f"Permission denied when accessing {file_path}: {str(error)}")
            except re.error as error:
                log.error(f"Regex error while processing {file_path.name}: {str(error)}")
            except OSError as error:
                log.error(f"OS error encountered with {file_path.name}: {str(error)}")
            except Exception as error:
                log.error(f"Unexpected error while processing {file_path}: {str(error)}")

    except FileNotFoundError as error:
        log.warning(f"Failed to find any {input_format.upper()} files in {input_directory} directory: {str(error)}")
    
