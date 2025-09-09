from enum import Enum
from pathlib import Path

import settings
from common.file_object import *
from common.util.color_string import *
from common.util.location import *
from common.util.file_object_size import *

class PackageStatus(Enum):
    PARTLY_REQUIRED = "PARTLY_REQUIRED"        # Some files are REQUIRED, some are NOT_REQUIRED (rest may be NOT_HANDLED).
    FULLY_REQUIRED = "FULLY_REQUIRED"          # All or some files are REQUIRED (rest may be NOT_HANDLED).
    FULLY_NOT_REQUIRED = "FULLY_NOT_REQUIRED"  # All or some files are NOT_REQUIRED (rest may be NOT_HANDLED).
    FULLY_NOT_HANDLED = "FULLY_NOT_HANDLED"    # All files are NOT_HANDLED.
    NOT_ON_DEVICE = "NOT_ON_DEVICE"            # All or some files are NOT_FOUND (rest may be NOT_HANDLED).
    UNINITIALIZED = "UNINITIALIZED"                        # Starting state.

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

        for file in self.file_objects.values():
            real_size += file.real_size
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

        self.status = PackageStatus.UNINITIALIZED

        self.file_objects = None

    def get_string(self):
        self.update_status()

        # Get the proper size to use.
        if self.status == PackageStatus.NOT_ON_DEVICE:
            size = self.theoretical_size
        else:
            size = self.real_size
        size_string = size.format(align=False)

        # Add first row for basic info.
        info_string = f"{self.name} , {self.recipe_name} , {size.format()} , {self.path}"

        # Add second row for status info.
        status_string = f"{self.status.value}"

        # Get strings for our files, if our package is on the target.
        files_string = ""
        if self.status == PackageStatus.NOT_ON_DEVICE:
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
        own_string = self.__get_status_color_string(own_string)

        # Add files if we found any.
        string = f"{own_string}{files_string}"

        return string

    @host_and_target
    def populate_file_objects(self):
        self.file_objects = {}

        for file_object_local_path in self.path.rglob("*"):
            if file_object_local_path.is_file():

                match Location.current:
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

                self.file_objects[file_object.path] = file_object

            else:
                # TODO: Handle directories.
                pass

    @target_only
    def check_files_on_target(self):
        all_found = True
        all_not_found = True
        
        for file_object in self.file_objects.values():
            file_object.check_existence_on_target()

            if file_object.found_on_target:
                all_not_found = False
                file_object.update_real_size_on_target()
            else:
                all_found = False

        # If both are false it means that some file objects are missing, which is an error.
        if not all_found and not all_not_found:
            raise Exception(f"Files missing in package: {self.name}")
        
        # If both are true it means that there are no file objects.
        # These should have been filtered out, so raise error.
        if all_found and all_not_found:
            raise Exception(f"Package with no file objects: {self.name}")

    def update_status(self):
        file_object_statuses = set()

        for file_object in self.file_objects.values():
            file_object_statuses.add(file_object.status)
            
        # Package with some needed Python files and some unneeded.
        if FileStatus.REQUIRED in file_object_statuses and FileStatus.NOT_REQUIRED in file_object_statuses:
            allowed = {FileStatus.REQUIRED, FileStatus.NOT_REQUIRED, FileStatus.NOT_HANDLED, FileStatus.UNINITIALIZED}
            if file_object_statuses.issubset(allowed):
                self.status = PackageStatus.PARTLY_REQUIRED
                return

        # Package with only needed Python files.
        if FileStatus.REQUIRED in file_object_statuses:
            allowed = {FileStatus.REQUIRED, FileStatus.NOT_HANDLED, FileStatus.UNINITIALIZED}
            if file_object_statuses.issubset(allowed):
                self.status = PackageStatus.FULLY_REQUIRED
                return

        # Package with only unneeded Python files.
        if FileStatus.NOT_REQUIRED in file_object_statuses:
            allowed = {FileStatus.NOT_REQUIRED, FileStatus.NOT_HANDLED, FileStatus.UNINITIALIZED}
            if file_object_statuses.issubset(allowed):
                self.status = PackageStatus.FULLY_NOT_REQUIRED
                return

        # Package only includes files we cannot process.
        # TODO: is this actually an error?
        if file_object_statuses == {FileStatus.NOT_HANDLED}:
            self.status = PackageStatus.FULLY_NOT_HANDLED
            return

        # Package is not on the device.
        if FileStatus.NOT_FOUND in file_object_statuses:
            allowed = {FileStatus.NOT_FOUND, FileStatus.NOT_HANDLED, FileStatus.UNINITIALIZED}
            if file_object_statuses.issubset(allowed):
                self.status = PackageStatus.NOT_ON_DEVICE
                return

        # Package has not been processed yet by us.
        if FileStatus.UNINITIALIZED in file_object_statuses:
            allowed = {FileStatus.UNINITIALIZED, FileStatus.NOT_HANDLED}
            if file_object_statuses.issubset(allowed):
                self.status = PackageStatus.UNINITIALIZED
                return

        raise Exception(f"Unable to choose package status for: {self.name} with statuses: {file_object_statuses}")

## PRIVATE ##

    def __get_status_color_string(self, string):

        if self.status == PackageStatus.PARTLY_REQUIRED:
            return ColorString.yellow(string)
        elif self.status == PackageStatus.FULLY_REQUIRED:
            return ColorString.green(string)
        elif self.status == PackageStatus.UNINITIALIZED:
            return ColorString.purple(string)
        elif self.status == PackageStatus.FULLY_NOT_REQUIRED:
            return ColorString.red(string)
        elif self.status == PackageStatus.FULLY_NOT_HANDLED:
            return string
        elif self.status == PackageStatus.NOT_ON_DEVICE:
            return string
        else:
            raise Exception(f"Unable to get package status color for: {self.name} with statuses: {self.status}")
