# ===========================================================================
#                            File Operations
# ===========================================================================

import json
import os


def readJSON(file_path, encoding='utf-8'):
    """
    Imports a JSON file from the given path and returns the data as a Python object.
    """
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)
    return data


def validatePath(path: str) -> str:
    """Returns a valid path or prints an error message"""

    if not os.path.exists(path):
        print(f"Directory or file {path} does not exist.")
        exit()

    return path
