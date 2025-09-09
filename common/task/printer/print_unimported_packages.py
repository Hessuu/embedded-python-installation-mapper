import settings

from common.util.logging import print

from common.task.base.local_task import LocalTask
from common.task.mapper.combine_target_and_local_data import CombineTargetAndLocalData

class PrintUnimportedPackages(LocalTask):

    previous_task = CombineTargetAndLocalData

    def _run_locally(self):
        from common.package import PackageStatus
        
        print(f"## Printing unimported packages... ##")
        
        for package in self._session.packages.values():
            package.update_status()
            if package.status == PackageStatus.FULLY_NOT_REQUIRED:
                print(package)

        print(f"## Printed unimported packages. ##")
        print()
