'''
from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

class PrintUnimportedPackages(LocalTask):

    _previous_task_name = "CombineHostAndTargetData"
    _visible = True

    def _run_locally(self, session):
        from common.package import PackageStatus
        
        print(f"## Printing unimported packages... ##")
        
        for package in session.python_packages.values():
            package.update_status()
            if package.status == PackageStatus.FULLY_NOT_REQUIRED:
                print(package)

        print(f"## Printed unimported packages. ##")
        print()
'''