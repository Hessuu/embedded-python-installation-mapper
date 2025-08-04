#!/usr/bin/env python3

import os
import settings
import shutil
import sys

from yocto_python_packages import get_yocto_python_packages

packages = get_yocto_python_packages()

if len(sys.argv) <= 1:
    print(f"ERROR: Needs destination suffix argument!")
    sys.exit(-1)

destination_suffix_arg = sys.argv[1]

if destination_suffix_arg == "py":
    destination_suffix = settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PY
elif destination_suffix_arg == "pyc":
    destination_suffix = settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC
elif destination_suffix_arg == "pyc-opt":
    destination_suffix = settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT
elif destination_suffix_arg == "pyc-opt-os":
    destination_suffix = settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT_OS
else:
    print(f"ERROR: Invalid destination suffix: {destination_suffix_arg}")
    sys.exit(-1)

for package in packages:

    package_new_dir_name = package.recipe_name + " @ " + package.name + destination_suffix

    package_new_dir_path = settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION + "/" + package_new_dir_name

    print("")

    if os.path.isdir(package_new_dir_path):
        print(f"Removing existing directory: {package_new_dir_path}")
        shutil.rmtree(package_new_dir_path) 

    print(f"Copying directory: {package.dir}")
    shutil.copytree(package.dir, package_new_dir_path)
