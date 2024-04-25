"""
This script provides a complete workflow for converting image files from DDS to PNG format,
upscaling them using AI (Real-ESRGAN, to be specific), resizing the upscaled images, and then converting them back to DDS format.

It uses Wand for image manipulation and the Replicate API for upscale transformations.

"""

import os
import sys
import logging
import shutil
from wand.image import Image
import replicate
from urllib.request import urlretrieve

# Setup stage where the logging is configured.
def ensure_logging_is_setup(base_path):
    """
    Ensures that logging is setup. This function is idempotent.
    
    Adds both a file handler and a stream handler to the root logger.

    """
    if not logging.getLogger().hasHandlers():
        log_file_path = os.path.join(base_path, "error_log.txt")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.ERROR)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)

        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.ERROR)
        stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                             datefmt='%Y-%m-%d %H:%M:%S')
        stream_handler.setFormatter(stream_formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)



# Pre-processing stage where files and folders are prepared and double-checked before initiating the workflow.
def ensure_dir_exists(directory):
    """
    Ensures that a directory exists, and if not, this function will create it.
    
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def check_original_folder(input_dir):
    """Checks if the original directory exists and ensures that it is not empty."""
    if not os.path.exists(input_dir) or not os.listdir(input_dir):
        print(f"Error: The {input_dir} directory either does not exist or is empty.")
        sys.exit(1)

def clean_and_prepare_directory(directory):
    """
    If the directory exists, deletes it and recreates it to ensure it is empty.
    
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


