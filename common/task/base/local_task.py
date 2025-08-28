from pickle import Pickler, Unpickler
from pathlib import Path

import settings
from common.session import Session
from common.util.class_property import classproperty
from common.util.logging import print

def _camel_case_to_snake_case(camel_str: str) -> str:
    snake_str = [camel_str[0].lower()]

    for char in camel_str[1:]:
        if char.isupper():
            snake_str.append("_")
            snake_str.append(char.lower())
        else:
            snake_str.append(char.lower())

    return "".join(snake_str)

class LocalTask(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##
    previous_task = None
    
    @classproperty
    def cli_name(cls) -> str:
        return _camel_case_to_snake_case(cls.__name__)

## PROTECTED ##
    @classproperty
    def _own_session_name(cls) -> str:
        return f"{cls.__name__}.session"

    @classproperty
    def _local_previous_task_session_path(cls) -> Path:
        if cls.previous_task:
            return settings.LOCAL_SESSIONS_DIR / cls.previous_task._own_session_name
        else:
            return None

    @classproperty
    def _local_own_session_path(cls) -> Path:
        return settings.LOCAL_SESSIONS_DIR / cls._own_session_name

    _session = None

#############
## METHODS ##
#############

## PUBLIC ##
    def run(self, we_are_remote=False):
        if self.previous_task:
            self.__load_previous_task_session()
        self._run_locally()
        self.__write_own_session()

    def print_result(self):
        print(f"Nothing to print for task: {self.cli_name}")

## PROTECTED ##
    def _run_locally(self):
        pass
    
    def _load_session(self, session_path: Path):
        if not session_path.exists():
            raise Exception(f"Session file missing for {__name__} task: {session_path}")

        with open(session_path, "rb") as session_file:
            self._session = Unpickler(session_file).load()

## PRIVATE ##
    def __load_previous_task_session(self):
        print(f"## Reading session file {self._local_previous_task_session_path} ##")

        self._load_session(self._local_previous_task_session_path)

        print(f"## Read session file {self._local_previous_task_session_path} ##")
        print()

    def __write_own_session(self):
        print(f"## Writing session file {self._local_own_session_path} ##")
        
        if not settings.LOCAL_SESSIONS_DIR.exists():
            settings.LOCAL_SESSIONS_DIR.mkdir()

        self._local_own_session_path.unlink(missing_ok=True)

        #session_out_data = pickle.dumps(self._session)
        with open(self._local_own_session_path, "wb") as session_out_file:
            Pickler(session_out_file).dump(self._session)
        #    session_out_file.write(session_out_data)


        print(f"## Wrote session file {self._local_own_session_path} ##")
        print()
