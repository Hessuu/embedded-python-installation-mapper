import settings

from common.util.logging import print

from .local_step import LocalStep
from ._step_5_map_target_dependencies import MapTargetDependencies

class MapUnimportedTargetModules(LocalStep):

    previous_step = MapTargetDependencies

    def _run_locally(self):
        print(f"## Mapping unimported target Python modules... ##")

        unneeded_modules = self._session.target_modules.get_unimported_modules()
        unneeded_modules.print_all("unneeded_modules")

        print(f"## Mapped unimported target Python modules. ##")
        print()
