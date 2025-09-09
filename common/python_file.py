
import importlib
from pathlib import Path

# Needed specificlly for modules implemented as .so files or similar.
def __is_importable_module():
    is_importable_module = False
    
    return is_importable_module

# Needed specifically for Python scripts lacking file extension.
def __is_python_script_file():
    is_python_script = False
    
    return is_python_script

# Needed specifically for Python bytecode files lacking file extension.
def __is_python_bytecode_file():
    is_python_bytecode = False
    
    return is_python_bytecode


def is_python_file(object_path: Path, ignore_pycs: bool):
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
