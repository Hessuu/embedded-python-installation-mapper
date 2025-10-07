from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 9 ##
############
class CombineHostAndTargetData(LocalTask):

    _previous_task_name = "MapTargetPythonDependencies"
    _visible = False

    def _run_locally(self, session):
        print(f"## Combining target module and Yocto package data... ##")
        
        session.python_installation.link_python_modules_to_file_objects()

        print(f"## Combined target module and Yocto package data. ##")
        print()
