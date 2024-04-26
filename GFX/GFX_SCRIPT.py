"""
This script provides a complete workflow for converting image files from DDS to PNG format,
upscaling them using AI (Real-ESRGAN, to be specific), resizing the upscaled images, and then converting them back to DDS format.

It uses Wand for image manipulation and the Replicate API for upscale transformations.
"""
import os
import sys
import logging
import shutil
import pathlib
import traceback
from urllib.request import urlretrieve

from wand.image import Image
import replicate

# Setup stage where the logging is configured.
def logging_setup(base_path):
    """
    Configures logging for the script.

    This function sets up both file and console logging. The log file is reset
    at the start of each run.

    Parameters:
    - base_path: The base path where the log file is created.

    Returns:
    - None
    """
    log_file_path = base_path / "logging.txt"
    log_file_path.write_text('')
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler.setFormatter(stream_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)



# Pre-processing stage where files and folders are prepared and double-checked before initiating the workflow.
def ensure_dir_exists(directory):
    """
    Ensures that a directory exists; if not, creates it.

    Parameters:
    - directory: The path to the directory to check or create.

    Returns:
    - None
    """
    directory.mkdir(parents=True, exist_ok=True)

def check_input_folder(input_dir):
    """
    Checks if the input directory exists.
    
    If not, creates the directory. Otherwise, checks if it's empty.

    Parameters:
    - input_dir: The path to the input directory.

    Returns:
    - None
    """
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        logging.error(f"\nThe {input_dir} directory does not exist.\n\nIt has now been created for you; make sure to place the DDS files that you want to process into the directory before proceeding.")
        sys.exit(1)
    
    if not any(input_dir.iterdir()):
        logging.error(f"\nThe {input_dir} directory is empty.\n\nPlace the DDS files that you want to process into the directory before proceeding.")
        sys.exit(1)
    
def clean_and_prepare_directory(directory):
    """
    Deletes the directory if it exists, then recreates it to ensure it's empty.

    Parameters:
    - directory: The directory to clean and prepare.

    Returns:
    - None
    """
    if directory.exists():
        shutil.rmtree(str(directory))
    directory.mkdir(parents=True, exist_ok=True)


