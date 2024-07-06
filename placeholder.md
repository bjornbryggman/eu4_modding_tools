    replicate_image_generation.upscale_images(
        config.PNG_DIRECTORY, config.UPSCALING_DIRECTORY, "PNG", os.getenv("REPLICATE_IMAGE_UPSCALING_MODEL")
    )

    gui_file_scaler.process_GUI_files(config.INPUT_DIRECTORY, "GUI", 1.2)