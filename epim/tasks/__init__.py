import ast
import importlib.util
import inspect
from pathlib import Path

__all__ = []

_task_dictionary = {}

# Get current directory
_package_dir = Path(__file__).resolve().parent

# Find all Python files in current directory
for python_file in Path(_package_dir).glob("*.py"):
    #print(f"  {python_file}")

    # Create a module name from the file path
    module_name = python_file.stem    
    if module_name == "__init__":
        continue
    
    #print(f"  {module_name}")

    # Create a module spec for the file
    spec = importlib.util.spec_from_file_location(module_name, python_file)
    if spec and spec.loader:

        # Create a module object from the spec
        module = importlib.util.module_from_spec(spec)

        # Execute the module to make its contents available
        spec.loader.exec_module(module)

        # Inspect the module for classes
        for class_name, task_class in inspect.getmembers(module, inspect.isclass):

            # Only use classes defined in the module
            if task_class.__module__ == module_name: 
                #print(f"    {class_name}")
                
                # Add class to this module's namespace
                globals()[class_name] = task_class
                
                # Add class name to __all__ for wildcard imports
                __all__.append(class_name)
                
                # Task class can by found by name
                _task_dictionary[class_name] = task_class

                #print(f"Discovered '{class_name}' in {task_class}")

#print(f"__all__:")
#print(f"{__all__}")
#print()

#print(f"_task_dictionary:")
#print(f"{_task_dictionary}")
#print()

def get_all():
    all_task_classes = {}
    
    for task_class in _task_dictionary.values():
        # Use the printable_name as the key
        all_task_classes[task_class.cli_name] = task_class

    return all_task_classes

__all__.append(get_all.__name__)


def get_visible():
    visible_task_classes = {}

    for task_class in _task_dictionary.values():
        if task_class.visible:
            # Use the printable_name as the key
            visible_task_classes[task_class.cli_name] = task_class

    return visible_task_classes

__all__.append(get_visible.__name__)


def get_class(task_name: str):
    return _task_dictionary[task_name]

__all__.append(get_class.__name__)

