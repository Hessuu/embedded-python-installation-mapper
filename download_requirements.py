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
]

# The target architecture of your offline device (e.g., aarch64, x86_64)
# 'manylinux' wheels are widely compatible on Linux.
TARGET_PLATFORM = "manylinux2014_aarch64"

# Names for the download directory and final archive
DOWNLOAD_ROOT_DIR = Path("./requirements-downloads")
INSTALL_ROOT_DIR = Path("./requirements")
# --- End Configuration ---


def run_command(command: str):

    process = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    return process
    

def main():
    parser = argparse.ArgumentParser(
        description="Download and install Python libraries into a portable directory for offline use."
    )
    parser.add_argument(
        "python_version",
        type=str,
        help="Target Python version for the packages (e.g., '3.12')."
    )
    args = parser.parse_args()

    py_version = args.python_version
    # Convert "3.12" to "cp312" for the ABI tag
    abi_tag = f"cp{py_version.replace('.', '')}"

    # Get version-specific directories
    download_dir = DOWNLOAD_ROOT_DIR / py_version
    install_dir = INSTALL_ROOT_DIR / py_version

    # Create the required directories
    DOWNLOAD_ROOT_DIR.mkdir(exist_ok=True)
    INSTALL_ROOT_DIR.mkdir(exist_ok=True)
    
    # Delete old downloads for this version
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
    
    # Delete old installs for this version
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

    print("Done!")


if __name__ == "__main__":
    main()
