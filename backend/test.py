import os
import structlog
import dotenv
import asyncio
from backend.api import openrouter

dotenv.load_dotenv()

async def test():
    role = "user"
    text_content = "Write me a haiku about the spring breeze."
    model = "gpt-3.5-turbo"
    api_key = os.getenv("OPENAI_API_KEY")

    log = structlog.stdlib.get_logger(__name__)

    log.info("Initiating workflow...")

    await openrouter.streaming_text_completion(role, text_content, model, api_key)

if __name__ == "__main__":
    asyncio.run(test())