# embedded-python-installation-mapper
## Old host main
```
import os
import pickle
import settings

from session import Session

session = Session()

print("## GETTING YOCTO PACKAGES... ##")

session.yocto_packages.populate(settings.YOCTO_TARGET_WORK_DIRS)

print("## SERIALIZING SESSION... ##")

pickle_dump = pickle.dumps(session)

print("## WRITING SESSION FILE... ##")

os.remove(settings.SESSION_FILE)

with open(settings.SESSION_FILE, "wb") as session_file:
    session_file.write(pickle_dump)

print("## HOST SIDE DONE. ##")
```

## Old target main
```
import pickle
import settings
import sys
from pathlib import Path

import python_module_mapper
from yocto_package import FileStatus

session = None

with open(settings.SESSION_FILE, "rb") as session_file:
    session_file_string = session_file.read()
    session = pickle.loads(session_file_string)

# Add packages from target
session.yocto_packages.add_packages_on_target(settings.PACKAGE_DIRS_ON_TARGET)

# Mark all existing files as existing
session.yocto_packages.check_files_on_target()
#print(session.yocto_packages)
#print()

# --- CONFIGURATION ---
# 1. Define the entry points of your applications.
#    Use absolute paths for reliability.
APP_ENTRY_POINTS = [
    "/home/root/known_imports.py",
]

# 2. Define the paths where Python looks for modules.
#    This should include the site-packages directory.
PYTHON_SEARCH_PATHS = [
    "/usr/bin",
]

# Add system paths for broader search, but prioritize your specific paths
PYTHON_SEARCH_PATHS.extend(sys.path)

own_dir_path = Path(__file__).parent.resolve()
own_dir_path_str = str(own_dir_path)
PYTHON_SEARCH_PATHS.remove(own_dir_path_str)
print(f"OWN_DIR: {own_dir_path_str}")

print(f"PYTHON_SEARCH_PATHS: {PYTHON_SEARCH_PATHS}")

print("--- Step 1: Finding all available modules ---")
python_module_mapper.find_all_available_modules(session.target_modules, APP_ENTRY_POINTS, PYTHON_SEARCH_PATHS)
session.target_modules.print_all("available_modules")

print("--- Step 2: Analyzing application dependencies ---")
python_module_mapper.find_all_dependencies(session.target_modules, APP_ENTRY_POINTS, PYTHON_SEARCH_PATHS)

required_modules = session.target_modules.get_imported_modules()
required_modules.print_all("required_modules")

print("--- Step 3: Identifying removable modules ---")
unneeded_modules = session.target_modules.get_unimported_modules()
unneeded_modules.print_all("unneeded_modules")

print("--- Step 4: Matching modules to Yocto packages ---")
for python_module in session.target_modules.values():
    module_found_from_packages = False
    #TODO: remove this debug string stuff, it's slow
    #debug_str = ""
    
    for yocto_package in session.yocto_packages.values():
        #debug_str += yocto_package.name + "\n"
        for yocto_file in yocto_package.files.values():
            #debug_str += f"    {yocto_file.path}\n"
            if python_module.path == yocto_file.path:
                module_found_from_packages = True

                if len(session.target_modules[python_module.path].importers) > 0:
                    yocto_file.status = FileStatus.REQUIRED
                else:
                    yocto_file.status = FileStatus.NOT_REQUIRED

    if not module_found_from_packages:
        if python_module.is_built_in:
            continue
        if python_module.is_entry_point:
            print(f"Entry point not found from packages, ignoring: {python_module.path}")
            continue

        raise Exception(f"Module not found from packages: {python_module}")

print(session.yocto_packages)

print("\nIMPORTANT CAVEATS:")
print("1. Dynamic Imports: This script cannot detect modules imported dynamically using `__import__()` or `importlib.import_module()` with variable names.")
print("2. C Extensions: Analysis of compiled C extensions (.so, .pyd) is limited.")
print("3. Data Files: This does not track non-code files that packages might need (e.g., .json, .pem, .txt).")
print("4. Always back up your system before removing files.")

```
