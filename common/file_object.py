from enum import Enum
from pathlib import Path

import settings
from common.python_file import *
from common.python_module import *
from common.util.color_string import *
from common.util.file_object_size import *
from common.util.location import *

class FileStatus(Enum):
    REQUIRED = "REQUIRED"           # File is present on target, and is used.
    NOT_REQUIRED = "NOT_REQUIRED"   # File is present on target, but not used. Could be removed.
    NOT_HANDLED = "NOT_HANDLED"     # We can't determine if this file is used or not, due to its type.
    NOT_FOUND = "NOT_FOUND"         # File does not seem to be on the device.
    UNINITIALIZED = "UNINITIALIZED"                 # File has not been processed yet. Error if these are present at the end.


class FileObject(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##

    @property
    def is_python_file(self):
        return is_python_file(self.path, ignore_pycs=False)

#############
## METHODS ##
#############

## PUBLIC ##

    def __init__(self, path: Path, path_on_host: Path):
        # Path on target.
        self.path = path
        # Path on host, i.e. in build directory.
        self.path_on_host = path_on_host

        self.theoretical_size = TheoreticalSize(None)
        self.real_size = RealSize(None)
        
        self.update_theoretical_size()

        # TODO: setting more permanent flags like this could be useful,
        # rather than relying on file status alone.
        self.found_on_target = False

        #TODO: use more
        # The corresponding module (i.e., Python file) found on target
        self.python_module = None

        # TODO: These should not be handled here. Flag in a printer task instead.
        if path.suffix in settings.NOT_HANDLED_FILE_TYPES:
            self.status = FileStatus.NOT_HANDLED
        else:
            # Initial state, not error right now
            self.status = FileStatus.UNINITIALIZED

    def get_string(self, file_object_size_type: FileObjectSizeType):
        
        # Get the proper size to use.
        match file_object_size_type:
            case FileObjectSizeType.REAL_SIZE:
                size = self.real_size
            case FileObjectSizeType.THEORETICAL_SIZE:    
                size = self.theoretical_size
            case _:
                raise Exception(f"Invalid size type: {file_object_size_type}")

        size_string = size.format(align=True)
        
        # Set up the string-
        string = f"{size_string} - {self.path}"

        # Add importers if we have any.
        if self.python_module and len(self.python_module.importers) > 0:
            importers_string = sorted(self.python_module.importers)
            string += f" - {importers_string}"

        # Color the string according to our status.
        return self.__colorize_status_string(string)

    @target_only
    def check_existence_on_target(self):
        if not self.path.exists():
            self.found_on_target = False
            self.status = FileStatus.NOT_FOUND
        else:
            self.found_on_target = True

    @host_and_target
    def update_theoretical_size(self):

        match Location.current:
            # On host, measure size from path on host (Yocto directory).
            case Location.HOST:
                self.theoretical_size.measure(self.path_on_host)

            # On target, measure size from path on the target.
            case Location.TARGET:
                self.theoretical_size(self.path)

            case _:
                raise Exception(f"Invalid current location: {Location.current}")

    @target_only
    def update_real_size_on_target(self):
        self.real_size.measure(self.path)

    # Initially all data on this file is gathered from the Yocto work area.
    # With this function, the corresponding module from the target is linked
    # to it to form the complete picture.
    def link_python_module(self, python_module: PythonModule):
        self.python_module = python_module

        # Figure out required state
        if len(self.python_module.importers) > 0:
            self.status = FileStatus.REQUIRED
        else:
            self.status = FileStatus.NOT_REQUIRED

## PRIVATE ##

    # Highlight problems to the user.
    def __get_problem_highlighting_string(self):
        match self.status:
            case FileStatus.REQUIRED:
                return ""
            case FileStatus.NOT_REQUIRED:
                return "NOTE: "
            case FileStatus.NOT_HANDLED:
                return ""
            case FileStatus.NOT_FOUND:
                return "ERROR: "
            case FileStatus.UNINITIALIZED:
                #TODO: Not an error when ran locally to print Yocto packages.
                return "ERROR: "
            case _:
                raise Exception(f"Invalid file status for: {self.path}")

    # Descriptive color for the file's status.
    def __colorize_status_string(self, string):
        match self.status:
            case FileStatus.REQUIRED:
                return ColorString.green(string)
            case FileStatus.NOT_REQUIRED:
                return ColorString.red(string)
            case FileStatus.NOT_HANDLED:
                return string
            case FileStatus.NOT_FOUND:
                return ColorString.red(string)
            case FileStatus.UNINITIALIZED:
                return ColorString.purple(string)
            case _:
                raise Exception(f"Invalid file status for: {self.path}")

    
