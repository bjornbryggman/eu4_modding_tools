# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"."

from pathlib import Path
from typing import Any

import structlog
import toml
import yaml

# Initialize logger for this module.
log = structlog.stdlib.get_logger(__name__)


def get_toml_variable(file_path: Path, variable_name: str, **kwargs: dict[str, Any]) -> dict:
    """Loads a variable from a toml file and replaces placeholders."""
    with Path.open(file_path, encoding="locale") as file:
        get_variable = toml.load(file)

    variable = get_variable[variable_name]
    content = variable["content"].format(**kwargs)
    variable["content"] = content
    return variable


def get_yaml_variable(file_path: Path, variable_name: str, **kwargs: dict[str, dict[str, Any]]) -> dict:
    """Loads a variable from a yaml file and replaces placeholders."""
    try:
        with Path.open(file_path, encoding="locale") as file:
            variable = yaml.safe_load(file)

    except FileNotFoundError as error:
        log.exception("'%s' file not found.", file_path, exc_info=error)
        raise
    except yaml.YAMLError as error:
        log.exception("Error parsing YAML file.", exc_info=error)
        raise

    else:
        get_variable = variable.get(variable_name)
        if get_variable is None:
            log.error("Variable '%s' not found in 'get_variables.yaml'.", variable_name)
            return None

        # Replace placeholders (if any).
        for key, value in get_variable.items():
            if isinstance(value, str) and value in kwargs:
                get_variable[key] = kwargs[value]

        return get_variable
