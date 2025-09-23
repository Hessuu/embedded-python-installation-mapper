from enum import Enum
from pathlib import Path

import settings
from epim.application import *
from epim.file_object import *
from epim.util.color_string import *
from epim.util.decorators import *
from epim.util.file_object_size import *
from epim.util.logging import *

class PackageStatus(Enum):
    OK = "OK"                                   # All files are OK.
    SOME_REMOVABLE = "SOME_REMOVABLE"           # Some files are OK, but rest need attention.
    FULLY_REMOVABLE = "FULLY_REMOVABLE"         # Package can likely be removed.
    NOT_ON_DEVICE = "NOT_ON_DEVICE"             # None of the files are present on target.

class PackageType(Enum):
    HOST_AND_TARGET = "HOST_AND_TARGET"
    TARGET_ONLY = "TARGET_ONLY"

class Package(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##
    @property
    def theoretical_size(self) -> TheoreticalSize:
        theoretical_size = TheoreticalSize(0)

        for file in self.file_objects.values():
            theoretical_size += file.theoretical_size
        return theoretical_size

    @property
    def real_size(self) -> RealSize:
        real_size = RealSize(0)

        for file_object in self.file_objects.values():
            real_size += file_object.real_size
        return real_size

    @property
    def is_python_package(self) -> bool:
        ''' Check common disqualifiers. '''
        if not self.__is_proper_package:
            return False

        ''' We trust that every package starting 
        with "python" is a Python package. '''
        if self.path.name.startswith("python"):
            return True

        ''' Packages can also be Python packages
        if they contain Python files. '''
        if self.__contains_python_files:
            return True

        return False

## PRIVATE ##

    # Check if this is a package that could actually be installed to target.
    @property
    def __is_proper_package(self):
        # Package must have an existing directory.
        if not self.path.is_dir():
            return False

        # Filter out common non-target packages.
        if (
            self.path.match("*-dbg") or
            self.path.match("*-dev") or
            self.path.match("*-doc") or
            self.path.match("*-lic") or
            self.path.match("*-locale") or
            self.path.match("*-src") or
            self.path.match("*-staticdev") or
            self.path.match("*-unneeded") or
            self.path.match("*-tests")
        ):
            return False

        # Package must contain file objects.
        if len(self.file_objects) <= 0:
            return False

        return True

    @property
    def __contains_python_files(self):
        for file_object in self.file_objects.values():
            if file_object.is_python_file:
                return True
        return False

#############
## METHODS ##
#############

## PUBLIC ##

    def __init__(self, name, recipe_name, path: Path, package_type: PackageType):
        self.name = name
        self.recipe_name = recipe_name
        self.path = path

        self.package_type = package_type

        self.found_on_target = None

        self.file_objects = None

    def get_string(self):
        status = self.get_status()

        # Get the proper size to use.
        if self.found_on_target == False:
            size = self.theoretical_size
        else:
            size = self.real_size
        size_string = size.format(align=False)

        # Add first row for basic info.
        info_string = f"{self.name} , {self.recipe_name} , {size.format()} , {self.path}"

        # Add second row for status info.
        status_string = f"{status.value}"

        # Get strings for our files, if our package is on the target.
        files_string = ""
        if status == PackageStatus.NOT_ON_DEVICE:
            status_string += " - (file objects hidden)"
        else:
            pycache_found = False

            for file in self.file_objects.values():
                if file.path.match("*/__pycache__/*"):
                    pycache_found = True
                else:
                    # File objects need to print the same file size type.
                    files_string += "    " + file.get_string(size.type) + "\n"

            # Don't show pycache files to improve readability.
            if pycache_found:
                status_string += " - (pycache hidden)"

        # Create the package part of the string.
        own_string = f"{info_string}\n{status_string}\n"

        # Only color the package part.
        own_string = self.__get_status_color_string(status, own_string)

        # Add files if we found any.
        string = f"{own_string}{files_string}"

        return string

    @host_and_target
    def populate_file_objects(self):
        self.file_objects = {}

        for file_object_local_path in self.path.rglob("*"):

            match Application.location:
                # On host, remove package's directory from path.
                case Location.HOST:
                    assert self.package_type == PackageType.HOST_AND_TARGET

                    file_object_target_path = "/" / file_object_local_path.relative_to(self.path)
                    file_object = FileObject(file_object_target_path, file_object_local_path)

                # On target, path is used as-is.
                case Location.TARGET:
                    assert self.package_type == PackageType.TARGET_ONLY
                    
                    file_object_target_path = "/" / file_object_local_path
                    file_object = FileObject(file_object_target_path, None)

                case _:
                    raise Exception(f"Invalid current location: {Location.current}")

            if not file_object.path in self.file_objects:
                self.file_objects[file_object.path] = file_object

    @host_only
    def add_file_objects_to_python_installation(self, python_installation):
        for file_object_path, file_object in self.file_objects.items():
            # Add to all file objects.
            if not file_object_path in python_installation:
                python_installation[file_object_path] = file_object
            else:
                if file_object.path_on_host.is_dir():
                    # Same directory may be in multiple packages, not an error.
                    # NOTE: We lose information on which packages a directory is from.
                    pass
                else:
                    # For files it is an error to be found in multiple packages.
                    raise Exception(f"Same file present in multiple packages: {file_object.path_on_host}")

        

    @target_only
    def check_files_on_target(self):
        all_found = True
        all_not_found = True
        directories_missing = False
        
        # Check if all file objects for this package exist on target.
        for file_object in self.file_objects.values():

                file_object.check_existence_on_target()
                if file_object.found_on_target:

                    # Directories can be part of multiple packages, so if we find one
                    # for this package, it means nothing.
                    if not file_object.file_object_type == FileObjectType.DIRECTORY:
                        all_not_found = False

                    file_object.update_real_size_on_target()
                else:
                    # Files or directories missing is always an issue.
                    all_found = False

        # If both are false it means that some file objects are missing, which is an error.
        if not all_found and not all_not_found:
            raise Exception(f"Files missing in package: {self.name}")

        # If both are true it means that there are no file objects.
        # These should have been filtered out, so raise error.
        if all_found and all_not_found:
            raise Exception(f"Package with no file objects: {self.name}")
        
        # If directories are missing

        # Update own status
        if all_found:
            self.found_on_target = True
        elif all_not_found:
            self.found_on_target = False
        else:
            assert False

    def get_status(self):
        total_files = 0
        
        # These together should add up to total files
        ok_files = 0
        neutral_files = 0
        problem_files = 0
        unknown_files = 0
        not_found_files = 0

        # Count files
        for file_object in self.file_objects.values():

            # Ignore directories, their usefulness is not handled,
            # and they can be part of multiple packages.
            if file_object.file_object_type == FileObjectType.DIRECTORY:
                continue

            # All
            total_files += 1
            
            match file_object.get_status():
                case FileObjectStatus.REQUIRED:
                    ok_files += 1
                case FileObjectStatus.NOT_REQUIRED:
                    problem_files += 1
                case FileObjectStatus.USELESS:
                    problem_files += 1
                case FileObjectStatus.NOT_HANDLED:
                    neutral_files += 1
                case FileObjectStatus.NOT_FOUND:
                    not_found_files += 1
                case FileObjectStatus.DIRECTORY:
                    assert False
                case FileObjectStatus.UNKNOWN:
                    neutral_files += 1
                case _:
                    raise Exception(f"Invalid file status for: {file_object.path}")

        # Check for errors
        # Empty?
        assert total_files > 0
        # File counting error?
        assert total_files == ok_files + neutral_files + problem_files + unknown_files + not_found_files
        # All files unknown?
        assert total_files != unknown_files 
        # Missing files? Could be user error.
        if not_found_files > 0 and not_found_files != total_files:
            raise Exception(f"Some files missing for package: {self.name}")

        # Statuses, no particular order should be needed.
        if total_files == ok_files + neutral_files:
            return PackageStatus.OK

        if ok_files > 0 and problem_files > 0:
            return PackageStatus.SOME_REMOVABLE

        if total_files == problem_files + neutral_files:
            return PackageStatus.FULLY_REMOVABLE

        if total_files == not_found_files:
            return PackageStatus.NOT_ON_DEVICE


        raise Exception(f"Unable to choose package status for: {self.name}")

## PRIVATE ##

    def __get_status_color_string(self, status, string):
        
        match status:
            case PackageStatus.OK:
                return ColorString.green(string)
            case PackageStatus.SOME_REMOVABLE:
                return ColorString.yellow(string)
            case PackageStatus.FULLY_REMOVABLE:
                return ColorString.red(string)
            case PackageStatus.NOT_ON_DEVICE:
                return string
            case _:
                raise Exception(f"Unable to get package status color for: {self.name} with statuses: {status}")
            
