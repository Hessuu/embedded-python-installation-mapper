import os, sys
from file_size_formatting import format_size
from pathlib import Path

def _get_real_size(path):
    stat_info = os.lstat(path)
    return stat_info.st_blocks * 512

def _get_theoretical_size(path):
    return os.path.getsize(path)

def _get_sorted_sys_path():
    sys_path = sys.path
    sys_path.sort(key=len, reverse=True)
    return sys_path

def _get_full_name(path):
    sys_path = _get_sorted_sys_path()
    
    #print(sys_path)
    #print(path)
    
    was_on_path = False
    # Remove possible python paths from path
    for sys_path_entry in sys_path:
        if sys_path_entry in path:
            path = path.replace(sys_path_entry, "")
            was_on_path = True

    #print(path)

    # In case we were not on pythonpath, full name = first name
    if not was_on_path:
        path = os.path.basename(path)

    #print(path)
    # Remove leading slash
    path = path.lstrip("/")
    

    # Remove extension
    file_name = os.path.basename(path)
    module_name = Path(path).stem
    path = path.replace(file_name, module_name)

    #print(path)

    # Convert slashes to dots
    path = path.replace("/", ".")
    
    #print(path)
    
    return path

def _get_first_and_last_name(full_name):
    name_components = full_name.split(".")
    first_name = name_components[-1]
    last_name_components = name_components[:-1]
    last_name = "".join(last_name_components)
    return (first_name, last_name)

class PythonModule(object):
    def __init__(self, path=None, full_name=None, importer=None):

        if path:
            real_size        = _get_real_size(path)
            theoretical_size = _get_theoretical_size(path)
        else:
            # This is a built-in
            path = ""
            real_size = 0
            theoretical_size = 0

        if not full_name:
            full_name = _get_full_name(path)
        #first_name = full_name.split(".")[-1]
        (first_name, last_name) = _get_first_and_last_name(full_name)

        self.full_name = full_name      # tr_conf_generator.file_generators.sandbox_content
        self.first_name = first_name    # sandbox_content
        self.last_name = last_name      # tr_conf_generator.file_generators

        self.path = path
        self.dirpath = os.path.dirname(path)

        self.real_size = real_size
        self.theoretical_size = theoretical_size
        
        importers = set()
        if importer:
            importers.add(importer)
            
        self.importers = importers

    def __repr__(self):
        return "(%s , %s , %s ----- %s)" % (self.full_name, format_size(self.real_size), self.path, sorted(self.importers))

    def __eq__(self, other):
        if isinstance(other, PythonModule):
            # TODO: use module first name as UID?
            return (self.first_name == other.first_name and
                    self.path == other.path)
        else:
            return False

    def __hash__(self):
        return hash(self.path + " " + self.first_name)

