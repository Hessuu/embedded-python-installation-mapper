import pickle
from pathlib import Path

import settings
from common.session import Session
from common.util.class_property import classproperty

from .local_step import LocalStep

class RemoteStep(LocalStep):
#### PROPERTIES & VARIABLES ####

## PROTECTED ##
    @classproperty
    def _remote_session_in_path(cls) -> Path:
        if cls.previous_step:
            return settings.REMOTE_SESSIONS_DIR / cls.previous_step._session_out_name
        else:
            return None

    @classproperty
    def _remote_session_out_path(cls) -> Path:
        return settings.REMOTE_SESSIONS_DIR / cls._session_out_name

    _session = None

#### METHODS ####

## PUBLIC ##
    def run(self, we_are_remote=False):
        if we_are_remote:
            super().run(we_are_remote)
        else:
            from host import remote_app
            remote_app.sync(settings.LOCAL_ROOT_PATH, settings.REMOTE_ROOT_PATH)

            self.__sync_remote_session_input()
            self.__run_remotely()
            self.__sync_remote_session_output()

## PRIVATE ##
    def __run_remotely(self):
        from host.remote_operations import run_command

        run_command(f"cd {settings.REMOTE_ROOT_PATH} && python3 -m main --run-only {self.cli_name} --remote")

    def __sync_remote_session_input(self):
        from host.remote_operations import put_file, run_command
        
        run_command(f"mkdir -p {self._remote_session_in_path.parent}")
        run_command(f"rm -f {self._remote_session_in_path}")

        put_file(self._local_session_in_path, self._remote_session_in_path)

    def __sync_remote_session_output(self):
        from host.remote_operations import get_file

        get_file(self._remote_session_out_path, self._local_session_out_path)
