
import importlib
import subprocess
from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from enum import Enum
from pathlib import Path

from epim.util.logging import *

class FileObjectContentType(Enum):
    PYTHON_SCRIPT = "SCRPT"
    PYTHON_BYTECODE = "BYTEC"
    OTHER = "OTHER"

# Needed specifically for Python files lacking file extensions.
def get_file_object_content_type(path: Path):
    command = ["file", str(path)]
    
    command_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    if "Python script" in command_result.stdout:
        # We can disregard some false-positives
        if (path.match("README*") or
            path.match("METADATA") or
            path.match("*.pyi") or
            path.match("*.tmpl") or
            path.match("*.rst") or
            path.match("*.py-tpl")
        ):
            return FileObjectContentType.OTHER
        else:
            return FileObjectContentType.PYTHON_SCRIPT

    elif "Byte-compiled Python module" in command_result.stdout:
        return FileObjectContentType.PYTHON_BYTECODE

    else:
        return FileObjectContentType.OTHER

# Needed specifically for modules implemented as .so files or similar.
def __is_importable_module(path: Path):
    #from epim.util.color_string import ColorString

    """
    Performs a deep check to see if a file path is an importable Python module
    by inspecting the binary's symbol table for the PyInit function. """
    if not path.is_file():
        return False

    # Normally module first name is its file name without the suffix.
    module_name = path.name.split('.')[0]

    # With init files, module name is the containing directory name.
    if path.name == "__init__.py":
        module_name = path.parent.name

    #print(ColorString.yellow(f"Checking {path.name}... derived module name: '{module_name}'"))

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        #print(ColorString.red(f"  -> No spec."))
        return False

    # For binary extensions, verify it has the Python init symbol.
    if isinstance(spec.loader, importlib.machinery.ExtensionFileLoader):
        symbol_name = f"PyInit_{module_name}"
        try:
            with open(path, 'rb') as f:
                elf_file = ELFFile(f)
                # Look for the dynamic symbol table.
                dynsym = elf_file.get_section_by_name('.dynsym')

                # If the table exists, search for our symbol.
                if dynsym and isinstance(dynsym, SymbolTableSection):
                    for symbol in dynsym.iter_symbols():
                        if symbol.name == symbol_name:
                            #print(ColorString.green(f"  -> It's a module!"))
                            return True

            #print(ColorString.red(f"  -> It's a binary, but missing the '{symbol_name}' symbol."))
            return False

        except ELFError:
            #print(ColorString.red(f"  -> Not a valid ELF file."))
            return False

    return True

def is_python_file(path: Path, ignore_pycache: bool):
    if path.is_file():

        # Try to rule out files with fast ways to avoid the slow ways.
        # We have to trust that these file extensions have not been used on non-Python files.
        if path.suffix == ".py":
            return True
        elif path.suffix == ".pyc":
            # Ignore pycache files if requested. In module terms they are duplicates of .py-files.
            if ignore_pycache and path.match("__pycache__/*"):
                return False
            else:
                return True

        # Slow ways.
        if __is_importable_module(path):
            return True
        if get_file_object_content_type(path) != FileObjectContentType.OTHER:
            return True

    return False
