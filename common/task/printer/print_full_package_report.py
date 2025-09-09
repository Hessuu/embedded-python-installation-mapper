import settings

from common.util.logging import print

from common.task.base.local_task import *
from common.task.mapper.combine_target_and_local_data import *
from common.util.file_object_size import *

class PrintFullPackageReport(LocalTask):

    previous_task = CombineTargetAndLocalData

    def _run_locally(self):
        print(f"## Printing Yocto package report... ##")

        print(self._session.packages.get_string())

        print(f"## Printed Yocto package report. ##")
        print()
