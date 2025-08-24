
from common.yocto_python_package_collection import YoctoPythonPackageCollection
from common.python_module_collection import PythonModuleCollection

class Session(object):
    def __init__(self):
        self.yocto_packages = YoctoPythonPackageCollection()
        self.target_modules = PythonModuleCollection()
