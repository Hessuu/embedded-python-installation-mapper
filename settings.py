import sysconfig
from pathlib import Path

'''
Example configuration for an embedded device running Archivebox and all of its
out-of-the-box dependencies. Plenty of useless stuff to find and remove.

All paths should be pathlib Paths.
'''

# Target device configuration.
TARGET_ADDRESS = "192.168.1.135"
TARGET_USER = "root"
TARGET_PASSWORD = ""
TARGET_PYTHON_VERSION = "3.12.6"

# Root Yocto directory.
YOCTO_ROOT_PATH = Path.home() / "src" / "uz3eg_iocc_base_2024_2"

# Where the mapper is installed on the host device.
LOCAL_ROOT_PATH = Path(__file__).parent

# Where to install the scanner on the target device.
REMOTE_ROOT_PATH = Path("/home/root/embedded-python-installation-mapper")

# Locations of Yocto work directories. These are where Yocto packages are collected from.
YOCTO_TARGET_WORK_DIRS = {
    Path(YOCTO_ROOT_PATH / "build/tmp/work/cortexa72-cortexa53-xilinx-linux"),
}

'''
Python dependency scanning is performed for these files on the target, and them
and their dependencies are marked as required.
NOTE: Do not add any Python modules that are intended to be imported, as
then their relative imports will not be detected. Add them to known_imports.py instead. '''
ENTRY_POINT_PATHS_ON_TARGET = [
    # A file where additional imports may be added.
    Path("/home/root/embedded-python-installation-mapper/known_imports/known_imports.py"),

    # Actual entry points
    Path("/usr/bin/archivebox"),
    Path("/usr/bin/yt-dlp"),
    
]

# Additional paths on target to search Python modules from.
# Python module search path will be added to these.
ADDITIONAL_PYTHON_SEARCH_PATHS_ON_TARGET = [
    Path("/usr/bin"),
]

# Some extra paths on target to treat as Yocto packages.
PACKAGE_DIR_PATHS_ON_TARGET = [
]

USEFUL_PATH_MATCHES = [
    # Python
    "/usr/bin/python3*",
    "/usr/lib/libpython*",
]

# We do not try to figure out if these file objects are used or not.
# We assume they can be useful depending on use case.
NOT_HANDLED_PATH_MATCHES = [
    # Python
    "*.pth",

    # Systemd
    "*.preset",
    "*.service",
    
    # python3-pytz (timezone data)
    "pytz/zoneinfo"
]

# Files and directories that match any of these paths have no actual or potential use on the target.
# - If these match a file, the file is automatically considered removable.
# - If these match a directory, the directory and everything in it is automatically considered removable.
USELESS_PATH_MATCHES = [
    # Python files
    "*.pyi",
    "*.typed",

    # Cython
    "*.pyx",
    "*.pxd",
    "*.pxi",

    # Metadata
    "*.dist-info",
    "AUTHORS*",
    "LICENSE*",
    "license.txt",
    "MANIFEST*",
    "README*",

    # Tests, demos, tutorials
    "test",
    "testing",
    "tests",
    "test_*",  # Watch out!
    "turtledemo",

    # Tools
    "fetch_macholib*",

    # Documentation
    "doc",
    "docs",
    "*.md",
    "*.rst",

    # Others
    "*.c",
    "*.cpp",
    #"*.h", # python3-cffi uses these?
    "*.exe",
    "*.pyd",

    # Build artifacts
    "config-*-aarch64-linux-gnu", # Very platform-dependent
    ".flake8",
    ".git",
    ".gitignore",
    ".gitlab-ci.yml",
    ".github",
    "*.ini",
    "Makefile",
    "*.py-tpl",
    "requirements.txt",
    "setup.*",
    ".travis.yml",
]

# Everything inside these directories on the target will be added to Python installation manifest.
# These should always include the Python libdir(s) and incdir(s).
# NOTE: As these are dynamic paths, they should not be accessed on the host.
PYTHON_INSTALLATION_MANIFEST_ADDITIONAL_DIRECTORIES_ON_TARGET = [
    Path(sysconfig.get_path('stdlib')),
    Path(sysconfig.get_path('platstdlib')),
    Path(sysconfig.get_path('include')),
    Path(sysconfig.get_path('platinclude')),
]

# Ignore these file objects in Python installation manifest.
# This removes them from the file object list and prevents them from contributing to installation size.
# These should include directories that are part of Python file paths that are also common system directories.
PYTHON_INSTALLATION_MANIFEST_FILE_OBJECTS_TO_IGNORE = [
    Path("/usr"),
    Path("/usr/bin"),
    Path("/usr/include"),
    Path("/usr/lib"),
    Path("/usr/lib/systemd"),
    Path("/usr/lib/systemd/system"),
    Path("/usr/lib/systemd/system-preset"),
]
