import os
from file_size_formatting import format_size
from enum import Enum
from collections import UserDict
from pythonmodule import PythonModule

class SORT_BY(Enum):
    name = 1
    size = 2

def _print_title(name):
    title_line = "### {} ###".format(name)
    top_and_bottom_line = "#" * len(title_line)
    
    print("")
    print(top_and_bottom_line)
    print(title_line)
    print(top_and_bottom_line)

class ModuleCollection(UserDict):
    def add(self, module: PythonModule):
        """Adds a module to the collection using its path as the key."""
        if module.__hash__() not in self.data:
            self.data[module.__hash__()] = module
        else:
            self.data[module.__hash__()].importers.update(module.importers)
            
    def popitem(self) -> PythonModule:
        return UserDict.popitem(self)[1]

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
        real_size = 0
        theoretical_size = 0
        for module in self.sorted_list_by_name():
            real_size        += module.real_size
            theoretical_size += module.theoretical_size

        return dict(
            real_size = real_size,
            theoretical_size = theoretical_size,
        )
    
    def print_all(self, name, sort_by=SORT_BY.name):
        self.print_modules(name, sort_by=SORT_BY.name)
        self.print_module_count()
        self.print_size()

    def print_modules(self, name, sort_by=SORT_BY.name):
        _print_title(name)
        
        sorted_list = []

        if sort_by == SORT_BY.name:
            sorted_list = self.sorted_list_by_name()
        elif sort_by == SORT_BY.size:
            sorted_list = self.sorted_list_by_size()

        for module in sorted_list:
            print(f"{name}: {module}")
            #print(printable_object.full_name)
            #print(printable_object.path)
            #print(printable_object.__hash__())
            #print(type(printable_object.full_name))
            #print(type(printable_object.path))

    def print_module_count(self):
        module_count = len(self)
        
        print("")
        print("## Module count ##")
        print(module_count)

    def print_size(self):
        size = self.get_size()
        
        print("")
        print("## Total size ##")
        print("Real size: {}".format(format_size(size["real_size"])))
        print("Theoretical size: {}".format(format_size(size["theoretical_size"])))

    def __sub__(self, other):
        result = super().__sub__(other)
        return self.__class__(result)
