from enum import Enum
from pathlib import Path    

class SIZE_UNIT(Enum):
    B  = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"

def format_size(size, unit=None):
    for unit_candidate in [SIZE_UNIT.B, SIZE_UNIT.KB, SIZE_UNIT.MB, SIZE_UNIT.GB, SIZE_UNIT.TB]:
        if size < 1024 or unit == unit_candidate:
            break
        size /= 1024
    
    size = size
    return f"{size:.1f} {unit_candidate.value}"

#TODO: Is lstat better than stat for file sizes?

def get_file_real_size(path: Path):
    return path.stat().st_blocks * 512

def get_file_theoretical_size(path: Path):
    return path.stat().st_size


def get_dir_real_size(path: Path):
    total_size = 0

    for file_obj in path.rglob("*"):
        if file_obj.is_file():
            total_size += get_file_real_size(file_obj)

    return total_size

def get_dir_theoretical_size(path: Path):
    total_size = 0

    for file_obj in path.rglob("*"):
        if file_obj.is_file():
            total_size += get_file_theoretical_size(file_obj)

    return total_size
