
import importlib
import subprocess
from pathlib import Path

def __file_command(path: Path, match_pattern: str):
    command = ["file", str(path)]
    
    command_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )
    
    return match_pattern in command_result.stdout

# Needed specifically for modules implemented as .so files or similar.
def __is_importable_module(path: Path):
    # Normally module first name is its file name without the suffix.
    module_name = path.stem

    # With init files, module name is the containing directory name.
    if path.name == "__init__.py":
        module_name = path.parent.name

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec != None:
        #print(f"spec: {spec}")
        return True

    return False

# Needed specifically for Python scripts lacking file extension.
def __is_python_script_file(path: Path):
    return __file_command(path, "Python script")

# Needed specifically for Python bytecode files lacking file extension.
def __is_python_bytecode_file(path: Path):
    return __file_command(path, "Byte-compiled Python module")

def is_python_file(path: Path, ignore_pycs: bool):
    if path.is_file():
        # Ignore pycs. In module terms they are duplicates of .py-files.
        if ignore_pycs and path.suffix == ".pyc":
            print(f"FALSE, PYCFILE: {path}")
            return False

        if __is_importable_module(path):
            print(f"TRUE, MODULE:   {path}")
            return True
        if __is_python_script_file(path):
            print(f"TRUE, SCRIPT:   {path}")
            return True
        if __is_python_bytecode_file(path):
            print(f"TRUE, BYTECODE: {path}")
            return True
    return False
