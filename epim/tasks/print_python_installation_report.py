from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

class PrintPythonInstallationReport(LocalTask):

    _previous_task_name = "FilterNonTargetPackages"
    visible = True

    def _run_locally(self, session):
        print(f"## Printing Python installation size... ##")

        print(session.python_packages.get_string())

        print(f"## Printed Python installation size. ##")
        print()
