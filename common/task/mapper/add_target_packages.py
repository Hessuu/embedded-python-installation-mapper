import settings

from common.session import Session
from common.util.logging import print

from common.task.base.remote_task import RemoteTask
from common.task.mapper.map_yocto_packages import MapYoctoPackages

############
## TASK 2 ##
############
class AddTargetPackages(RemoteTask):

    previous_task = MapYoctoPackages

    def _run_locally(self):
        #import packages

        print(f"## Adding packages from target... ##")

        self._session.packages.add_packages_on_target(settings.PACKAGE_DIRS_ON_TARGET)

        print(f"## Added packages from target. ##")
        print()

    def print_result(self):
        print(self._session.packages)
