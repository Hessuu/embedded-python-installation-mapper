import settings

from common.util.logging import print

from common.task.base.remote_task import RemoteTask
from common.task.mapper.add_target_packages import AddTargetPackages

############
## TASK 3 ##
############
class CheckTargetFiles(RemoteTask):

    previous_task = AddTargetPackages

    def _run_locally(self):
        #import packages

        print(f"## Checking Python files on target... ##")

        self._session.packages.update_package_statuses_on_target()

        print(f"## Checked Python files on target. ##")
        print()

    def print_result(self):
        print(self._session.packages)
