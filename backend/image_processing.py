import structlog
from wand.image import Image
from wand.exceptions import WandError, FileOpenError, CorruptImageError
from pathlib import Path

log = structlog.stdlib.get_logger(__name__)

#====================================================#
#          Functions for processing images           #
#====================================================#

def convert_images(input_directory: Path, output_directory: Path, input_format: str, output_format: str):
    """
    Converts images from one format to another.

    Args:
    - input_directory: The directory containing the input images to convert.
    - output_directory: The directory where the converted images will be stored.
    - input_format: The format of the input images (e.g., "dds", "png").
    - output_format: The format of the output images (e.g., "png", "dds").

    Returns:
    - Converted images in the specified output format.
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
            
            except FileOpenError as error:
                log.error(f"Failed to open file {input_file}: {str(error)}")
            except CorruptImageError as error:
                log.error(f"Corrupt image file: {input_file}: {str(error)}")
            except WandError as error:
                log.error(f"A Wand library error occurred when converting {input_file} to {output_format.upper()} format: {str(error)}")
            except PermissionError as error:
                log.error(f"Permission denied when converting {input_file} to {output_format.upper()} format: {str(error)}")
            except OSError as error:
                log.error(f"OS error occurred when converting {input_file} to {output_format.upper()} format: {str(error)}")
            except Exception as error:
                log.error(f"An unexpected error occurred when converting {input_file} to {output_format.upper()} format: {str(error)}")


    except FileNotFoundError as error:
        log.error(f"Failed to find any {input_format.upper()} files in {input_directory} directory: {str(error)}")
    except Exception as error:
        log.error(f"An unexpected error occurred: {str(error)}")

def resize_images(input_directory: Path, output_directory: Path, input_format: str, scaling_factor: float):
    """
    Resizes the upscaled images with a specified scaling factor.

    Args:
    - input_directory: Path to the directory containing the upscaled images.
    - output_directory: Path where the resized images will be saved.
    - scaling_factor: The factor by which images are resized (default is 0.6).

    Returns:
    - DDS files.
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

            except FileOpenError as error:
                log.error(f"Failed to open file {upscaled_file}: {str(error)}")
            except CorruptImageError as error:
                log.error(f"Corrupt image file: {upscaled_file}: {str(error)}")
            except WandError as error:
                log.error(f"A Wand library error occurred while resizing {upscaled_file}: {str(error)}")
            except PermissionError as error:
                log.error(f"Permission denied while resizing {upscaled_file}: {str(error)}")
            except ValueError as error:
                log.error(f"Invalid scaling factor value: {str(error)}")
            except OSError as error:
                log.error(f"OS error occurred while resizing {upscaled_file}: {str(error)}")
            except Exception as error:
                log.error(f"An unexpected error occurred while resizing {upscaled_file}: {str(error)}")

    
    except FileNotFoundError as error:
        log.error(f"Failed to find any upscaled images in {input_directory} directory: {str(error)}")
    except Exception as error:
        log.error(f"An unexpected error occurred: {str(error)}")

