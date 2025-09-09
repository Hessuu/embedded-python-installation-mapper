import settings

from common.util.logging import print

from common.task.base.local_task import LocalTask
from common.task.mapper.map_target_dependencies import MapTargetDependencies

############
## TASK 6 ##
############
class CombineTargetAndLocalData(LocalTask):

    previous_task = MapTargetDependencies

    def _run_locally(self):
        print(f"## Combining target module and Yocto package data... ##")

        self._session.packages.combine_with_python_module_data(self._session.python_modules)

        print(f"## Combined target module and Yocto package data. ##")
        print()
