import json
from pathlib import Path
from os.path import dirname

# VARIABLES
repo_loc = Path(dirname(__file__))

# IMPORT
def import_json_content(file:str):
    with open(file, 'r') as j:
        content = json.loads(j.read())
    return content

# EXPORT
def export_as_json(export_name:str, data):
    content = json.dumps(data)
    with open(export_name, "w") as outfile:
        outfile.write(content)