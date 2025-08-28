import settings

from common.util.logging import print

from common.task.base.local_task import LocalTask
from common.task.mapper.combine_target_and_local_data import CombineTargetAndLocalData

class PrintUnimportedYoctoPackages(LocalTask):

    previous_task = CombineTargetAndLocalData

    def _run_locally(self):
        from common.yocto_package import PackageStatus
        
        print(f"## Printing unimported Yocto packages... ##")
        
        for yocto_package in self._session.yocto_packages.values():
            yocto_package.update_own_status()
            if yocto_package.status == PackageStatus.FULLY_NOT_REQUIRED:
                print(yocto_package)

        print(f"## Printed unimported Yocto packages. ##")
        print()
