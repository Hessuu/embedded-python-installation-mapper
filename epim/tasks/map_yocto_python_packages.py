import settings
from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 1 ##
############
class MapYoctoPythonPackages(LocalTask):

    _previous_task_name = None
    visible = False

    def _run_locally(self, session):
        print(f"## Mapping Yocto Python packages... ##")

        session.python_packages.populate_on_host(settings.YOCTO_TARGET_WORK_DIRS, session.all_file_objects)

        print(f"## Mapped Yocto Python packages. ##")
        print()
