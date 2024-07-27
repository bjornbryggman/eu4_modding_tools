I'm currently developing a set of modules for modding a PC game called "Europa Universalis 4". So far, I've made a series of scripts that can automatically scale game assets (both GFX files and GUI files) from the native 1080p resolution to both 2K and 4K. This involves both going through the games DDS image assets and scaling them, as well as searching through the game files for GUI text files that contain positional values, which are also scaled accordingly.

The project directory structure currently looks like this:
<project_structure>
```
EU4_Modding_Tools
├─ backend
│  ├─ .env
│  ├─ app
│  │  ├─ api
│  │  │  ├─ openrouter_text_generation.py
│  │  │  ├─ replicate_image_generation.py
│  │  │  └─ __init__.py
│  │  ├─ core
│  │  │  ├─ config.py
│  │  │  ├─ db.py
│  │  │  └─ __init__.py
│  │  ├─ database
│  │  │  ├─ SQLite.db
│  │  │  └─ __init__.py
│  │  ├─ functions
│  │  │  ├─ image_processing.py
│  │  │  ├─ original_text.py
│  │  │  ├─ text_processing.py
│  │  │  ├─ text_processing_backup.py
│  │  │  └─ __init__.py
│  │  ├─ image_script.py
│  │  ├─ main.py
│  │  ├─ tests
│  │  │  ├─ tests.py
│  │  │  └─ __init__.py
│  │  ├─ text_script.py
│  │  ├─ utils
│  │  │  ├─ checks.py
│  │  │  ├─ file_utils.py
│  │  │  ├─ logging_utils.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ planning.md
│  ├─ pyproject.toml
│  ├─ README.md
│  ├─ requirements-dev.lock
│  ├─ requirements.lock
│  └─ ruff.toml
├─ frontend
├─ LICENSE
└─ README.md

```
</project_structure>

A good unit test suite should aim to:
- Test the function's behavior for a wide range of possible inputs
- Test edge cases that the author may not have foreseen
- Take advantage of the features of  pytest, pytest-asyncio, faker and hypothesis to make the tests easy to write and maintain
- Be easy to read and understand, with clean code and descriptive names
- Be deterministic, so that the tests always pass or fail in the same way

To help unit test the function above, list diverse scenarios that the function should be able to handle (and under each scenario, include a few examples as sub-bullets).