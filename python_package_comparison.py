#!/usr/bin/env python3

import glob
import os

import settings

from colorama import Fore, Style

def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it is a symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


package_dirs = set()
           
for package_dir in glob.glob(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION + "/*"):
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PY)
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC)
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT)
    print(package_dir)

    package_dirs.add(package_dir)

for package_dir in sorted(package_dirs):
    package_dir_py = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PY
    package_dir_pyc = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC
    package_dir_pyc_opt = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT
    
    
    package_dir_py_size = get_dir_size(package_dir_py)
    package_dir_pyc_size = get_dir_size(package_dir_pyc)
    package_dir_pyc_opt_size = get_dir_size(package_dir_pyc_opt)

    print("")
    
    if package_dir_pyc_opt_size >= package_dir_pyc_size:
        print(Fore.GREEN + "######################################" + Style.RESET_ALL)
        print(Fore.GREEN + "## ALERT! Bad optimization outcome. ##" + Style.RESET_ALL)
        print(Fore.GREEN + "######################################" + Style.RESET_ALL)

    print(f"{package_dir_py_size:,} - {package_dir_py}")
    print(f"{package_dir_pyc_size:,} - {package_dir_pyc}")
    print(f"{package_dir_pyc_opt_size:,} - {package_dir_pyc_opt}")
