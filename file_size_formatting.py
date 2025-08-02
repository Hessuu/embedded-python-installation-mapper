from enum import Enum

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
