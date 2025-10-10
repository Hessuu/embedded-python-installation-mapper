#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
# List of libraries you want to install
LIBRARIES_TO_INSTALL = [
    "pydeps",
    "pyelftools",
    "fabric",
]

# The target architecture of your offline device (e.g., aarch64, x86_64)
# 'manylinux' wheels are widely compatible on Linux.
TARGET_PLATFORM = "manylinux2014_aarch64"

INSTALL_ROOT_DIR = Path("./requirements")
# --- End Configuration ---

def log(string: str = ""):
    print(string, flush=True)


def run_command(command: str):
    log(f"Running command:")
    log()
    log(f"{command}")
    log()
    process = subprocess.run(command, check=True)
    log()

    return process


def main():
    log(f"Parsing arguments...")
    parser = argparse.ArgumentParser(
        description="Install Python libraries into a portable directory for offline use."
    )
    parser.add_argument(
        "python_version",
        type=str,
        help="Target Python version for the packages (e.g., '3.12')."
    )
    args = parser.parse_args()

    py_version = args.python_version
    # Convert "3.12" to "cp312" for the ABI tag
    major_minor = "".join(py_version.split('.')[:2])
    abi_tag = f"cp{major_minor}"

    # Get version-specific directories
    install_dir = INSTALL_ROOT_DIR / py_version

    # Create the required directories
    log(f"Setting up install root directory...")
    INSTALL_ROOT_DIR.mkdir(exist_ok=True)

    # Delete old installs for this version
    log(f"Setting up install directory for version \"{py_version}\"...")
    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.mkdir()

    # Install the packages from the cache into the final target directory
    install_command = [
        sys.executable, "-m", "pip", "install",
        *LIBRARIES_TO_INSTALL,
        "--no-index",
        f"--find-links={download_dir}",
        f"--target={install_dir}",
    ]
    run_command(install_command)

    log("Done!")


if __name__ == "__main__":
    main()
