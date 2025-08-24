import settings
from common.session import Session

from .local_step import LocalStep

import common.session
print(f"Creator session: {common.session.__file__}")

class MapYoctoPackages(LocalStep):

    previous_step = None

    def _run_locally(self):
        print(f"## Mapping Yocto Python packages... ##")

        self._session = Session()
        self._session.yocto_packages.populate(settings.YOCTO_TARGET_WORK_DIRS)

        print(f"## Mapped Yocto Python packages. ##")
        print()

    def print_result(self):
        print(self._session.yocto_packages)
