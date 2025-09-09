import json
import math
import shutil
import sys
from pathlib import Path

from common.python_file import is_python_file
from common.python_module import PythonModule, get_module_full_name_from_path
from common.python_module_collection import PythonModuleCollection

# For Python 3.10+
STD_LIB_MODULES = sys.stdlib_module_names

def construct_search_paths(
        additional_search_paths: list[str],
        own_app_root_dir: Path
        ):

    search_paths = additional_search_paths

    # Add system paths for broader search, but prioritize custom paths.
    search_paths.extend(sys.path)

    # Remove our own directory from paths to prevent the scanner from being included.
    own_dir_path = own_app_root_dir.resolve()
    own_dir_path_str = str(own_dir_path)
    if own_dir_path_str in search_paths:
        search_paths.remove(own_dir_path_str)

    print(f"Python search paths: {search_paths}")

    return search_paths


def find_all_available_modules(
        all_modules: PythonModuleCollection,
        entry_points: list[str],
        additional_search_paths: list[str],
        own_app_root_dir: Path
        ):

    search_paths = construct_search_paths(additional_search_paths, own_app_root_dir)

    all_modules.clear()

    for built_in_module in STD_LIB_MODULES:
        print(f"Adding built-in module: {built_in_module}")
        all_modules[built_in_module] = PythonModule(None, built_in_module, search_paths, is_built_in=True)

    for entry_point in entry_points:
        entry_point_path = Path(entry_point)
        print(f"Adding entry point module: {entry_point_path}")
        all_modules[entry_point_path] = PythonModule(entry_point_path, None, search_paths, is_entry_point=True, importer=__name__)

    for search_path_str in search_paths:
        search_path = Path(search_path_str)
        if not search_path.is_dir():
            # There is a zip file in Python path by default.
            if search_path.suffix == ".zip":
                print(f"Ignoring search path: {search_path}")
                continue
            raise Exception(f"Search path is not an existing directory: {search_path}")

        for object_path in search_path.rglob("*"):
            if is_python_file(object_path, ignore_pycs=True):
                if not object_path in all_modules:
                    python_module = PythonModule(object_path, None, search_paths)
                    all_modules[object_path] = python_module


def find_all_dependencies(
        all_modules: PythonModuleCollection,
        entry_points: list[str],
        own_app_root_dir
        ):

    from pydeps import py2depgraph
    from pydeps.configs import Config
    from pydeps.target import Target
    
    # Own direcory needs to be removed from Python path for the duration of the scan
    if str(own_app_root_dir) in sys.path:
        sys.path.remove(str(own_app_root_dir))

    for entry_point in entry_points:        
        '''
        We need to simulate running "python <entry_point>.py", so path needs to be modified
        similar to how python would do it.
        '''
        entry_point_dir = str(Path(entry_point).parent)
        print(f"entry_point_dir: {entry_point_dir}")

        path_was_added = False
        if not entry_point_dir in sys.path:
            print("Not In path!")
            print(f"path before modifying: {sys.path}")
            sys.path.insert(0, entry_point_dir)
            print(f"path after modifying: {sys.path}")
            path_was_added = True
        else:
            print("In path!")

        input = Target(entry_point, use_calling_fname=True)

        print(f"Processing dependencies for {entry_point}")
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

        dep_graph_dict = json.loads(dep_graph.__json__())
        #print(dep_graph_dict)

        if path_was_added:
            sys.path.remove(entry_point_dir)
            print(f"Path after processing: {sys.path}")

        for dep_entry in dep_graph_dict.values():
            #print(f"{dep_entry['name']} , {dep_entry['path']}")
            #print(f"    {dep_entry}")
            #print()

            if dep_entry["path"]:
                dep_entry_path = Path(dep_entry["path"])
                #print(all_modules[dep_entry_path])
                all_modules[dep_entry_path].importers.update(dep_entry["imported_by"])
                    
                #print(all_modules[dep_entry_path])
            else:
                #print(f"No path for: {dep_entry}")
                pass

    return
