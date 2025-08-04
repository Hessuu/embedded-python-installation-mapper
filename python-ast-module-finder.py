import ast
import os
import pkgutil
import sys
from pathlib import Path

own_dir = os.path.dirname(__file__)

sys.path.append(own_dir)

from pythonmodule import PythonModule
from modulecollection import ModuleCollection

sys.path.remove(own_dir)


# For Python 3.10+
STD_LIB_MODULES = sys.stdlib_module_names

class DependencyFinder(ast.NodeVisitor):
    """
    An AST visitor that finds all imported modules in a Python file.
    It uses the module's own dotted name to resolve relative imports.
    """
    def __init__(self, source_module: PythonModule):
        self.imports = set()
        self.source_path = Path(source_module.path)
        self.module_dotted_name = source_module.full_name

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level > 0:  # This is a relative import
            if not self.module_dotted_name:
                return  # Cannot resolve relative import without knowing our own package

            is_init_file = self.source_path.name == '__init__.py'
            
            # If current file is a package's __init__.py, its name is the package name.
            # Otherwise, its name is package.module, and we need the package part.
            package_parts = self.module_dotted_name.split('.')
            if not is_init_file:
                package_parts = package_parts[:-1]
            
            # For `from .. import foo`, level is 2. We go up level-1 directories.
            if node.level > 1:
                package_parts = package_parts[:-(node.level - 1)]

            module_parts = node.module.split('.') if node.module else []
            
            full_module_path = '.'.join(package_parts + module_parts)
            if full_module_path:
                self.imports.add(full_module_path)
        
        elif node.module:  # This is an absolute import
            self.imports.add(node.module)

def find_module_path(module_name: str, search_paths: list) -> Path | None:
    """
    Tries to find the file path for a given module name.
    Handles dotted module names like 'package.module'.
    """
    module_path_parts = module_name.split('.')
    
    for search_path in search_paths:
        base_path = Path(search_path)
        
        # Check for a package directory: .../package/module/__init__.py
        potential_path = base_path.joinpath(*module_path_parts, '__init__.py')
        if potential_path.exists():
            return potential_path
            
        # Check for a .py file: .../package/module.py
        potential_path = base_path.joinpath(*module_path_parts[:-1], f'{module_path_parts[-1]}.py')
        if potential_path.exists():
            return potential_path
            
    try:
        # Fallback using pkgutil for more complex cases (e.g., C extensions)
        # This part should handle dotted names correctly already.
        spec = pkgutil.find_loader(module_name)
        if spec and hasattr(spec, 'path') and spec.path:
             return Path(spec.path)
    except (ImportError, AttributeError, ModuleNotFoundError):
        pass
        
    return None

def get_module_name_from_path(path: Path, search_paths: list[str]) -> str | None:
    """
    Converts a file path to a Python module name.
    e.g., /usr/lib/python3.12/site-packages/yt_dlp/cookies.py -> yt_dlp.cookies
    """
    resolved_path = path.resolve()
    # Sort search paths by length, longest first, to handle nested paths correctly.
    sorted_search_paths = sorted([p for p in search_paths if p], key=len, reverse=True)

    for sp_str in sorted_search_paths:
        sp = Path(sp_str).resolve()
        # Check if the search path is a parent of the module path
        if sp in resolved_path.parents:
            relative_path = resolved_path.relative_to(sp)
            
            if relative_path.name == '__init__.py':
                # /path/to/pkg/__init__.py -> pkg
                module_parts = relative_path.parent.parts
            else:
                # /path/to/pkg/mod.py -> pkg.mod
                module_parts = relative_path.with_suffix('').parts
            
            return '.'.join(module_parts)
    return None

