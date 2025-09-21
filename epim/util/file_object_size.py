from enum import Enum
from pathlib import Path    

from epim.util.decorators import *

class FileObjectSizeType(Enum):
    REAL_SIZE = "R"
    THEORETICAL_SIZE = "T"

class SizeUnit(Enum):
    B  = "B"
    KIB = "KiB"
    MIB = "MiB"
    GIB = "GiB"
    TIB = "TiB"


class Size():

    @property
    def bytes(self):
        return self._bytes
    @property
    def type(self):
        return self.__type

    def __init__(self, bytes: int, type: FileObjectSizeType):
        self._bytes = bytes
        self.__type = type
    def format(self, align: bool = False, unit: SizeUnit = None):
        size = self._bytes

        ''' Select size unit.
        Use the smallest unit where the number to print would
        be smaller than 1024. Use user-specified type, if given.'''
        for unit_candidate in list(SizeUnit):
            if unit:
                if unit == unit_candidate:
                    break
            else:
                if size < 1024:
                    break
            size /= 1024

        ''' Prepare string components. '''
        size_type_string = self.type.value
        size_string = f"{size:.1f}"
        unit_string = unit_candidate.value

        ''' Align everything if requested. '''
        if align:
            size_string = size_string.rjust(6)
            unit_string = unit_string.rjust(3)

        return f"{size_type_string} {size_string} {unit_string}"
    
    def __add__(self, other):
        # Not allowed to mix between different size types.
        if   isinstance(other, self.__class__):
            return self.__class__(self.bytes + other.bytes)
        
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)


class RealSize(Size):
    def __init__(self, value):
        return super().__init__(value, FileObjectSizeType.REAL_SIZE)
    
    @target_only
    def measure(self, path: Path):
        self._bytes = path.stat(follow_symlinks=False).st_blocks * 512


class TheoreticalSize(Size):
    def __init__(self, value):
        return super().__init__(value, FileObjectSizeType.THEORETICAL_SIZE)

    # TODO: Is lstat better than stat for file sizes?
    @host_and_target
    def measure(self, path: Path):
        self._bytes = path.stat(follow_symlinks=False).st_size


'''
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
'''