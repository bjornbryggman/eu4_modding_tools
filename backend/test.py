import asyncio
import os
from pathlib import Path

import dotenv
import structlog

from backend.api import openrouter_text_generation
from backend.robot import documenter

dotenv.load_dotenv()


async def request():
    contents = Path("C:\\Side Projects\\EU4 Modding Tools\\backend\\utils\\input.py").read_text()
    message = documenter.code_agent(contents)
    model = "meta-llama/llama-3-70b-instruct:nitro"
    api_key = os.getenv("OPENAI_API_KEY")

    log = structlog.stdlib.get_logger(__name__)

    log.info("Initiating workflow...")

    superss, cost = await openrouter_text_generation.completion_request(message, model, api_key, False)
    log.info(f"Workflow result: superss={superss}, cost={cost}")


if __name__ == "__main__":
    asyncio.run(request())