def find_all_dependencies(entry_points: list[str], search_paths: list[str]) -> set[str]:
    """
    Recursively finds all module dependencies for a list of entry-point scripts.

    Args:
        entry_points: A list of absolute paths to the main Python applications.
        search_paths: A list of directories to search for modules (like sys.path).

    Returns:
        A set containing the names of all required modules.
    """
    modules_to_scan = ModuleCollection()
    scanned_files = ModuleCollection()
    all_dependencies = ModuleCollection()

    # Initialize with the entry points
    for point in entry_points:
        p = Path(point).resolve()
        if p.exists():
            modules_to_scan.add(PythonModule(str(p)))
        else:
            print(f"Warning: Entry point not found: {point}")

    print(f"starting modules_to_scan: {modules_to_scan}")

    while modules_to_scan:
        current_module = modules_to_scan.popitem()
        print(current_module)
        if current_module.first_name == "pdb":
            continue
        if current_module.__hash__() not in scanned_files:
            scanned_files.add(current_module)
            
            try:
                with open(current_module.path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                tree = ast.parse(source_code, filename=current_module.path)
            except (SyntaxError, UnicodeDecodeError, OSError) as e:
                print(f"Warning: Could not parse {current_module}. Reason: {e}")
                continue
    
            finder = DependencyFinder(current_module)
            finder.visit(tree)
            
            # Add found imports to our master set and the queue to be scanned
            for dep_name in finder.imports:
                module_path = find_module_path(dep_name, search_paths)
                if module_path:
                    all_dependencies.add(PythonModule(str(module_path), None, current_module.full_name))
    
                    # If it's a package (__init__.py), we scan the file.
                    # The imports within the init will lead to other files in the package.
                    modules_to_scan.add(PythonModule(str(module_path), None, current_module.full_name))
                else:
                    print("No path for: " + dep_name)
                    if dep_name in STD_LIB_MODULES:
                        all_dependencies.add(PythonModule(None, dep_name, current_module.full_name))
        else:
            all_dependencies.add(current_module)

    return all_dependencies


def find_all_available_modules(search_paths: list[str]) -> dict[str, str]:
    """
    Uses pkgutil.walk_packages to find all available modules.

    Returns:
        A dictionary mapping module names to their file paths.
    """
    all_modules = ModuleCollection()
    for module_info in pkgutil.walk_packages(search_paths):
        #if module_info.name in STD_LIB_MODULES:
        #    continue
        
        finder = module_info.module_finder
        spec = finder.find_spec(module_info.name)
        module_path = spec.origin

        if not os.path.exists(module_path):
            # Handle packages
            print("package before: " + module_path)
            module_path = os.path.join(module_info.module_finder.path, module_info.name.replace('.', '/'), '__init__.py')
            print("package after: " + module_path)
        
        if os.path.exists(module_path):
            all_modules.add(PythonModule(module_path))
        else:
            print("path not found: " + module_path)

    return all_modules


if __name__ == '__main__':
    # --- CONFIGURATION ---
    # 1. Define the entry points of your applications.
    #    Use absolute paths for reliability.
    APP_ENTRY_POINTS = [
        "/usr/bin/archivebox",
        "/usr/bin/yt-dlp",
    ]

    # 2. Define the paths where Python looks for modules.
    #    This should include the site-packages directory.
    PYTHON_SEARCH_PATHS = [
        "/usr/bin/",
        #'/path/to/your/embedded/system/lib/python3.9/site-packages/',
        # Add any other custom library paths here
    ]

    # Add system paths for broader search, but prioritize your specific paths
    PYTHON_SEARCH_PATHS.extend(sys.path)

    print(PYTHON_SEARCH_PATHS)


    print("--- Step 1: Finding all available modules ---")
    available_modules = find_all_available_modules(PYTHON_SEARCH_PATHS)
    print(f"Found {len(available_modules)} potentially removable modules.")
    available_modules.print_all("available_modules")
    print("-" * 20)


    print("--- Step 2: Analyzing application dependencies ---")
    required_modules = find_all_dependencies(APP_ENTRY_POINTS, PYTHON_SEARCH_PATHS)
    print(f"Found {len(required_modules)} required modules for the applications.")
    required_modules.print_all("required_modules")
    print("-" * 20)
    
    
    print("--- Step 3: Identifying removable modules ---")   
    available_modules_set = set(available_modules.keys()) 
    required_modules_set = set(required_modules.keys())
    # We compare the top-level module names
    removable_modules_set = available_modules_set - required_modules_set

    removable_modules = ModuleCollection()
    for key in sorted(list(removable_modules_set)):
        removable_modules.add(available_modules[key])

    print(f"Found {len(removable_modules)} modules that are not direct dependencies.")

    #removable_modules.print_all("removable_modules")

    print("\nIMPORTANT CAVEATS:")
    print("1. Dynamic Imports: This script cannot detect modules imported dynamically using `__import__()` or `importlib.import_module()` with variable names.")
    print("2. C Extensions: Analysis of compiled C extensions (.so, .pyd) is limited.")
    print("3. Data Files: This does not track non-code files that packages might need (e.g., .json, .pem, .txt).")
    print("4. Always back up your system before removing files.")

