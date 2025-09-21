from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 6 ##
############
class CombineHostAndTargetData(LocalTask):

    _previous_task_name = "MapTargetPythonDependencies"
    visible = False

    def _run_locally(self, session):
        print(f"## Combining target module and Yocto package data... ##")

        session.python_packages.combine_with_python_module_data(session.python_modules)

        print(f"## Combined target module and Yocto package data. ##")
        print()
