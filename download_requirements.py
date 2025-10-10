#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
# List of libraries you want to download
LIBRARIES_TO_INSTALL = [
    "pydeps",
    "pyelftools",
    "fabric",
]

# The target architecture of your offline device (e.g., aarch64, x86_64)
# 'manylinux' wheels are widely compatible on Linux.
TARGET_PLATFORM = "manylinux2014_aarch64"

DOWNLOAD_ROOT_DIR = Path("./requirements-downloads")
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
        description="Download Python libraries into a portable directory for offline use."
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
    download_dir = DOWNLOAD_ROOT_DIR / py_version

    # Create the required directories
    log(f"Setting up download root directory...")
    DOWNLOAD_ROOT_DIR.mkdir(exist_ok=True)

    # Delete old downloads for this version
    log(f"Setting up download directory for version \"{py_version}\"...")
    if download_dir.exists():
        shutil.rmtree(download_dir)
    download_dir.mkdir()

    # Build and run the pip download command
    download_command = [
        sys.executable, "-m", "pip", "download",
        *LIBRARIES_TO_INSTALL,
        "--platform", TARGET_PLATFORM,
        "--python-version", py_version,
        "--abi", abi_tag,
        "--only-binary=:all:",
        "-d", str(download_dir),
    ]
    run_command(download_command)

    log("Done!")


if __name__ == "__main__":
    main()
