import asyncio
import os

import dotenv
import structlog

from backend.api import aasdasda

dotenv.load_dotenv()


async def request():
    role = "user"
    text_content = "Describe this image"
    url = "https://adamj.eu/tech/assets/2021-07-10-typing-trap.jpg"
    message = [
        {
            "role": role,
            "content": [{"type": "text", "text": text_content}, {"type": "image_url", "image_url": {"url": url}}],
        }
    ]
    model = "fireworks/firellava-13b"
    api_key = os.getenv("OPENAI_API_KEY")

    log = structlog.stdlib.get_logger(__name__)

    log.info("Initiating workflow...")

    await aasdasda.completion_request(message, model, api_key, False)


if __name__ == "__main__":
    asyncio.run(request())
