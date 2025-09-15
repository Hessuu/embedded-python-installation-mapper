from epim.tasks.base.remote_task import RemoteTask
from epim.util.logging import *

############
## TASK 3 ##
############
class CheckTargetFiles(RemoteTask):

    _previous_task_name = "AddTargetPackages"
    visible = False

    def _run_locally(self, session):
        print(f"## Checking Python files on target... ##")

        session.python_packages.update_package_statuses_on_target()

        print(f"## Checked Python files on target. ##")
        print()