# Main workflow.
def convert_dds_to_png (input_dir, png_dir, base_path):
    """
    Converts DDS formatted files within a directory to PNG format using the Wand library.

    Parameters:
    - input_dir: A string path to the directory containing the original DDS files.
    - png_dir: A string path to the directory where converted PNG files will be stored.
    - base_path: The base directory path, used for any potential error logging.

    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".dds"):
                input_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(png_dir, rel_dir)
                os.makedirs(output_subdir, exist_ok=True)
                output_path = os.path.join(output_subdir, os.path.splitext(file)[0] + ".png")

                try:
                    with Image(filename=input_path) as img:
                        img.format = 'png'
                        img.save(filename=output_path)
                    print(f"Converted {file} to PNG using Wand.")

                except Exception as e:
                    ensure_logging_is_setup(base_path)
                    logging.error(f"Failed to convert {file} to PNG. Error: {e}")

def upscale_images(png_dir, upscaled_dir, base_path):
    """
    Upscales PNG images using the Replicate API.

    Parameters:
    - png_dir: A string path to the directory containing the PNG files to be upscaled.
    - upscaled_dir: A string path to the directory where upscaled images will be stored.
    - base_path: The base directory path, used for any potential error logging.

    """
    for root, _, files in os.walk(png_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, png_dir)
                output_subdir = os.path.join(upscaled_dir, rel_dir)
                os.makedirs(output_subdir, exist_ok=True)
                output_path = os.path.join(output_subdir, file)
                
                try:
                    with open(input_path, 'rb') as image_file:
                        output = replicate.predict(
                            "nightmareai/real-esrgan",
                            version="350d32041630ffbe63c8352783a26d94126809164e54085352f8326e53999085",
                            input={
                                "image": image_file,
                                "scale": 2,
                                "face_enhance": False,
                            }
                        )
                    urlretrieve(output[0]["url"], output_path)
                    print(f"Upscaled {file} using Real-ESRGAN via the Replicate API.")
                
                except replicate.exceptions.ReplicateError as e:
                    ensure_logging_is_setup(base_path)
                    logging.error(f"Failed to upscale {file} due to a Replicate API error: {e}")

                except Exception as e:
                    ensure_logging_is_setup(base_path)
                    logging.error(f"An unexpected error occurred while upscaling {file}: {e}")
                
def resize_images(upscaled_dir, resized_dir, base_path, scaling_factor=0.6):
    """
    Resizes images using Wand, with the new size being a specified fraction
    of the original size, determined by the scaling_factor parameter.

    Parameters:
    - upscaled_dir: The directory containing images to be resized.
    - resized_dir: The target directory for resized images.
    - base_path: The base directory path, used for any potential error logging.
    - scaling_factor: The factor by which to scale images, relative to their original size.

    """
    for root, _, files in os.walk(upscaled_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, upscaled_dir)
                output_subdir = os.path.join(resized_dir, rel_dir)
                os.makedirs(output_subdir, exist_ok=True)
                output_path = os.path.join(output_subdir, file)

                try:
                    with Image(filename=input_path) as img:
                        # Calculate new dimensions based on the scaling factor
                        new_width = int(img.width * scaling_factor)
                        new_height = int(img.height * scaling_factor)
                        img.resize(new_width, new_height)
                        img.save(filename=output_path)
                    print(f"Resized {file} to {scaling_factor*100}% of its original dimensions using Wand.")

                except Exception as e:
                    ensure_logging_is_setup(base_path)
                    logging.error(f"Failed to resize {file}. Error: {e}")

def convert_png_to_dds (resized_dir, final_output_dir, base_path):
    """
    Converts PNG formatted files back to DDS format using Wand.

    Parameters:
    - resized_dir: A string path to the directory containing the resized PNG files.
    - final_output_dir: A string path to the directory where the final DDS files will be stored.
    - base_path: The base directory path, used for any potential error logging.

    """
    for root, _, files in os.walk(resized_dir):
        for file in files:
            if file.lower().endswith(".png"):
                input_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, resized_dir)
                output_subdir = os.path.join(final_output_dir, rel_dir)
                os.makedirs(output_subdir, exist_ok=True)
                output_path = os.path.join(output_subdir, os.path.splitext(file)[0] + ".dds")

                try:
                    with Image(filename=input_path) as img:
                        img.format = 'dds'
                        img.save(filename=output_path)
                    print(f"Converted {file} to DDS using Wand.")

                except Exception as e:
                    ensure_logging_is_setup(base_path)
                    logging.error(f"Failed to convert {file} back to DDS. Error: {e}")


# Clean-up stage where unnecessary files and folders are deleted.
def clean_up_directory(base_path, dir_to_clean):
    """
    Deletes all files within a specified directory relative to the base path, 
    including files in its subdirectories.

    Parameters:
    - base_path: The base directory path related to which the dir_to_clean is specified.
    - dir_to_clean: The relative path from the base directory to the directory from which files will be deleted.

    """
    dir_path = os.path.join(base_path, dir_to_clean)

    try:
        shutil.rmtree(dir_path)
        print(f"Completely removed the directory {dir_path}")

    except OSError as e:
        ensure_logging_is_setup(base_path)
        logging.error(f"Failed to remove the directory {dir_path}. Error: {e}")


# Main function.
def main():
    """
    Orchestrates the workflow of converting DDS to PNG, upscaling, resizing, and
    converting back to DDS, storing the results using their original file names and folder structure,
    then finishing up by deleting everything except the original input and the final output.

    """
    base_path = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(base_path, "input_files_to_be_converted")
    png_dir = os.path.join(base_path, "converted_files_in_png_format")
    upscaled_dir = os.path.join(base_path, "upscaled_files")
    resized_dir = os.path.join(base_path, "resized_files")
    final_output_dir = os.path.join(base_path, "final_output")
    print("Preparing files and folders for processing...")
    

    check_original_folder(input_dir)
    for dir_path in [png_dir, upscaled_dir, resized_dir, final_output_dir]:
        clean_and_prepare_directory(dir_path)
    print("Prepration complete, workflow initiated. Proceeding with converting the DDS files into PNG format...")


    convert_dds_to_png(input_dir, png_dir, base_path)
    print("Conversion complete. Proceeding with upscaling...")
    

    upscale_images(png_dir, upscaled_dir, base_path)
    print("Upscaling complete. Proceeding with resizing the files according to the specified scaling factor...")

    
    resize_images(upscaled_dir, resized_dir, base_path)
    print("Resizing complete. Proceeding with converting the files back to their original .dds format...")


    convert_png_to_dds(resized_dir, final_output_dir, base_path)
    print("Workflow complete. Proceeding with cleanup...")
    

    directories_to_clean = ["converted_files_in_png_format", "upscaled_files", "resized_files"]
    for dir_name in directories_to_clean:
        clean_up_directory(base_path, dir_name)
    print("Cleanup complete. You can now close this window.")


if __name__ == "__main__":
    main()