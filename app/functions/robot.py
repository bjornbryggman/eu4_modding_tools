# Copyright (C) 2024 Björn Gunnar Bryggman. Licensed under the MIT License.

"""
Agent module.

Creating cool shit.

"""

import ast
import json
import pathlib

import tomli


def generate_file_tree_json(path, exclude_folders=None):
    if exclude_folders is None:
        exclude_folders = [".venv", "__pycache__", ".git", "robot", "commands.toml", ".tx"]  # default exclude folders

    file_tree = {}
    for item in path.iterdir():
        if item.is_file():
            if item.suffix == ".py":
                file_tree[item.name] = {"type": "file", "functions": get_functions_from_file(item)}
            else:
                file_tree[item.name] = {"type": "file"}
        elif item.is_dir() and item.name not in exclude_folders:
            file_tree[item.name] = {"type": "dir", "contents": generate_file_tree_json(item, exclude_folders)}
    return json.dumps(file_tree, indent=4)


def get_functions_from_file(file_path):
    functions = []
    with file_path.open("r") as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                functions.append({"name": node.name, "docstring": docstring})
    return functions


def find_root_dir(path):
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    raise ValueError("Could not find pyproject.toml file in the directory tree")


def scan_pyproject_toml():
    root_dir = find_root_dir(pathlib.Path.cwd())
    pyproject_toml_path = root_dir / "pyproject.toml"
    try:
        with pyproject_toml_path.open("rb") as f:
            pyproject_toml = tomli.load(f)
    except FileNotFoundError:
        raise ValueError("Could not find pyproject.toml file in the project directory")
    return pyproject_toml


if __name__ == "__main__":
    root_dir = find_root_dir(pathlib.Path.cwd())
    pyproject_toml = scan_pyproject_toml()
    print("Pyproject.toml:")
    print(pyproject_toml)
    print("\nFile Tree:")
    file_tree_json = generate_file_tree_json(root_dir)
    print(file_tree_json)
