from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

############
## TASK 4 ##
############
# TODO: Remove
class FilterNonTargetPackages(LocalTask):

    _previous_task_name = "CheckTargetFiles"
    visible = False

    def _run_locally(self, session):
        print(f"## Filtering out non-target packages... ##")

        session.python_packages.remove_packages_not_found_on_target()

        print(f"## Filtered out non-target packages. ##")
        print()
