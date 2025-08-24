
import importlib
from pathlib import Path

def is_python_file(object_path: Path, ignore_pycs: bool = False):
    if object_path.is_file():
        # Ignore pycs. In module terms they are duplicates of .py-files.
        if ignore_pycs and object_path.suffix == ".pyc":
            return False
        
        # Normally module first name is file name without suffix.
        module_name = object_path.stem

        # With init files, module name is the containing directory name.
        if object_path.name == "__init__.py":
            module_name = object_path.parent.name

        spec = importlib.util.spec_from_file_location(module_name, object_path)
        if spec != None:
            #print(f"spec: {spec}")
            return True

    return False
