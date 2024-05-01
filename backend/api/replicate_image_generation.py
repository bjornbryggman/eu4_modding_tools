import asyncio
import replicate
import structlog
from pathlib import Path
from replicate.exceptions import ReplicateError
from requests import RequestException
from urllib.request import urlretrieve

log = structlog.stdlib.get_logger(__name__)

def upscale_images(
    input_directory: Path,
    output_directory: Path,
    input_format: str,
    replicate_upscaling_model: str,
):
    """
    Upscales images using the Replicate API.

    Args:
    - input_directory: Path to the directory containing the images to be upscaled.
    - output_directory: Path where the upscaled images will be stored.
    - api_key: API key for the Replicate API.

    Returns:
    - Upscaled PNG images.
    """
    try:

        for png_file in (input_directory.glob(f"*.{input_format}")):
            output_path = output_directory / png_file.name

            try:
                with open(png_file, "rb") as image_file:
                    output = replicate.run(
                        replicate_upscaling_model,
                        input={
                            "image": image_file,
                            "scale": 2,
                            "face_enhance": False,
                        },
                    )

                    output_url = output if isinstance(output, str) else output["url"]
                    urlretrieve(output_url, output_path)
                log.info(f"Upscaled {png_file} via the Replicate API.")

            except RequestException as error:
                log.error(f"Error: {error}. Request to the Replicate API failed.")
            except ReplicateError as error:
                log.error(f"Failed to upscale {png_file} due to an error with the Replicate API: {error}")
            except ValueError as error:
                log.error(f"Invalid input when upscaling {png_file}: {str(error)}")
            except TypeError as error:
                log.error(f"Invalid data type when upscaling {png_file}: {str(error)}")
            except OSError as error:
                log.error(f"An I/O error occurred while upscaling {png_file}: {str(error)}")

    except Exception as error:
        log.error(f"An unexpected error occurred while upscaling {png_file}: {str(error)}")

async def batching():
    # https://github.com/replicate/replicate-python
    model_version = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
    prompts = [
        f"A chariot pulled by a team of {count} rainbow unicorns"
        for count in ["two", "four", "six", "eight"]
    ]

    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(replicate.async_run(model_version, input={"prompt": prompt}))
            for prompt in prompts
        ]

    results = await asyncio.gather(*tasks)
    print(results)

def pipelines():
    laionide = replicate.models.get("afiaka87/laionide-v4").versions.get("b21cbe271e65c1718f2999b038c18b45e21e4fba961181fbfae9342fc53b9e05")
    swinir = replicate.models.get("jingyunliang/swinir").versions.get("660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a")
    image = laionide.predict(prompt="avocado armchair")
    upscaled_image = swinir.predict(image=image)
    return upscaled_image