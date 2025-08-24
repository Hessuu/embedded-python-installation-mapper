import settings

from .remote_step import RemoteStep
from ._step_3_check_target_files import CheckTargetFiles

class MapTargetModules(RemoteStep):

    previous_step = CheckTargetFiles

    def _run_locally(self):
        import remote.python_module_mapper 

        print(f"## Mapping target Python modules... ##")

        search_paths = settings.PYTHON_SEARCH_PATHS_ON_TARGET

        # Add system paths for broader search, but prioritize custom paths.
        search_paths.extend(sys.path)

        # Remove our own directory from paths to prevent the scanner from being included.
        own_dir_path = Path(__file__).parent.resolve()
        own_dir_path_str = str(own_dir_path)
        search_paths.remove(own_dir_path_str)

        print(f"Python search paths: {search_paths}")

        python_module_mapper.find_all_available_modules(self._session.target_modules, APP_ENTRY_POINTS, search_paths)

        self._session.target_modules.print_all("available_modules")

        print(f"## Mapped target Python modules. ##")
        print()
