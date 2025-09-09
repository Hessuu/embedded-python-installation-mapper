
from common.package_collection import *
from common.python_module_collection import *

class Session(object):
    def __init__(self):
        self.packages = PackageCollection()
        self.python_modules = PythonModuleCollection()
