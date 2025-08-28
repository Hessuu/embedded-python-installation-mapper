from enum import Enum
from pathlib import Path

from common.util import color_string
import settings
from common.util.file_object_size import get_file_theoretical_size, format_size


class FileStatus(Enum):
    REQUIRED = "REQUIRED"          # File is present on target, and is used.
    NOT_REQUIRED = "NOT_REQUIRED"  # File is present on target, but not used. Could be removed.
    NOT_HANDLED = "NOT_HANDLED"    # We can't determine if this file is used or not, due to its type.
    NOT_FOUND = "NOT_FOUND"        # File does not seem to be on the device.
    NEUTRAL = "NEUTRAL"            # File has not been processed yet. Error if these are present at the end.

class PackageStatus(Enum):
    PARTLY_REQUIRED = "PARTLY_REQUIRED"        # Some files are REQUIRED, some are NOT_REQUIRED (rest may be NOT_HANDLED).
    FULLY_REQUIRED = "FULLY_REQUIRED"          # All or some files are REQUIRED (rest may be NOT_HANDLED).
    FULLY_NOT_REQUIRED = "FULLY_NOT_REQUIRED"  # All or some files are NOT_REQUIRED (rest may be NOT_HANDLED).
    FULLY_NOT_HANDLED = "FULLY_NOT_HANDLED"    # All files are NOT_HANDLED.
    NOT_ON_DEVICE = "NOT_ON_DEVICE"            # All or some files are NOT_FOUND (rest may be NOT_HANDLED).
    NEUTRAL = "NEUTRAL"                        # Starting state.

class YoctoPackageFile(object):
    def __init__(self, path: Path, theoretical_size: int):
        self.path = path
        self.theoretical_size = theoretical_size
        # Real size comes from self.target_module

        #TODO: use more
        # The corresponding module(i.e., file) found on target
        self.target_module = None

        if path.suffix in settings.NOT_HANDLED_FILE_TYPES:
            self.status = FileStatus.NOT_HANDLED
        else:
            self.status = FileStatus.NEUTRAL

    def get_status_color_string(self, string):
        if   self.status == FileStatus.REQUIRED:
            return color_string.green(string)
        elif self.status == FileStatus.NEUTRAL:
            return color_string.purple(string)
        elif self.status == FileStatus.NOT_REQUIRED:
            return color_string.red(string)
        elif self.status == FileStatus.NOT_HANDLED:
            return string
        elif self.status == FileStatus.NOT_FOUND:
            return color_string.red(string)
        else:
            raise Exception(f"Invalid file status for: {self.path}")


    def __str__(self):
        importers = ""
        if self.target_module and len(self.target_module.importers) > 0:
            importers = sorted(self.target_module.importers)
        
        if self.target_module:
            size_to_print = f"r {self.target_module.real_size}"
        else:
            size_to_print = f"t {self.theoretical_size}"
        
        return self.get_status_color_string(f"{format_size(size_to_print).rjust(8)} - {self.path} - {importers}")

class YoctoPackage(object):
    def __init__(self, name, recipe_name, path: Path, only_on_target: bool):
        self.name = name
        self.recipe_name = recipe_name
        self.path = path

        self.files = {}
        self.theoretical_size = None
        self.real_size = None

        self.status = PackageStatus.NEUTRAL
        
        self.only_on_target = only_on_target

        self.populate_files()
        self.calculate_theoretical_size()

    def populate_files(self):
        self.files.clear()
        
        for file_obj in self.path.rglob("*"):
            if file_obj.is_file():
                if self.only_on_target:
                    yocto_package_file = YoctoPackageFile("/" / file_obj, get_file_theoretical_size(file_obj))
                else:
                    yocto_package_file = YoctoPackageFile("/" / file_obj.relative_to(self.path), get_file_theoretical_size(file_obj))
                
                self.files[yocto_package_file.path] = yocto_package_file

    def calculate_theoretical_size(self):
        self.theoretical_size = 0
        for file in self.files.values():
            self.theoretical_size += file.theoretical_size

    def calculate_real_size(self):
        self.real_size = 0
        for file in self.files.values():
            self.real_size += file.target_module.real_size

    def update_own_status(self):
        file_statuses = set()

        for file in self.files.values():
            file_statuses.add(file.status)

        #print(file_statuses)

        if FileStatus.REQUIRED in file_statuses and FileStatus.NOT_REQUIRED in file_statuses:
            allowed = {FileStatus.REQUIRED, FileStatus.NOT_REQUIRED, FileStatus.NOT_HANDLED, FileStatus.NEUTRAL}
            if file_statuses.issubset(allowed):
                self.status = PackageStatus.PARTLY_REQUIRED
                return

        if FileStatus.REQUIRED in file_statuses:
            allowed = {FileStatus.REQUIRED, FileStatus.NOT_HANDLED, FileStatus.NEUTRAL}
            if file_statuses.issubset(allowed):
                self.status = PackageStatus.FULLY_REQUIRED
                return

        if FileStatus.NOT_REQUIRED in file_statuses:
            allowed = {FileStatus.NOT_REQUIRED, FileStatus.NOT_HANDLED, FileStatus.NEUTRAL}
            if file_statuses.issubset(allowed):
                self.status = PackageStatus.FULLY_NOT_REQUIRED
                return

        if file_statuses == {FileStatus.NOT_HANDLED}:
            self.status = PackageStatus.FULLY_NOT_HANDLED
            return
        if len(file_statuses) == 0:
            self.status = PackageStatus.FULLY_NOT_HANDLED
            return

        if FileStatus.NOT_FOUND in file_statuses:
            allowed = {FileStatus.NOT_FOUND, FileStatus.NOT_HANDLED, FileStatus.NEUTRAL}
            if file_statuses.issubset(allowed):
                self.status = PackageStatus.NOT_ON_DEVICE
                return

        if FileStatus.NEUTRAL in file_statuses:
            allowed = {FileStatus.NEUTRAL, FileStatus.NOT_HANDLED}
            if file_statuses.issubset(allowed):
                self.status = PackageStatus.NEUTRAL
                return

        raise Exception(f"Unable to choose package status for: {self.name} with statuses: {file_statuses}")

    def get_status_color_string(self, string):

        if self.status == PackageStatus.PARTLY_REQUIRED:
            return color_string.yellow(string)
        elif self.status == PackageStatus.FULLY_REQUIRED:
            return color_string.green(string)
        elif self.status == PackageStatus.NEUTRAL:
            return color_string.purple(string)
        elif self.status == PackageStatus.FULLY_NOT_REQUIRED:
            return color_string.red(string)
        elif self.status == PackageStatus.FULLY_NOT_HANDLED:
            return string
        elif self.status == PackageStatus.NOT_ON_DEVICE:
            return string
        else:
            raise Exception(f"Unable to get package status color for: {self.name} with statuses: {self.status}")

    def __str__(self):
        self.update_own_status()

        # Basic information
        string = self.get_status_color_string(f"{self.name} , {self.recipe_name} , {format_size(self.theoretical_size)} , {self.path} {self.status.value}")

        # Print files only if present on device
        if not self.status == PackageStatus.NOT_ON_DEVICE:
            pyc_files_hidden_str = ""
            files_string = ""

            for file in self.files.values():
                if file.path.match("*/__pycache__/*"):
                    pyc_files_hidden_str = " (pycache hidden)"
                else:
                    files_string += "    " + str(file) + "\n"
            string += pyc_files_hidden_str + "\n" + files_string
        
        else:
            string += " (files hidden)\n"

        return string
