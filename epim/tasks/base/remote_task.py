import pickle
from pathlib import Path

import settings
from epim.application import *
from epim.host.remote_app import *
from epim.session import Session
from epim.util.decorators import *
from epim.util.logging import print

from .local_task import LocalTask

class RemoteTask(LocalTask):
#### METHODS ####

## PUBLIC ##
    @host_and_target
    def run(self):

        if Application.location == Location.TARGET:

            # If on target, we can run the task locally.
            super().run()

        elif Application.location == Location.HOST:

            # Ensure our app is present on target.
            from epim.host.remote_app import RemoteOperation
            RemoteApp.sync(settings.LOCAL_ROOT_PATH, settings.REMOTE_ROOT_PATH)

            self.__sync_session_to_remote()
            self.__run_remotely()
            self.__sync_session_from_remote()

        else:
            assert False

## PRIVATE ##
    @host_only
    def __run_remotely(self):
        from host.remote_operation import RemoteOperation

        RemoteOperation.command(f"cd {settings.REMOTE_ROOT_PATH} && python3 -m main {self.cli_name} --remote")

    @host_only
    def __sync_session_to_remote(self):
        self._load_session()
        self._session.write_to_remote(self.previous_task.name)

    @host_only
    def __sync_session_from_remote(self):
        self._session = Session.load_from_remote(self.name)
