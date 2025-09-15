from enum import Enum
from pathlib import Path

import settings
from epim.util.decorators import classproperty

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

        elif location == Location.TARGET:
            # Target is only aware of itself.
            cls.__local_root_path = settings.REMOTE_ROOT_PATH
            cls.__remote_root_path = None

        else:
            raise Exception(f"Invalid location: {location}")

        # Create local session dir.
        # We expect the root path to exist.
        cls.local_session_dir_path.mkdir(parents=False, exist_ok=True)
        
        # TODO: Clear if -f is set
        # Always clear session dir on target.
        if location == Location.TARGET:
            cls.clear_sessions()

    @classmethod
    def clear_sessions(cls):
        
        print(f"Clearing old sessions from: {cls.local_session_dir_path}")
        
        for item in cls.local_session_dir_path.iterdir():
            if item.is_file():
                item.unlink()
            else:
                raise Exception(f"Non-file in sessions dir: {item}")
