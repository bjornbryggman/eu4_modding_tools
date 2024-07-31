# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
insert one-liner description here.

insert more descriptive explanation here, max 3 rows with max 100 words each row.
"""

import torch
from diffusers import FlowMatchEulerDiscreteScheduler, StableDiffusion3Pipeline, schedulers

torch.set_float32_matmul_precision("high")

torch._inductor.config.conv_1x1_as_mm = True
torch._inductor.config.coordinate_descent_tuning = True
torch._inductor.config.epilogue_fusion = False
torch._inductor.config.coordinate_descent_check_all_directions = True


FlowMatchScheduler = FlowMatchEulerDiscreteScheduler(shift=3.0).from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", subfolder="scheduler"
)

pipeline = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16
).to("cuda")
pipeline.set_progress_bar_config(disable=True)

pipeline.transformer.to(memory_format=torch.channels_last)
pipeline.vae.to(memory_format=torch.channels_last)
pipeline.transformer = torch.compile(pipeline.transformer, mode="max-autotune", fullgraph=True)
pipeline.vae.decode = torch.compile(pipeline.vae.decode, mode="max-autotune", fullgraph=True)

prompt = "a photo of a cat"
image = pipeline(
    prompt=prompt,
    num_inference_steps=28,
    height=640,
    width=1536,
    guidance_scale=3.5,
    generator=torch.manual_seed(1),
).images[0]
filename = "_".join(prompt.split(" "))
image.save(f"diffusers_{filename}.png")
