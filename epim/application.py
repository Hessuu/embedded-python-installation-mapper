from enum import Enum
from pathlib import Path

import settings
from epim.util.decorators import classproperty
from epim.util.logging import *

class Location(Enum):    
    # The developer's PC.
    HOST = "HOST"

    # The device to be mapped.
    TARGET = "TARGET"


class Application(object):
    __SESSION_DIR_NAME = "sessions"

    __location = None
    __local_root_path = None
    __remote_root_path = None

    @classproperty
    def location(cls) -> Location:
        return cls.__location

    @classproperty
    def local_root_path(cls) -> Path:
        return cls.__local_root_path

    @classproperty
    def remote_root_path(cls) -> Path:
        return cls.__remote_root_path

    @classproperty
    def local_session_dir_path(cls) -> Path:
        return cls.__local_root_path / cls.__SESSION_DIR_NAME

    @classproperty
    def remote_session_dir_path(cls) -> Path:
        return cls.__remote_root_path / cls.__SESSION_DIR_NAME

    @classmethod
    def initialize(cls, location: Location):
        # Location
        cls.__location = location

        # Root paths
        if location == Location.HOST:
            # Host is aware of itself and remote.
            cls.__local_root_path = settings.LOCAL_ROOT_PATH
            cls.__remote_root_path = settings.REMOTE_ROOT_PATH

            print(f"Creating sessions dir: {cls.local_session_dir_path}")
            cls.local_session_dir_path.mkdir(parents=False, exist_ok=True)

        elif location == Location.TARGET:
            # Target is only aware of itself.
            cls.__local_root_path = settings.REMOTE_ROOT_PATH
            cls.__remote_root_path = None

            # Target session dir can't be created at this point, because it is already needed.

        else:
            raise Exception(f"Invalid location: {location}")

        # TODO: Clear if -f is set

    @classmethod
    def clear_sessions(cls):
        
        print(f"Clearing old sessions from: {cls.local_session_dir_path}")
        
        for item in cls.local_session_dir_path.iterdir():
            if item.is_file():
                item.unlink()
            else:
                raise Exception(f"Non-file in sessions dir: {item}")
