import settings

from common.util.logging import print

from common.task.base.local_task import LocalTask
from common.task.mapper.map_target_dependencies import MapTargetDependencies

class PrintUnimportedTargetModules(LocalTask):

    previous_task = MapTargetDependencies

    def _run_locally(self):
        print(f"## Mapping unimported target Python modules... ##")

        unneeded_modules = self._session.target_modules.get_unimported_modules()
        unneeded_modules.print_all("unneeded_modules")

        print(f"## Mapped unimported target Python modules. ##")
        print()
