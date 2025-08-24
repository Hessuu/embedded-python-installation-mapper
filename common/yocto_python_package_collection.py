
import collections
import glob
import time

from pathlib import Path

import settings
from common.python_file import is_python_file
from common.yocto_package import YoctoPackage, FileStatus

glob_once_wins = 0
glob_multi_wins = 0
def is_proper_package(path: Path):
    if (
        not path.is_dir() or
        path.match("*-dbg") or
        path.match("*-dev") or
        path.match("*-doc") or
        path.match("*-lic") or
        path.match("*-locale") or
        path.match("*-src") or
        path.match("*-staticdev") or
        path.match("*-unneeded") or
        path.match("*-tests")
    ):
        return False
    else:
        return True


def package_contains_python_files(path: Path):
    for file_object in path.rglob("*"):
        if is_python_file(file_object):
            return True
    return False

def is_python_package(path: Path):
    if is_proper_package(path):
        if (
            path.name.startswith("python") or
            package_contains_python_files(path)
        ):
            return True
    return False

class YoctoPythonPackageCollection(collections.UserDict):

    def populate(self, yocto_target_work_dirs: [Path]):
        for work_dir in yocto_target_work_dirs:
            for recipe_dir in work_dir.glob("*"):
                for package_dir in recipe_dir.glob("*/packages-split/*"):
                    if is_python_package(package_dir):
                        python_package = YoctoPackage(package_dir.name, recipe_dir.name, package_dir, False)
                        self[python_package.path] = python_package

    def add_packages_on_target(self, package_dirs):
        for package_dir in package_dirs:
            python_package = YoctoPackage(package_dir.name, package_dir.name, package_dir, True)
            self[python_package.path] = python_package

    def check_files_on_target(self):
        for package in self.data.values():
            #print(f"package: {package}")
            for file in package.files.values():
                #print(f"    file: {file}")
                #print(f"        file.path: {file.path}")
                if not file.path.exists():
                    #print(f"FALSE: Package: {package.name} , File exists: {file.path}")
                    package.files[file.path].status = FileStatus.NOT_FOUND
                #else:
                    #print(f"TRUE: Package: {package.name} , File exists: {file.path}")

    def __str__(self):
        string = ""
        for yocto_package in self.values():
            string += "\n" + str(yocto_package)
        return string

def main():
    python_packages = YoctoPythonPackageCollection()
    python_packages.populate(settings.YOCTO_TARGET_WORK_ROOT)

    string = ""
    for python_package in python_packages.values():
        string += python_package.recipe_name + " "
    print(string)

if __name__ == "__main__":
    main()
