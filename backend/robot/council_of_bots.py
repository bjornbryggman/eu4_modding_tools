import os
import structlog
from dotenv import load_dotenv
from backend.core.config import DirectoryConfig
from backend.utils import file_utils
from backend.api import litellm_text_generation

load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")

log = structlog.stdlib.get_logger(__name__)

def AI_preprocessing(file_name: str = None):
    """
    The main entry point of the script.

    This function handles the overall workflow of the image processing pipeline.
    """

    config = DirectoryConfig()

    log.info("Initiating workflow...")
    
    litellm_text_generation.validate_environment
    
    try:
        
        for directory_path in [config.PNG_DIRECTORY, config.UPSCALED_DIRECTORY, config.RESIZED_DIRECTORY, config.OUTPUT_DIRECTORY]:
            file_utils.delete_directory(directory_path)
            file_utils.create_directory(directory_path)

        prefix = str
        target_file = config.BASE_PATH / file_name
        suffix = str
        file_utils.preprocess_text_formatting(prefix, target_file, suffix)

        for directory_path in [config.PNG_DIRECTORY, config.RESIZED_DIRECTORY, config.UPSCALED_DIRECTORY]:
            file_utils.delete_directory(directory_path)

        log.info("Image processing pipeline completed successfully.")

    except Exception as e:
        log.error("An unexpected error occurred during the image processing pipeline:\n%s", str(e))


if __name__ == "__main__":
    AI_preprocessing()