
import collections
import glob
import time

from pathlib import Path

import settings
from common.python_file import *
from common.python_module_collection import *
from common.util.location import *
from common.util.file_object_size import *
from common.package import *

class PackageCollection(collections.UserDict):
#############
## METHODS ##
#############

## PUBLIC ##

    def get_string(self):
        string = ""
        for package in self.values():
            string += "\n" + package.get_string()
        return string
    
    @host_only
    def populate_on_host(self, yocto_target_work_dirs: [Path]):
        for work_dir in yocto_target_work_dirs:
            assert(work_dir.exists())

            for recipe_dir in work_dir.glob("*"):
                for package_dir in recipe_dir.glob("*/packages-split/*"):
                    if package_dir.is_dir():
                        package = Package(package_dir.name, recipe_dir.name, package_dir, PackageType.HOST_AND_TARGET)

                        package.populate_file_objects()
                        
                        if package.is_python_package:
                            self[package.path] = package
                        else:
                            # Not error, we will find many non-Python packages.
                            pass

    @target_only
    def add_packages_on_target(self, package_dirs):        
        for package_dir in package_dirs:
            package = Package(package_dir.name, package_dir.name, package_dir, PackageType.TARGET_ONLY)
            
            package.populate_file_objects()
            
            if package.is_python_package:
                self[package.path] = package
            else:
                raise Exception(f"User-defined package on target at {package_dir} is not a valid Python package!")

    @target_only
    def update_package_statuses_on_target(self):
        for package in self.values():
            package.check_files_on_target()

    @host_only
    def combine_with_python_module_data(self, python_modules: PythonModuleCollection):
        for python_module in python_modules.values():
            module_found_from_packages = False

            for package in self.values():

                if python_module.path in package.file_objects:
                    module_found_from_packages = True

                    file_object = package.file_objects[python_module.path]

                    file_object.link_python_module(python_module)

            if not module_found_from_packages:
                if python_module.is_built_in:
                    continue
                if python_module.is_entry_point:
                    print(f"Entry point not found from packages, ignoring: {python_module.path}")
                    continue

                raise Exception(f"Module not found from packages: {python_module}")

        # TODO: Check that all Python files in all packages have been handled in some way