# Main workflow.
def convert_dds_to_png (input_dir, png_dir):
    """
    Converts DDS files in the input directory to PNG format.

    Parameters:
    - input_dir: The directory containing the DDS files to convert.
    - png_dir: The directory where the converted PNG files will be stored.

    Returns:
    - None
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".dds"):
                input_path = pathlib.Path(root) / file
                rel_dir = pathlib.Path(root).relative_to(input_dir)
                output_subdir = png_dir / rel_dir
                output_subdir.mkdir(parents=True, exist_ok=True)
                output_path = output_subdir / (pathlib.Path(input_path).stem + ".png")

                try:
                    with Image(filename=str(input_path)) as img:
                        img.format = 'png'
                        img.save(filename=str(output_path))
                    logging.info(f"Converted {file} to PNG using Wand.")

                except Exception as e:
                    logging.error(f"\nFailed to convert {file} to PNG format. {e}\n\nTraceback: {traceback.format_exc()}")


def upscale_images(png_dir, upscaled_dir):
    """
    Upscales PNG images using the Replicate API.

    Parameters:

    Parameters:
    - png_dir: The directory containing the PNG files to upscale.
    - upscaled_dir: The directory where the upscaled images will be stored.

    Returns:
    - None
    """
    for root, _, files in os.walk(png_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = pathlib.Path(root) / file
                rel_dir = pathlib.Path(root).relative_to(png_dir)
                output_subdir = upscaled_dir / rel_dir
                output_subdir.mkdir(parents=True, exist_ok=True)
                output_path = output_subdir / file

                try:
                    with open(input_path, 'rb') as image_file:
                        output = replicate.run(
                            "nightmareai/real-esrgan:350d32041630ffbe63c8352783a26d94126809164e54085352f8326e53999085",
                            input={
                                "image": image_file,
                                "scale": 2,
                                "face_enhance": False,
                            }
                        )

                        if isinstance(output, str):
                            urlretrieve(output, output_path)
                        else:
                            urlretrieve(output["url"], output_path)
                    logging.info(f"Upscaled {file} using Real-ESRGAN via the Replicate API.")

                except replicate.exceptions.ReplicateError as e:
                    logging.error(f"\nFailed to upscale {file} due to Replicate API {e}\n\nTraceback: {traceback.format_exc()}")

                except Exception as e:
                    logging.error(f"\nAn unexpected error occurred while upscaling {file}: {e}\n\nTraceback: {traceback.format_exc()}")

                
def resize_images(upscaled_dir, resized_dir, scaling_factor=0.6):
    """
    Resizes upscaled images according to a specified scaling factor.

    Parameters:
    - upscaled_dir: The directory containing the upscaled images to resize.
    - resized_dir: The directory where the resized images will be stored.
    - scaling_factor (float): The factor by which to scale the images (default: 0.6).

    Returns:
    - None
    """
    for root, _, files in os.walk(upscaled_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = pathlib.Path(root) / file
                rel_dir = pathlib.Path(root).relative_to(upscaled_dir)
                output_subdir = resized_dir / rel_dir
                output_subdir.mkdir(parents=True, exist_ok=True)
                output_path = output_subdir / file

                try:
                    with Image(filename=str(input_path)) as img:
                        new_width = int(img.width * scaling_factor)
                        new_height = int(img.height * scaling_factor)
                        img.resize(new_width, new_height)
                        img.save(filename=str(output_path))
                    logging.info(f"Resized {file} to {scaling_factor*100}% of its original dimensions using Wand.")

                except Exception as e:
                    logging.error(f"\nFailed to resize {file}. {e}\n\nTraceback: {traceback.format_exc()}")



def convert_png_to_dds (resized_dir, final_output_dir):
    """
    Converts resized PNG images back to DDS format.

    Parameters:
    - resized_dir: The directory containing the resized PNG files to convert.
    - final_output_dir: The directory where the converted DDS files will be stored.

    Returns:
    - None
    """
    for root, _, files in os.walk(resized_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = pathlib.Path(root) / file
                rel_dir = pathlib.Path(root).relative_to(resized_dir)
                output_subdir = final_output_dir / rel_dir
                output_subdir.mkdir(parents=True, exist_ok=True)
                output_path = output_subdir / (pathlib.Path(input_path).stem + ".dds")

                try:
                    with Image(filename=str(input_path)) as img:
                        img.format = 'dds'
                        img.save(filename=str(output_path))
                    logging.info(f"Converted {file} to DDS using Wand.")

                except Exception as e:
                    logging.error(f"\nFailed to convert {file} back to DDS. {e}\n\nTraceback: {traceback.format_exc()}")



# Clean-up stage where unnecessary files and folders are deleted.
def clean_up_directory(base_path, dir_to_clean):
    """
    Deletes a specified directory relative to the base path.

    Parameters:
    - base_path: The base directory path related to which the dir_to_clean is specified.
    - dir_to_clean: The relative path from the base directory to the directory to clean.

    Returns:
    - None
    """
    dir_path = base_path / dir_to_clean

    try:
        shutil.rmtree(dir_path)
        logging.info(f"Completely removed the following directory: {dir_path}")

    except OSError as e:
        logging.error(f"\nFailed to remove the following directory: {dir_path}. {e}\n\nTraceback: {traceback.format_exc()}")


# Main function.
def main():
    """
    Orchestrates the entire workflow of converting DDS to PNG, upscaling, resizing, and converting back to DDS.

    Returns:
    - None
    """
    base_path = pathlib.Path(__file__).resolve().parent
    input_dir = base_path / "input_dds_files"
    png_dir = base_path / "converted_files_in_png_format"
    upscaled_dir = base_path / "upscaled_files"
    resized_dir = base_path / "resized_files"
    final_output_dir = base_path / "output_dds_files"
    logging_setup(base_path)

    logging.info("Preparing files and folders for processing...")
    check_input_folder(input_dir)
    for dir_path in [png_dir, upscaled_dir, resized_dir, final_output_dir]:
        clean_and_prepare_directory(dir_path)
    logging.info("Prepration completed.")

    logging.info("Beginning DDS to PNG conversion...")
    convert_dds_to_png(input_dir, png_dir)
    logging.info("DDS to PNG conversion completed.")
    
    logging.info("Beginning image upscaling...")
    upscale_images(png_dir, upscaled_dir)
    logging.info("Image upscaling completed.")
    
    logging.info("Beginning image resizing...")
    resize_images(upscaled_dir, resized_dir)
    logging.info("Resizing completed.")

    logging.info("Beginning PNG to DDS conversion...")
    convert_png_to_dds(resized_dir, final_output_dir)
    logging.info("PNG to DDS conversion completed.")
    
    logging.info("Proceeding with cleanup...")
    directories_to_clean = ["converted_files_in_png_format", "upscaled_files", "resized_files"]
    for dir_name in directories_to_clean:
        clean_up_directory(base_path, dir_name)
    logging.info("Cleanup completed.")

    logging.info("The workflow is now fully completed. You can now close this window.")


if __name__ == "__main__":
    main()