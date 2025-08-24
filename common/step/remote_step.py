import pickle
from pathlib import Path

import settings
from common.session import Session
from common.util.class_property import classproperty
from common.util.logging import print

from .local_step import LocalStep

class RemoteStep(LocalStep):
#### PROPERTIES & VARIABLES ####

## PROTECTED ##
    @classproperty
    def _remote_previous_step_session_path(cls) -> Path:
        if cls.previous_step:
            return settings.REMOTE_SESSIONS_DIR / cls.previous_step._own_session_name
        else:
            return None

    @classproperty
    def _remote_own_session_path(cls) -> Path:
        return settings.REMOTE_SESSIONS_DIR / cls._own_session_name

    _session = None

#### METHODS ####

## PUBLIC ##
    def run(self, we_are_remote=False):
        if we_are_remote:
            super().run(we_are_remote)
        else:
            from host import remote_app
            remote_app.sync(settings.LOCAL_ROOT_PATH, settings.REMOTE_ROOT_PATH)

            self.__sync_remote_previous_step_session()
            self.__run_remotely()
            self.__sync_remote_own_session()
            self.__load_own_session() # Load for printing

## PRIVATE ##
    def __run_remotely(self):
        from host.remote_operations import run_command

        run_command(f"cd {settings.REMOTE_ROOT_PATH} && python3 -m main --run-only {self.cli_name} --remote")

    def __sync_remote_previous_step_session(self):
        from host.remote_operations import put_file, run_command
        
        run_command(f"mkdir -p {self._remote_previous_step_session_path.parent}")
        run_command(f"rm -f {self._remote_previous_step_session_path}")

        print(f"Sending local file {self._local_previous_step_session_path} to {self._remote_previous_step_session_path}")
        put_file(self._local_previous_step_session_path, self._remote_previous_step_session_path)

    def __sync_remote_own_session(self):
        from host.remote_operations import get_file

        print(f"Getting remote file {self._remote_own_session_path} to {self._local_own_session_path}")
        get_file(self._remote_own_session_path, self._local_own_session_path)
        
    def __load_own_session(self):
        print(f"## Reading own session file {self._local_own_session_path} ##")

        self._load_session(self._local_own_session_path)

        print(f"## Read own session file {self._local_own_session_path} ##")
        print()
