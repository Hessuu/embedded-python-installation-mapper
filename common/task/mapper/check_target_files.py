import settings

from common.util.logging import print

from common.task.base.remote_task import RemoteTask
from common.task.mapper.add_target_yocto_packages import AddTargetYoctoPackages

############
## TASK 3 ##
############
class CheckTargetFiles(RemoteTask):

    previous_task = AddTargetYoctoPackages

    def _run_locally(self):
        #import yocto_packages

        print(f"## Checking Python files on target... ##")

        self._session.yocto_packages.check_files_on_target()

        print(f"## Checked Python files on target. ##")
        print()

    def print_result(self):
        print(self._session.yocto_packages)
