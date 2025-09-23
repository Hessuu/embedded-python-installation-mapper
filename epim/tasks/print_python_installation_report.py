from epim.python_installation_report import *
from epim.tasks.base.local_task import LocalTask
from epim.util.file_object_size import *
from epim.util.logging import *


class PrintPythonInstallationReport(LocalTask):

    _previous_task_name = "MapTargetPythonInstallation"
    visible = True

    def _run_locally(self, session):
        print(f"## Printing Python installation report... ##")
        print()
        
        report = PythonInstallationReport()
        
        # Print all files
        print(f"## FILES FROM PACKAGES ##")
        for _, file_object in sorted(session.python_installation.items()):
            report.add_file_object_data(file_object)
            print(file_object.get_string(file_object_size_type=FileObjectSizeType.REAL_SIZE))
        print()
        
        print(f"## ADDITIONAL FILES FROM TARGET ##")
        for _, file_object in sorted(session.python_installation_from_target.items()):
            report.add_file_object_data(file_object)
            print(file_object.get_string(file_object_size_type=FileObjectSizeType.REAL_SIZE))
        print()
        
        report.print_report()
        
        print(f"#########################################")
        print(f"## Printed Python installation report. ##")

        