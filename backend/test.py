import os
import structlog
from dotenv import load_dotenv

from backend.api import litellm_text_generation

load_dotenv()


def test():
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    specific_model = os.getenv("OPENROUTER_TEXT_META_LLAMA-3_70B_NITRO")
    log = structlog.stdlib.get_logger(__name__)

    log.info("Initiating workflow...")

    litellm_text_generation.text_completion_call("user", "this is a text. write me a haiku about a famous historical figure", specific_model, os.getenv("OPENROUTER_API_KEY"), False)

if __name__ == "__main__":
    test()