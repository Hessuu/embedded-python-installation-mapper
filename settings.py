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

# These Python files on the target are automatically considered required,
# and therefore all their dependencies are also considered required.
ENTRY_POINT_PATHS_ON_TARGET = [
    Path("/usr/bin/archivebox"),
    Path("/usr/bin/yt-dlp"),
    
    # The Archivebox commands that the current server configuration runs.
    # These are here because Archivebox calls these dynamically, which we can't detect.
    Path("/usr/lib/python3.12/site-packages/archivebox/cli/archivebox_init.py"),
    Path("/usr/lib/python3.12/site-packages/archivebox/cli/archivebox_server.py"),
    
    # A file where additional imports may be added.
    Path("/home/root/embedded-python-installation-mapper/known_imports.py"),
]

# Additional paths on target to search Python modules from.
# Python module search path will be added to these.
ADDITIONAL_PYTHON_SEARCH_PATHS_ON_TARGET = [
    Path("/usr/bin"),
]

# Some extra paths on target to treat as Yocto packages.
PACKAGE_DIR_PATHS_ON_TARGET = [
]

# We do not try to figure out if these file types are used or not.
NOT_HANDLED_FILE_TYPES = [
    # Python
    ".pth",

    # Systemd
    ".preset",
    ".service",
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

    # Documentation
    "doc",
    "docs",
    "*.md",
    "*.rst",

    # Others
    "*.c",
    "*.cpp",
    "*.h",
    "*.exe",
    "*.pyd",

    # Build artifacts
    "config-*-aarch64-linux-gnu", # Very platform-dependent
    ".git",
    ".gitignore",
    ".gitlab-ci.yml",
    ".github",
    "*.ini",
    "Makefile",
    "*.py-tpl",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    ".travis.yml",
]
