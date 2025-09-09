import sys
from pathlib import Path

import settings
from common.util.logging import print

from common.task.base.remote_task import RemoteTask
from common.task.mapper.check_target_files import CheckTargetFiles

############
## TASK 4 ##
############
class MapTargetPythonModules(RemoteTask):

    previous_task = CheckTargetFiles

    def _run_locally(self):
        from remote import python_module_mapper 

        print(f"## Mapping target Python modules... ##")

        python_module_mapper.find_all_available_modules(
            self._session.python_modules,
            settings.ENTRY_POINTS_ON_TARGET,
            settings.ADDITIONAL_PYTHON_SEARCH_PATHS_ON_TARGET,
            settings.REMOTE_ROOT_PATH
            )

        print(f"## Mapped target Python modules. ##")
        print()

    def print_result(self):
        self._session.python_modules.print_all("available_modules")
