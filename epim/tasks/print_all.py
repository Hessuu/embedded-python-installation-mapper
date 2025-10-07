from epim.tasks.print_python_installation_report import *

class PrintAll(PrintPythonInstallationReport):

    _previous_task_name = "PrintPythonPackageReport"
    _visible = True
    _never_skip = True

    def _run_locally(self, session):
        super()._run_locally(session)
