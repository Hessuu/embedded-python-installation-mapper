from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 5 ##
############
class ConstructPythonInstallation(LocalTask):

    _previous_task_name = "CheckTargetFiles"
    _visible = False

    def _run_locally(self, session):
        print(f"## Constructing Python installation... ##")
        
        session.python_installation.populate(session.all_python_packages)

        print(f"## Constructed Python installation. ##")
        print()
