import settings

from common.util.logging import print

from .remote_step import RemoteStep
from ._step_2_add_target_yocto_packages import AddTargetYoctoPackages

class CheckTargetFiles(RemoteStep):

    previous_step = AddTargetYoctoPackages

    def _run_locally(self):
        #import yocto_packages

        print(f"## Checking Python files on target... ##")

        self._session.yocto_packages.check_files_on_target()

        print(f"## Checked Python files on target. ##")
        print()

    def print_result(self):
        print(self._session.yocto_packages)
