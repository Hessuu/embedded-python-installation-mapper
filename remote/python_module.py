import os, sys
from common.util.file_object_size import get_file_real_size, get_file_theoretical_size, format_size
from pathlib import Path

def _get_sorted_search_paths(search_paths: list[str]):
    sorted_search_paths = sorted(search_paths, key=len, reverse=True)
    return sorted_search_paths

def get_module_full_name_from_path(path: Path, search_paths: list[str]):
    sorted_search_paths = _get_sorted_search_paths(search_paths)

    was_on_search_paths = False
    # Remove potential search paths from path
    for search_path in sorted_search_paths:
        if path.is_relative_to(search_path):
            path = path.relative_to(search_path)
            was_on_search_paths = True

    # In case we were not on pythonpath, full name = first name
    if not was_on_search_paths:
        print(path.stem)
        return path.stem

    # Remove extension
    file_name = path.name
    module_first_name = path.stem
    module_full_name = str(path)
    module_full_name = module_full_name.replace(file_name, module_first_name)

    # Convert slashes to dots
    module_full_name = module_full_name.replace("/", ".")

    # Remove __init__
    module_full_name = module_full_name.replace(".__init__", "")

    #print(f"    {module_full_name}")
    return module_full_name

def _get_first_and_last_name(full_name):
    name_components = full_name.split(".")
    first_name = name_components[-1]
    last_name_components = name_components[:-1]
    last_name = "".join(last_name_components)
    return (first_name, last_name)

class PythonModule(object):
    def __init__(self, path: Path, full_name: str, search_paths: list[str], is_built_in: bool = False, is_entry_point: bool = False, importer: str = None):

        if path:
            real_size        = get_file_real_size(path)
            theoretical_size = get_file_theoretical_size(path)
        else:
            path = Path("")
            real_size = 0
            theoretical_size = 0

        if not full_name:
            full_name = get_module_full_name_from_path(path, search_paths)
        #first_name = full_name.split(".")[-1]
        (first_name, last_name) = _get_first_and_last_name(full_name)

        self.full_name = full_name      # tr_conf_generator.file_generators.sandbox_content
        self.first_name = first_name    # sandbox_content
        self.last_name = last_name      # tr_conf_generator.file_generators

        self.path = path

        self.real_size = real_size
        self.theoretical_size = theoretical_size

        self.is_built_in = is_built_in
        self.is_entry_point = is_entry_point

        self.importers = set()
        if importer:
            self.importers.add(importer)

    def __str__(self):
        return "(%s , %s , %s , %s)" % (self.full_name, format_size(self.real_size), self.path, sorted(self.importers))
