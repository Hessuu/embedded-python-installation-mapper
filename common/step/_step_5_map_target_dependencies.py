import settings

from .remote_step import RemoteStep
from ._step_4_map_target_modules import MapTargetModules

class MapTargetDependencies(RemoteStep):

    previous_step = MapTargetModules

    def _run_locally(self):
        import remote.python_module_mapper

        print(f"## Mapping target Python dependencies... ##")

        python_module_mapper.find_all_available_modules(self._session.target_modules, settings.ENTRY_POINTS_ON_TARGET, settings.ADDITIONAL_PYTHON_SEARCH_PATHS_ON_TARGET)

        self._session.target_modules.print_all("available_modules")

        print(f"## Mapped target Python dependencies. ##")
        print()
