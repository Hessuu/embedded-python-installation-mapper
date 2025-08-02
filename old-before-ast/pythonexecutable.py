import os
from pathlib import Path

class PythonExecutable(object):
    def __init__(self, parent_name, path):

        name = Path(path).stem
        if parent_name:
            name = parent_name + "." + name
        
        self.name = name
        self.parent_name = parent_name
        self.path = path
        self.dirpath = os.path.dirname(path)
