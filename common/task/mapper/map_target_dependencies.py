import settings

from common.util.logging import print

from common.task.base.remote_task import RemoteTask
from common.task.mapper.map_target_python_modules import MapTargetPythonModules

############
## TASK 5 ##
############
class MapTargetDependencies(RemoteTask):

    previous_task = MapTargetPythonModules
    
    def _run_locally(self):
        from remote import python_module_mapper

        print(f"## Mapping target Python dependencies... ##")

        python_module_mapper.find_all_dependencies(
            self._session.python_modules,
            settings.ENTRY_POINTS_ON_TARGET,
            settings.REMOTE_ROOT_PATH
            )

        print(f"## Mapped target Python dependencies. ##")
        print()

    def print_result(self):
        required_modules = self._session.python_modules.get_imported_modules()
        required_modules.print_all("required_modules")

        unneeded_modules = self._session.python_modules.get_unimported_modules()
        unneeded_modules.print_all("unneeded_modules")
