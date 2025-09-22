import settings
from epim.tasks.base.remote_task import RemoteTask
from epim.util.logging import *

############
## TASK 4 ##
############
class MapTargetPythonModules(RemoteTask):

    _previous_task_name = "CheckTargetFiles"
    visible = False

    def _run_locally(self, session):
        from epim.remote import python_module_mapper 

        print(f"## Mapping target Python modules... ##")

        python_module_mapper.find_all_available_modules(
            session.python_modules,
            settings.ENTRY_POINT_PATHS_ON_TARGET,
            settings.ADDITIONAL_PYTHON_SEARCH_PATHS_ON_TARGET,
            settings.REMOTE_ROOT_PATH
            )

        print(f"## Mapped target Python modules. ##")
        print()
