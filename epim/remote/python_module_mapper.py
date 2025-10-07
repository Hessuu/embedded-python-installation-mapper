import json
import math
import shutil
import sys
from pathlib import Path

import settings
from epim.python_file import *
from epim.python_module import PythonModule, get_module_full_name_from_path
from epim.python_module_collection import PythonModuleCollection
from epim.util.logging import *

# For Python 3.10+
_STD_LIB_MODULE_NAMES = sys.stdlib_module_names

def _construct_search_path_strs(
        additional_search_paths: list[Path],
        own_root_dir: Path
        ) -> list[str]:

    # Python handles modules search paths as strings.
    search_path_strs = [str(path) for path in additional_search_paths]

    # Add system paths for broader search, but prioritize custom paths.
    search_path_strs.extend(sys.path)

    # Remove our own directory from paths to prevent the scanner from being included.
    own_dir_path = own_root_dir.resolve()
    own_dir_path_str = str(own_dir_path)
    if own_dir_path_str in search_path_strs:
        search_path_strs.remove(own_dir_path_str)

    print(f"Python search paths: {search_path_strs}")

    return search_path_strs


def find_all_available_modules(
        all_modules: PythonModuleCollection,
        entry_point_paths: list[Path],
        additional_search_paths: list[Path],
        own_app_root_dir: Path
        ):

    # Combine PYTHONPATH to additional search paths, and exclude our own directory.
    search_paths = _construct_search_path_strs(additional_search_paths, own_app_root_dir)

    # Start from a clean table.
    all_modules.clear()

    print(f"Finding all available Python modules...")

    print(f"Adding built-in modules...")
    built_in_module_count = 0
    for built_in_module in _STD_LIB_MODULE_NAMES:
        all_modules[built_in_module] = PythonModule(None, built_in_module, search_paths, is_built_in=True)
        built_in_module_count += 1
    print(f"Added {built_in_module_count} built-in modules.")


    # Add all entry points to Python modules.
    for entry_point_path in entry_point_paths:
        print(f"Adding entry point module: {entry_point_path}")
        all_modules[entry_point_path] = PythonModule(entry_point_path, None, search_paths, is_entry_point=True, importer=__name__)

    for search_path_str in search_paths:

        search_path = Path(search_path_str)
        if not search_path.is_dir():
            # There is a zip file in Python path by default, ignore it.
            if search_path.suffix == ".zip":
                print(f"Ignoring search path: {search_path}")
                continue
            raise Exception(f"Search path is not an existing directory: {search_path}")

        # Glob the search path and use heuristics to detect all Python files.
        print(f"Adding modules from {search_path_str}")
        for object_path in search_path.rglob("*"):
            #print(f"Checking path: {object_path}")
            if is_python_file(object_path, ignore_pycache=True):
                if not object_path in all_modules:
                    python_module = PythonModule(object_path, None, search_paths)
                    all_modules[object_path] = python_module


def find_all_dependencies(
        all_modules: PythonModuleCollection,
        entry_point_paths: list[Path],
        own_app_root_dir
        ):

    from pydeps import py2depgraph
    from pydeps.configs import Config
    from pydeps.target import Target
    
    # Own directory needs to be removed from Python path for the scan.
    if str(own_app_root_dir) in sys.path:
        sys.path.remove(str(own_app_root_dir))
        
    # Run dependency scan for each entry point.
    for ep_path in entry_point_paths:     
        '''
        For extensionless Python files like app launchers, we need to create
        a temporary copy with a Python extension. Pydeps insists on
        having an extension. '''
        if ep_path.suffix == "":
            # Added extension depends on file type. 
            python_file_type = get_file_object_content_type(ep_path)
            
            if python_file_type == FileObjectContentType.PYTHON_SCRIPT:
                ep_path_for_pydeps = ep_path.with_suffix(".py")
            elif python_file_type == FileObjectContentType.PYTHON_BYTECODE:
                ep_path_for_pydeps = ep_path.with_suffix(".pyc")
            else:
                raise Exception(f"Entry point is not a Python file: {ep_path}")

            shutil.copy(ep_path, ep_path_for_pydeps)
            ep_copied = True
        else:
            ep_path_for_pydeps = ep_path
            ep_copied = False
        
        # We need to simulate running "python <ep_path>.py", so path
        # needs to be modified similarly to how Python would do it. 
        ep_dir_str = str(ep_path.parent)

        if not ep_dir_str in sys.path:
            sys.path.insert(0, ep_dir_str)
            path_was_added = True
        else:
            path_was_added = False

        # Run pydeps. An arcane art.
        print(f"Processing dependencies for {ep_path}")

        input = Target(str(ep_path_for_pydeps), use_calling_fname=True)

        config = Config(
            no_show=True,
            no_dot=True,
            no_output=True,

            include_missing=True,
            pylib = True,
            pylib_all = True,
            max_bacon = math.inf,

            show_deps=False,
        )
        context = dict(iter(config))
                       
        dep_graph_dict = {}
        with input.chdir_work():
            context["fname"] = input.fname
            context["isdir"] = input.is_dir

            dep_graph = py2depgraph.py2dep(input, **context)

        # Convert pydeps result to a JSON dictionary.
        dep_graph_dict = json.loads(dep_graph.__json__())

        #print(dep_graph_dict)

        # Clean up path so that it does not confuse the next entry point scan.
        if path_was_added:
            sys.path.remove(ep_dir_str)

        # Delete the entry point copy with .py extension, if one was created.
        if ep_copied:
            ep_path_for_pydeps.unlink()

        # Process found dependencies and update our data structure.
        for dep_entry in dep_graph_dict.values():
            
            if dep_entry["path"]:
                dep_entry_path = Path(dep_entry["path"])
                
                # If we encounter the current entry point, redirect to the original path.
                if dep_entry_path == ep_path_for_pydeps:
                    dep_entry_path = ep_path
                
                new_importers = dep_entry["imported_by"]
                    
                all_modules[dep_entry_path].importers.update(new_importers)
                    
            else:
                # There is a large amount of 
                #print(f"No path for: {dep_entry}")
                pass

    return
