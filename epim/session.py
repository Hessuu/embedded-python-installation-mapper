from pickle import Pickler, Unpickler

import settings
from epim.application import *
from epim.util.logging import *
from epim.package_collection import *
from epim.python_module_collection import *
from epim.util.decorators import *




class Session(object):
    __SESSION_FILE_SUFFIX = ".session"

    def __init__(self):
        self.python_packages = PackageCollection()
        self.python_modules = PythonModuleCollection()
        self.all_file_objects = {}


## PUBLIC ##  

    @classmethod
    def exists(cls, name):
        local_path = cls.__get_local_path(name)
        return local_path.exists()
        
    @classmethod
    @host_and_target
    def load_from_disk(cls, name):
        local_session_path =  cls.__get_local_path(name)

        if not local_session_path.exists():
            raise Exception(f"Missing session file: {local_session_path}")

        print(f"## Loading session file {local_session_path} ##")

        with open(local_session_path, "rb") as session_file:
            return Unpickler(session_file).load()

    @classmethod
    @host_only
    def load_from_remote(cls, name):
        from epim.host.remote_operation import RemoteOperation
        
        local_session_path = cls.__get_local_path(name)
        remote_session_path = cls.__get_remote_path(name)

        print(f"Getting remote file {remote_session_path} to {local_session_path}")
        RemoteOperation.get_file(remote_session_path, local_session_path)
        
        return cls.load_from_disk(name)

    @host_and_target
    def write_to_disk(self, name):
        local_session_path = self.__get_local_path(name)

        print(f"## Writing session file {local_session_path} ##")

        if local_session_path.exists():
            local_session_path.unlink()

        with open(local_session_path, "wb") as session_file:
            Pickler(session_file).dump(self)

        print(f"## Wrote session file {local_session_path} ##")
        print()
    
    @host_only
    def write_to_remote(self, name):
        self.write_to_disk(name)

        local_session_path = self.__get_local_path(name)
        remote_session_path = self.__get_remote_path(name)

        from epim.host.remote_operation import RemoteOperation

        print(f"Sending local file {local_session_path} to {remote_session_path}")
        RemoteOperation.put_file(local_session_path, remote_session_path)

## PRIVATE ##
    @classmethod
    def __get_local_path(self, name):
        return Application.local_session_dir_path / (name + self.__SESSION_FILE_SUFFIX)

    @classmethod
    def __get_remote_path(self, name):
        return Application.remote_session_dir_path / (name + self.__SESSION_FILE_SUFFIX)
