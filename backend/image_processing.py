import structlog
from wand.image import Image
from wand.exceptions import WandError, FileOpenError, CorruptImageError
from pathlib import Path

log = structlog.stdlib.get_logger("./src/image_processing.py")

def convert_images(input_directory: Path, output_directory: Path, input_format: str, output_format: str):
    """
    Converts images from one format to another.

    Parameters:
    - input_directory: The directory containing the input images to convert.
    - output_directory: The directory where the converted images will be stored.
    - input_format: The format of the input images (e.g., "dds", "png").
    - output_format: The format of the output images (e.g., "png", "dds").

    Returns:
    - Converted images in the specified output format.

    Raises:
    - FileNotFoundError: If the input directory is empty.
    - FileOpenError: If an error occurs when opening a file.
    - CorruptImageError: If an image file is corrupted.
    - WandError: If an error occurs when using the Wand library.
    - PermissionError: If permission is denied when accessing files.
    - OSError: If an OS error occurs when accessing files.
    - Exception: If an unexpected error occurs.
    """
    try:
        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError

        for input_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / (input_file.stem + f".{output_format}")
            
            try:
            
                with Image(filename=str(input_file)) as img:
                    img.format = output_format
                    img.save(filename=str(output_path))
                log.info(f"Converted {input_file.name} to {output_format.upper()}.")
            
            except FileOpenError as e:
                log.error(f"Failed to open file {input_file}: {str(e)}")
            except CorruptImageError as e:
                log.error(f"Corrupt image file: {input_file}: {str(e)}")
            except WandError as e:
                log.error(f"A Wand library error occurred when converting {input_file} to {output_format.upper()} format: {str(e)}")
            except PermissionError as e:
                log.error(f"Permission denied when converting {input_file} to {output_format.upper()} format: {str(e)}")
            except OSError as e:
                log.error(f"OS error occurred when converting {input_file} to {output_format.upper()} format: {str(e)}")
            except Exception as e:
                log.error(f"An unexpected error occurred when converting {input_file} to {output_format.upper()} format: {str(e)}")


    except FileNotFoundError as e:
        log.error(f"Failed to find any {input_format.upper()} files in {input_directory} directory: {str(e)}")
    except Exception as e:
        log.error(f"An unexpected error occurred: {str(e)}")

def resize_images(input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float):
    """
    Resizes the upscaled images with a specified scaling factor.

    Parameters:
    - input_directory: Path to the directory containing the upscaled images.
    - output_directory: Path where the resized images will be saved.
    - scaling_factor: The factor by which images are resized (default is 0.6).

    Returns:
    - DDS files.

    Raises:
    - FileNotFoundError: If the upscaled directory is empty.
    - FileOpenError: If an error occurs when opening a file.
    - CorruptImageError: If an image file is corrupted.
    - WandError: If an error occurs when using the Wand library.
    - PermissionError: If permission is denied when accessing files.
    - ValueError: If the scaling factor is invalid.
    - OSError: If an OS error occurs when accessing files.
    - Exception: If an unexpected error occurs.
    """
    try:
        if not any(input_directory.glob(f"*.{input_format}")):
            raise FileNotFoundError

        for upscaled_file in input_directory.glob(f"*.{input_format}"):
            output_path = output_directory / upscaled_file.name
            
            try:
                with Image(filename=str(upscaled_file)) as img:
                    img.resize(int(img.width * scaling_factor), int(img.height * scaling_factor))
                    img.save(filename=str(output_path))
                log.info(f"Resized {upscaled_file.name} with a factor of {scaling_factor}")

            except FileOpenError as e:
                log.error(f"Failed to open file {upscaled_file}: {str(e)}")
            except CorruptImageError as e:
                log.error(f"Corrupt image file: {upscaled_file}: {str(e)}")
            except WandError as e:
                log.error(f"A Wand library error occurred while resizing {upscaled_file}: {str(e)}")
            except PermissionError as e:
                log.error(f"Permission denied while resizing {upscaled_file}: {str(e)}")
            except ValueError as e:
                log.error(f"Invalid scaling factor value: {str(e)}")
            except OSError as e:
                log.error(f"OS error occurred while resizing {upscaled_file}: {str(e)}")
            except Exception as e:
                log.error(f"An unexpected error occurred while resizing {upscaled_file}: {str(e)}")

    
    except FileNotFoundError as e:
        log.error(f"Failed to find any upscaled images in {input_directory} directory: {str(e)}")
    except Exception as e:
        log.error(f"An unexpected error occurred: {str(e)}")

