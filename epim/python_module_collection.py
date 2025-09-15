import collections
import os
from enum import Enum

from epim.util.file_object_size import *

class SORT_BY(Enum):
    name = 1
    size = 2

def _get_title_str(name):
    title_line = "### {} ###".format(name)
    top_and_bottom_line = "#" * len(title_line)
    
    string  = "\n"
    string += top_and_bottom_line + "\n"
    string += title_line + "\n"
    string += top_and_bottom_line + "\n"
    
    return string

class PythonModuleCollection(collections.UserDict):
    def sorted_list_by_name(self):
        return sorted(
            list(self.values()),
            key=lambda x: x.full_name
        )

    def sorted_list_by_size(self):
        return sorted(
            list(self.values()),
            key=lambda x: x.real_size
        )

    def get_size(self):
        real_size = RealSize(0)
        theoretical_size = TheoreticalSize(0)

        for module in self.sorted_list_by_name():
            real_size        += module.real_size
            theoretical_size += module.theoretical_size

        return dict(
            real_size = real_size,
            theoretical_size = theoretical_size,
        )

    def get_imported_modules(self):
        imported_python_module_collection = PythonModuleCollection()

        for python_module in self.data.values():
            if len(python_module.importers) > 0:
                imported_python_module_collection[python_module.path] = python_module

        return imported_python_module_collection

    def get_unimported_modules(self):
        unimported_python_module_collection = PythonModuleCollection()

        for python_module in self.data.values():
            if len(python_module.importers) == 0:
                unimported_python_module_collection[python_module.path] = python_module

        return unimported_python_module_collection

    def print_all(self, name, sort_by=SORT_BY.name):
        string  = ""
        string += self.get_modules_str(name, sort_by=SORT_BY.name)
        string += self.get_module_count_str()
        string += self.get_size_str()
        print(string + "-" * 20)

    def get_modules_str(self, name, sort_by=SORT_BY.name):
        string = _get_title_str(name)

        sorted_list = []

        if sort_by == SORT_BY.name:
            sorted_list = self.sorted_list_by_name()
        elif sort_by == SORT_BY.size:
            sorted_list = self.sorted_list_by_size()

        for module in sorted_list:
            string += f"{name}: {module}\n"

        return string

    def get_module_count_str(self):
        module_count = len(self)

        string  = f"\n"
        string += f"## Module count ##\n"
        string += f"{module_count}\n"

        return string

    def get_size_str(self):
        size = self.get_size()
        
        string  = "\n"
        string += "## Total size ##\n"
        string += "Real size: {}\n".format(format_size(size['real_size']))
        string += "Theoretical size: {}\n".format(format_size(size['theoretical_size']))

        return string

    def __sub__(self, other):
        result = super().__sub__(other)
        return self.__class__(result)
