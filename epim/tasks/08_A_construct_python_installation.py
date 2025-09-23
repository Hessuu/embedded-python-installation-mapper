from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

##############
## TASK 8 A ##
##############
class ConstructPythonInstallation(LocalTask):

    _previous_task_name = "FilterNonTargetPackages"
    visible = False

    def _run_locally(self, session):
        print(f"## Constructing Python installation... ##")

        for package in session.python_packages.values():
            package.add_file_objects_to_python_installation(session.python_installation)

        print(f"## Constructed Python installation. ##")
        print()
