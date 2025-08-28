import settings

from common.util.logging import print

from common.task.base.local_task import LocalTask
from common.task.mapper.combine_target_and_local_data import CombineTargetAndLocalData

class PrintFullYoctoPackageReport(LocalTask):

    previous_task = CombineTargetAndLocalData

    def _run_locally(self):
        print(f"## Printing Yocto package report... ##")

        print(self._session.yocto_packages)

        print(f"## Printed Yocto package report. ##")
        print()
