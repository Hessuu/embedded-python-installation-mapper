
import importlib
import subprocess
from pathlib import Path

from epim.util.logging import *

# TODO: These are very slow, measure which is faster.

# Needed specifically for Python files lacking file extensions.
def __is_native_python_file(path: Path):
    command = ["file", str(path)]
    
    command_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    if "Python script" in command_result.stdout:
        return True

    elif "Byte-compiled Python module" in command_result.stdout:
        return True

    else:
        return False

# Needed specifically for modules implemented as .so files or similar.
def __is_importable_module(path: Path):
    # Normally module first name is its file name without the suffix.
    module_name = path.stem

    # With init files, module name is the containing directory name.
    if path.name == "__init__.py":
        module_name = path.parent.name

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is not None and spec.loader is not None:
        #print(f"spec: {spec}")
        return True

    return False

def is_python_file(path: Path, ignore_pycs: bool):
    if path.is_file():

        # Try to rule out files with fast ways to avoid the slow ways.
        # We have to trust that these file extensions have not been used on non-Python files.
        if path.suffix == ".py":
            return True
        elif path.suffix == ".pyc":
            # Ignore pycs. In module terms they are duplicates of .py-files.
            if ignore_pycs:
                return False
            else:
                return True

        # Slow ways.
        if __is_importable_module(path):
            return True
        if __is_native_python_file(path):
            return True
    return False
