
import pkgutil, os, sys

from modulefinder import ModuleFinder
from pythonmodule import PythonModule
from pythonmoduleset import PythonModuleSet, SORT_BY

executables = [
    PythonModule("known_imports.py"),

]


# Find all Python modules on the system, regardless of accessibility or file format
def find_all_modules(all_modules):
    find_modules_in_pythonpath(all_modules)
    
    # Get all directories for all executables, eliminating duplicates
    executable_dirpaths = set()
    for executable in executables:
        executable_dirpath = (executable.dirpath, executable.last_name)
        executable_dirpaths.add(executable_dirpath)

    for dirpath, last_name in iter(executable_dirpaths):
        print("Finding modules in %s..." % dirpath)
        prefix = ""
        if last_name:
            prefix = last_name + "."
        find_modules_in_dirpath(all_modules, [dirpath], prefix)


# Find modules imported by all of our input executables
def find_imported_modules(imported_modules):

    finder = ModuleFinder(debug=0)

    for executable in executables:
        print("")
        print("Finding imported modules for %s..." % executable.path)
        
        # Add the executable first
        imported_modules.add(executable)
        
        path_modified = False
        if executable.dirpath not in sys.path:
            print("Adding to path: {}".format(executable.dirpath))
            sys.path.insert(0, executable.dirpath)
            path_modified = True

        finder.run_script(executable.path, executable.full_name)

        if path_modified:
            print("Removing from path: {}".format(executable.dirpath))
            sys.path.remove(executable.dirpath)

        # Clear badmodules in betweeen runs
        for name, importer in finder.badmodules.items():
            print("Failed: {} : {}".format(name, importer))

        finder.badmodules.clear()

    for name, mod in finder.modules.items():
        python_module = PythonModule(mod.__file__, name, mod.__caller_names__)
        
        print("{}      {}".format(name, mod.__caller_names__))
        
        if python_module in imported_modules:
            for imported_module in imported_modules:
                if imported_module == python_module:
                    imported_modules.remove(imported_module)
                    imported_module.importers.update(python_module.importers)
                    imported_modules.add(imported_module)
        else:
            imported_modules.add(python_module)



def find_modules_in_dirpath(all_modules, dirpath, name):
    for module_info in pkgutil.walk_packages(dirpath, name):
        finder = module_info.module_finder
        if finder:
            spec = finder.find_spec(module_info.name)
            if spec and spec.origin:
                python_module = PythonModule(spec.origin, module_info.name)
                all_modules.add(python_module)
            else:
                print("no spec with " + module_info.name)
        else:
            print("no finder with " + module_info.name)


def find_modules_in_pythonpath(all_modules):
    print("Finding modules in PYTHONPATH...")
    find_modules_in_dirpath(all_modules, None, "")


all_modules = PythonModuleSet()
find_all_modules(all_modules)

imported_modules = PythonModuleSet()
find_imported_modules(imported_modules)

unused_modules = all_modules - imported_modules
not_found_modules = imported_modules - all_modules


all_modules.print_all("All")

imported_modules.print_all("Imported")

unused_modules.print_all("Unused")

not_found_modules.print_all("Not found")
