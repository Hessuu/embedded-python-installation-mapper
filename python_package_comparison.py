#!/usr/bin/env python3

import glob
import os
from colorama import Fore, Style
from pathlib import Path


import settings
from print_size_by_filetype import print_dicts_side_by_side

def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it is a symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def get_sizes_of_filetypes_in_dir(start_path):
    start_path = Path(start_path)
    total_sizes = {}

    for dirpath, dirnames, filenames in os.walk(str(start_path)):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            #skip if it is a symbolic link
            if not os.path.islink(fp):
                suffix =  "".join(Path(fp).suffixes)

                if suffix not in total_sizes:
                    total_sizes[suffix] = 0 
                total_sizes[suffix] += os.path.getsize(fp)
    return total_sizes

def print_sizes_of_filetypes_in_dir(start_path):
    sizes_by_suffix = get_sizes_of_filetypes_in_dir(start_path)

    total_size = 0
    for suffix, size in sizes_by_suffix.items():
        print(f"    {size:,} - {suffix}")
        total_size += size

    print(f"    {total_size:,} - Total")

package_dirs = set()
           
for package_dir in glob.glob(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION + "/*"):
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PY)
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC)
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT)
    package_dir = package_dir.removesuffix(settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT_OS)

    print(package_dir)

    package_dirs.add(package_dir)

for package_dir in sorted(package_dirs):
    package_dir_py = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PY
    package_dir_pyc = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC
    package_dir_pyc_opt = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT
    package_dir_pyc_opt_os = package_dir + settings.YOCTO_PYTHON_PACKAGE_COPY_DESTINATION_SUFFIX_PYC_OPT_OS

    
    package_dir_py_size = get_dir_size(package_dir_py)
    package_dir_pyc_size = get_dir_size(package_dir_pyc)
    package_dir_pyc_opt_size = get_dir_size(package_dir_pyc_opt)
    package_dir_pyc_opt_os_size = get_dir_size(package_dir_pyc_opt_os)

    print("")
    
    if package_dir_pyc_opt_size >= package_dir_pyc_size:
        print(Fore.GREEN + "######################################" + Style.RESET_ALL)
        print(Fore.GREEN + "## ALERT! Bad optimization outcome. ##" + Style.RESET_ALL)
        print(Fore.GREEN + "######################################" + Style.RESET_ALL)

    print(f"{package_dir_py_size:,} - {package_dir_py}")
    print(f"{package_dir_pyc_size:,} - {package_dir_pyc}")
    print(f"{package_dir_pyc_opt_size:,} - {package_dir_pyc_opt}")
    #print_sizes_of_filetypes_in_dir(package_dir_pyc_opt)
    print(f"{package_dir_pyc_opt_os_size:,} - {package_dir_pyc_opt_os}")
    #print_sizes_of_filetypes_in_dir(package_dir_pyc_opt_os)
    
    print_dicts_side_by_side([
        get_sizes_of_filetypes_in_dir(package_dir_pyc_opt),
        get_sizes_of_filetypes_in_dir(package_dir_pyc_opt_os)
    ])
