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
    USEFUL = "USFL"                 # Always useful files.
    REQUIRED_MODULE = " REQ"        # File is present on target, and is used.
    NOT_REQUIRED_MODULE = "NREQ"    # File is present on target, but not used. Could be removed.
    USELESS = "USLS"                # File has been marked as useless due to type.
    NOT_HANDLED = "NHND"            # We can't determine if this file is used or not, due to its type.
    DIRECTORY = " DIR"              # Directories are not handled, but need special arrangements.
    UNKNOWN = "UNKN"                # We don't know what to do with this file.


class FileObject(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##

    @property
    def is_python_file(self):
        if Application.location == Location.HOST:
            return is_python_file(self.path_on_host, ignore_pycache=False)
        elif Application.location == Location.TARGET:
            return is_python_file(self.path, ignore_pycache=False)
        else:
            assert False


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

        self.found_on_target = False
        
        self.file_object_content_type = None

        # The corresponding module (i.e., Python file) found on target.
        self.python_module = None

        # The bytecode file that this file is a pycache of.
        self.pycache_of = None

    def get_status(self):
        # Most important statuses returned first to give them priority.

        # Directories need to always be flagged as such, and no other states considered.
        if self.file_object_type == FileObjectType.DIRECTORY:
            return FileObjectStatus.DIRECTORY

        # If we are a pycache file, our status is our parent's status.
        if self.pycache_of:
            return self.pycache_of.get_status()

        if self.is_useful():
            return FileObjectStatus.USEFUL

        # If file is marked as useless, it takes priority.
        if self.is_useless():
            return FileObjectStatus.USELESS

        # If file is not on device, nothing else matters.
        #if not self.found_on_target:
        #    return FileObjectStatus.NOT_FOUND

        # Python modules.
        if self.python_module:
            if self.python_module.required:
                return FileObjectStatus.REQUIRED_MODULE
            else:
                return FileObjectStatus.NOT_REQUIRED_MODULE

        # Not handled file types are the least important.
        if self.is_not_handled():
            return FileObjectStatus.NOT_HANDLED

        # Unknown if nothing else matches. This will include random text files, images, etc.
        return FileObjectStatus.UNKNOWN

    def get_string(self, file_object_size_type: FileObjectSizeType):
        status = self.get_status()

        # Get a string to show file object status.
        status_string = status.value
        
        # Get a string to show file content type.
        content_type_string = self.file_object_content_type.value

        # Get the proper size to use.
        if file_object_size_type == FileObjectSizeType.REAL_SIZE:
            size = self.real_size
        elif file_object_size_type == FileObjectSizeType.THEORETICAL_SIZE:    
            size = self.theoretical_size
        else:
            assert False
        size_string = size.format(align=True)

        # Set up the string-
        string = f"{status_string} - {content_type_string} - {size_string} - {self.path}"

        # Add importers if we have any.
        if self.python_module and len(self.python_module.importers) > 0:
            importers_string = sorted(self.python_module.importers)
            string += f" - {importers_string}"

        # Color the string according to our status.
        return self.__colorize_status_string(status, string)
    
    def is_useful(self):
        return self.__is_path_match(settings.USEFUL_PATH_MATCHES)
    
    # Check if the file object has no actual or potential use in the installation.
    def is_useless(self):
        return self.__is_path_match(settings.USELESS_PATH_MATCHES)

    # Check if the file object's usefulness cannot be determined.
    def is_not_handled(self):
        return self.__is_path_match(settings.NOT_HANDLED_PATH_MATCHES)

    @target_only
    def check_existence_on_target(self):
        # exists() won't work for symlinks.
        if self.path.is_symlink():
            self.found_on_target = True
            return

        if not self.path.exists():
            self.found_on_target = False
            return
        else:
            self.found_on_target = True
            return

    @host_and_target
    def update_theoretical_size(self):

        # On host, measure size from path on host (Yocto directory).
        if Application.location == Location.HOST:
            self.theoretical_size.measure(self.path_on_host)

        # On target, measure size from path on the target.
        elif Application.location == Location.TARGET:
            self.theoretical_size.measure(self.path)

        else:
            assert False

    @target_only
    def update_data_on_target(self, file_objects):
        # Measure real size on target
        self.real_size.measure(self.path)

        # If we are a pycache file, link us to our script.
        if self.file_object_type == FileObjectType.FILE and self.path.match("__pycache__/*"):
            if self.path.suffix != ".pyc":
                raise Exception(f"Unexpected file in pycache: {self.path}")

            script_dir_path = self.path.parent.parent
            script_filename = self.path.stem.split(".")[0] + ".py"

            script_path = script_dir_path / script_filename
            try:
                self.pycache_of = file_objects[script_path]
            except:
                raise Exception(f"Unable to find script file {script_path} for pycache file: {self.path}")

        # Get our content type
        if self.file_object_type == FileObjectType.FILE:
            self.file_object_content_type = get_file_object_content_type(self.path)
        else:
            self.file_object_content_type = FileObjectContentType.OTHER

    # Initially all data about this file is gathered from the Yocto work area.
    # With this function, the corresponding module from the target is linked
    # to it to form the complete picture.
    def link_python_module(self, python_module: PythonModule):
        self.python_module = python_module

## PRIVATE ##

    # Descriptive color for the file's status.
    def __colorize_status_string(self, status, string):
        if status == FileObjectStatus.USEFUL:
            return ColorString.dark_green(string)
        elif status == FileObjectStatus.REQUIRED_MODULE:
            return ColorString.green(string)
        elif status == FileObjectStatus.NOT_REQUIRED_MODULE:
            return ColorString.red(string)
        elif status == FileObjectStatus.USELESS:
            return ColorString.dark_red(string)
        elif status == FileObjectStatus.NOT_HANDLED:
            return ColorString.white(string)
        elif status == FileObjectStatus.DIRECTORY:
            return ColorString.gray(string)
        elif status == FileObjectStatus.UNKNOWN:
            return ColorString.purple(string)
        else:
            assert False

    @host_and_target
    def __get_file_object_type(self):
        if Application.location == Location.HOST:
            path_to_check = self.path_on_host
        elif Application.location == Location.TARGET:
            path_to_check = self.path
        else:
            assert False

        if path_to_check.is_dir():
            return FileObjectType.DIRECTORY
        else:
            return FileObjectType.FILE


    def __is_path_match(self, path_matches):
        for path_match in path_matches:
            # Check our path and all our parent directories.
            all_paths = [self.path] + list(self.path.parents)
            
            for path in all_paths:
                if path.match(path_match):
                    return True
        return False

