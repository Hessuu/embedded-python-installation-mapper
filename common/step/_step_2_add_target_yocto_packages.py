import settings

from common.session import Session

from .remote_step import RemoteStep
from ._step_1_map_yocto_packages import MapYoctoPackages

import common.session
print(f"User session: {common.session.__file__}")


class AddTargetYoctoPackages(RemoteStep):

    previous_step = MapYoctoPackages

    def _run_locally(self):
        #import yocto_packages

        print(f"## Adding Yocto packages from target... ##")

        self._session.yocto_packages.add_packages_on_target(settings.PACKAGE_DIRS_ON_TARGET)

        print(f"## Added Yocto packages from target. ##")
        print()

    def print_result(self):
        print(self._session.yocto_packages)
