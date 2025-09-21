from enum import Enum
from pathlib import Path

import settings
from epim.application import *
from epim.python_file import *
from epim.python_module import *
from epim.util.color_string import *
from epim.util.decorators import *
from epim.util.file_object_size import *

class FileObjectType(Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"

class FileObjectStatus(Enum):
    REQUIRED = "REQUIRED"           # File is present on target, and is used.
    NOT_REQUIRED = "NOT_REQUIRED"   # File is present on target, but not used. Could be removed.
    USELESS = "USELESS"             # File has been marked as useless due to type.
    NOT_HANDLED = "NOT_HANDLED"     # We can't determine if this file is used or not, due to its type.
    NOT_FOUND = "NOT_FOUND"         # File does not seem to be on the device.
    UNKNOWN = "UNKNOWN"             # We don't know what to do with this file.


class FileObject(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##

    @property
    def is_python_file(self):
        return is_python_file(self.path, ignore_pycs=False)
        
    @property
    def not_handled(self):
        if self.path.suffix in settings.NOT_HANDLED_FILE_TYPES:
            return True
        else:
            return False


#############
## METHODS ##
#############

## PUBLIC ##

    def __init__(self, path: Path, path_on_host: Path):
        # Path on target.
        self.path = path
        # Path on host, i.e. in build directory.
        self.path_on_host = path_on_host
        
        self.file_object_type = self.__get_file_object_type()

        self.theoretical_size = TheoreticalSize(None)
        self.real_size = RealSize(None)
        
        self.update_theoretical_size()

        ''' TODO: setting more permanent flags like this could be useful,
        rather than relying on file status alone. '''
        self.found_on_target = False

        #TODO: use more
        # The corresponding module (i.e., Python file) found on target
        self.python_module = None


    def get_status(self):
        # Most important statuses returned first to give them priority.

        # If file object is not on device, nothing else matters.
        if not self.found_on_target:
            return FileObjectStatus.NOT_FOUND
        
        # If file is marked as useless, it takes priority.
        if self.is_useless():
            return FileObjectStatus.USELESS
        
        # Python modules.
        if self.python_module:
            if self.python_module.required:
                return FileObjectStatus.REQUIRED
            else:
                return FileObjectStatus.NOT_REQUIRED

        # Not handled file types are the least important.
        if self.not_handled:
            return FileObjectStatus.NOT_HANDLED

        # Unknown if nothing else matches. This will include random text files, images, etc.
        return FileObjectStatus.UNKNOWN


    def get_string(self, file_object_size_type: FileObjectSizeType):

        # Get the proper size to use.
        match file_object_size_type:
            case FileObjectSizeType.REAL_SIZE:
                size = self.real_size
            case FileObjectSizeType.THEORETICAL_SIZE:    
                size = self.theoretical_size
            case _:
                assert False
        size_string = size.format(align=True)

        # Set up the string-
        string = f"{size_string} - {self.path}"

        # Add importers if we have any.
        if self.python_module and len(self.python_module.importers) > 0:
            importers_string = sorted(self.python_module.importers)
            string += f" - {importers_string}"

        # Color the string according to our status.
        return self.__colorize_status_string(string)

    # Check if the file object has no actual or potential use in the installation.
    def is_useless(self):
        for useless_file_path_match in settings.USELESS_FILE_PATH_MATCHES:
            
            # Check our path and all our parent directories.
            all_paths = [self.path] + list(self.path.parents)
            
            for path in all_paths:
                if path.match(useless_file_path_match):
                    return True
        return False


    @target_only
    def check_existence_on_target(self):
        if not self.path.exists():
            self.found_on_target = False
        else:
            self.found_on_target = True

    @host_and_target
    def update_theoretical_size(self):

        match Application.location:
            # On host, measure size from path on host (Yocto directory).
            case Location.HOST:
                self.theoretical_size.measure(self.path_on_host)

            # On target, measure size from path on the target.
            case Location.TARGET:
                self.theoretical_size(self.path)

            case _:
                assert False

    @target_only
    def update_real_size_on_target(self):
        self.real_size.measure(self.path)

    # Initially all data about this file is gathered from the Yocto work area.
    # With this function, the corresponding module from the target is linked
    # to it to form the complete picture.
    def link_python_module(self, python_module: PythonModule):
        self.python_module = python_module

## PRIVATE ##

    # TODO: Use
    # Highlight problems to the user.
    def __get_problem_highlighting_string(self):
        match self.get_status():
            case FileObjectStatus.REQUIRED:
                return ""
            case FileObjectStatus.NOT_REQUIRED:
                return "NOTE: "
            case FileObjectStatus.NOT_HANDLED:
                return ""
            case FileObjectStatus.NOT_FOUND:
                return "ERROR: "
            case FileObjectStatus.UNINITIALIZED:
                #TODO: Not an error when ran locally to print Yocto packages.
                return "ERROR: "
            case _:
                assert False

    # Descriptive color for the file's status.
    def __colorize_status_string(self, string):
        match self.get_status():
            case FileObjectStatus.REQUIRED:
                return ColorString.green(string)
            case FileObjectStatus.NOT_REQUIRED:
                return ColorString.red(string)
            case FileObjectStatus.USELESS:
                return ColorString.dark_red(string)
            case FileObjectStatus.NOT_HANDLED:
                return string
            case FileObjectStatus.NOT_FOUND:
                return ColorString.red(string)
            case FileObjectStatus.UNKNOWN:
                return ColorString.purple(string)
            case _:
                assert False

    @host_and_target
    def __get_file_object_type(self):
        match Application.location:
            case Location.HOST:
                path_to_check = self.path_on_host
            case Location.TARGET:
                path_to_check = self.path
            case _:
                assert False

        if path_to_check.is_dir():
            return FileObjectType.DIRECTORY
        else:
            return FileObjectType.FILE
