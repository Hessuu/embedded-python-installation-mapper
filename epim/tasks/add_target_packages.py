import settings
from epim.tasks.base.remote_task import RemoteTask
from epim.util.logging import *

############
## TASK 2 ##
############
class AddTargetPackages(RemoteTask):

    _previous_task_name = "MapYoctoPythonPackages"
    visible = False

    def _run_locally(self, session):
        print(f"## Adding packages from target... ##")

        session.python_packages.add_packages_on_target(settings.PACKAGE_DIRS_ON_TARGET)

        print(f"## Added packages from target. ##")
        print()
