#!/bin/bash

# Initiate a basic Accelerate config.
accelerate config default

# Distribute workload across 5 GPUs.
accelerate launch --num_processes 5 distributed_inference.py

    # 21:9 dimensions:
    # height: 640
    # width: 1536
    # guidance_scale: 4
    # num_inference_steps: 28