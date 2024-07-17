https://github.com/Microsoft/DirectXTex/wiki/Texconv 



```
project_root/
│
├── src/                      # All source code will be contained in this directory
│   ├── __init__.py           # Makes src a Python package
│   ├── main.py               # Entry point of the script which calls other modules
│   ├── file_utils.py         # Module for filesystem operations
│   ├── image_processing.py   # Module for image convert, upscale, and resize
│   ├── api_utils.py          # Module for interacting with external APIs
│   ├── logging_utils.py      # Module for setting up logging
│   └── config.py             # Module for loading configuration
│
├── tests/                    # Directory for test files
│   ├── __init__.py           # Makes tests a Python package
│   ├── test_file_utils.py
│   ├── test_image_processing.py
│   ├── test_api_utils.py
│   └── test_logging_utils.py
│
├── config/                   # Configurations directory
│   ├── settings.ini          # Configuration file for the script
│   └── logging_config.ini    # Separate config for logging if needed
│
├── input_dds_files/          # Directory for input .dds files
├── output_dds_files/         # Final directory for output .dds files
├── requirements.txt          # Required Python packages
├── .gitignore                # List of files and paths to ignore in version control
├── .env                      # Contains the relevant environment variables.
├── README.md                 # Documentation for using and contributing to the script
└── LICENSE                   # The license for the script
```

- `src/` is the directory where all the Python source code lives. Each Python file like `file_utils.py`, `image_processing.py`, etc., represents a module dedicated to a specific aspect of the workflow.
- `tests/` contains the test suite for your application. It's good practice to write tests for your functions to ensure they're working as expected.
- `config/` holds configuration files, which can be in whichever format you prefer (INI, JSON, YAML, etc.).
- `input_dds_files/` and `output_dds_files/` are directories that the script will interact with for processing the images. These are separated out to keep the root directory clean.
- `requirements.txt` is where you list all external dependencies needed to run the script, making it easier for other developers to install the necessary packages.
- `.gitignore` is a Git file where you specify all files and directories that should not be checked into version control (e.g., `__pycache__/`, virtual environment directories).
- `README.md` provides a description of the project, installation instructions, usage examples, and any other important information a user or contributor might need.
- `LICENSE` contains the licensing information for your project, making it clear under what terms others can use or contribute to your code.

Each file and directory has a clear purpose, making the project both easier to navigate and understand. This structure will also make it easier to package your script using tools like setuptools, creating an installable Python package.

Excellent. Now that we know what we need to do and how to do it, lets take a moment to plan out step-by-step the most reasonable order in which to write these new modules. To reiterate - it's important that we don't simply copy the original code. This won't work well since these new modules are isolated and, as such, can't easily reference each others variables. As such, the new code needs to be written in such an order that the relevant modules can be imported in any subsequent modules that might need to reference it. The code can be adapted as you see fit as long as it still retains its' original function, so take any liberties you deem fit in order to accomplish the objective.

Proceed step-by-step and do not shorten for brevity, you can always continue in another response if necessary.

Nice work! Keep it steady and continue writing out the code step-by-step for the specified modules strictly as per the previously outlined plan, while also ensuring that the new code adheres to the code written in the previous steps, as well as overall good practices for proper coding.

Remember, do not shorten for brevity as you can always continue in another response if necessary.

Let us take a moment to look back and reflect on the code we've written so far step-by-step. 

Does it adhere to our previously outlined plan? Does it contain any errors? Does it adhere to proper coding practices?

Your reflection is logical and reasonable. As such, go ahead and directly modify the previously written code as you see fit, as per your critique.

Take it slow and think before you act. There is no need to be overly verbose either - simply modifying the relevant code is enough.