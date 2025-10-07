from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

class PrintPythonPackageReport(LocalTask):

    _previous_task_name = "CombineHostAndTargetData"
    _visible = True
    _never_skip = True

    def _run_locally(self, session):
        print(f"## Printing Yocto package report... ##")

        print(session.python_installation.python_packages.get_string())

        print(f"## Printed Yocto package report. ##")
        print()
