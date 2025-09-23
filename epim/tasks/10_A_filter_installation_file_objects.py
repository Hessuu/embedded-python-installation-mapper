from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

##############
## TASK 10 A ##
##############
class FilterInstallationFileObjects(LocalTask):

    _previous_task_name = "MapTargetPythonInstallation"
    visible = False

    def _run_locally(self, session):
        print(f"## Filtering out non-installation file objects... ##")

        session.python_packages.remove_packages_not_found_on_target()

        print(f"## Filtered out non-installation file objects. ##")
        print()
