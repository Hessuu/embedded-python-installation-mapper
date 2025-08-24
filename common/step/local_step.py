from pickle import Pickler, Unpickler
from pathlib import Path

import settings
from common.session import Session
from common.util.class_property import classproperty

def _camel_case_to_snake_case(camel_str: str) -> str:
    snake_str = [camel_str[0].lower()]

    for char in camel_str[1:]:
        if char.isupper():
            snake_str.append("_")
            snake_str.append(char.lower())
        else:
            snake_str.append(char.lower())

    return "".join(snake_str)

class LocalStep(object):
############################
## PROPERTIES & VARIABLES ##
############################

## PUBLIC ##
    previous_step = None
    
    @classproperty
    def cli_name(cls) -> str:
        return _camel_case_to_snake_case(cls.__name__)

## PROTECTED ##
    @classproperty
    def _session_out_name(cls) -> str:
        return f"{cls.__name__}.session"

    @classproperty
    def _local_session_in_path(cls) -> Path:
        if cls.previous_step:
            return settings.LOCAL_SESSIONS_DIR / cls.previous_step._session_out_name
        else:
            return None

    @classproperty
    def _local_session_out_path(cls) -> Path:
        return settings.LOCAL_SESSIONS_DIR / cls._session_out_name

    _session = None

#############
## METHODS ##
#############

## PUBLIC ##
    def run(self, we_are_remote=False):
        if self.previous_step:
            self.__load_session_in()
        self._run_locally()
        self.__write_session_out()

    def print_result(self):
        print(f"Nothing to print for task: {self.cli_name}")

## PROTECTED ##
    def _run_locally(self):
        pass

## PRIVATE ##
    def __load_session_in(self):
        print(f"## Reading session file {self._local_session_in_path} ##")

        if not self._local_session_in_path.exists():
            raise Exception(f"Input session file missing for {__name__} step: {self._local_session_in_path}")

        with open(self._local_session_in_path, "rb") as session_in_file:
            self._session = Unpickler(session_in_file).load()

        #    session_in_data = session_in_file.read()
        #    self._session = pickle.loads(session_in_data)

        print(f"## Read session file {self._local_session_in_path} ##")
        print()

    def __write_session_out(self):
        print(f"## Writing session file {self._local_session_out_path} ##")
        
        if not settings.LOCAL_SESSIONS_DIR.exists():
            settings.LOCAL_SESSIONS_DIR.mkdir()

        self._local_session_out_path.unlink(missing_ok=True)

        #session_out_data = pickle.dumps(self._session)
        with open(self._local_session_out_path, "wb") as session_out_file:
            Pickler(session_out_file).dump(self._session)
        #    session_out_file.write(session_out_data)


        print(f"## Wrote session file {self._local_session_out_path} ##")
        print()
