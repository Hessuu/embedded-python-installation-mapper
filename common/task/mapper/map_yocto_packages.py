import settings
from common.session import Session
from common.util.logging import print

from common.task.base.local_task import LocalTask

############
## TASK 1 ##
############
class MapYoctoPackages(LocalTask):

    previous_task = None

    def _run_locally(self):
        print(f"## Mapping Yocto Python packages... ##")

        self._session = Session()
        self._session.yocto_packages.populate(settings.YOCTO_TARGET_WORK_DIRS)

        print(f"## Mapped Yocto Python packages. ##")
        print()

    def print_result(self):
        print(self._session.yocto_packages)
