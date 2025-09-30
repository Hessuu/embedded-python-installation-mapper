
import collections
import glob
import time
from pathlib import Path

import settings
from epim.python_file import *
from epim.python_module_collection import *
from epim.util.decorators import *
from epim.util.file_object_size import *
from epim.package import *

class PackageCollection(collections.UserDict):
#############
## METHODS ##
#############

## PUBLIC ##

    def get_string(self):
        string = ""
        for _, package in sorted(self.items()):
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
    
    # TODO: Remove
    @host_and_target        
    def remove_packages_not_found_on_target(self):
        for package_path in sorted(list(self.keys())):
            package = self[package_path]

            package_status = package.get_status()

            if package_status == PackageStatus.NOT_ON_DEVICE:
                print(f"❌ Not found on target | {package.name}")

                # Remove it from packages.
                self.pop(package_path)
            else:
                print(f"✅ Found on target     | {package.name}")

    @target_only
    def check_existences_on_target(self):
        for package in self.values():
            package.check_existences_on_target()
