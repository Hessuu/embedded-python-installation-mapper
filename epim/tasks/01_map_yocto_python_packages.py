import settings
from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 1 ##
############
class MapYoctoPythonPackages(LocalTask):

    _previous_task_name = None
    _visible = False

    def _run_locally(self, session):
        print(f"## Mapping Yocto Python packages... ##")

        session.all_python_packages.populate_on_host(settings.YOCTO_TARGET_WORK_DIRS)

        print(f"## Mapped Yocto Python packages. ##")
        print()
