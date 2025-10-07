from epim.python_installation_report import *
from epim.tasks.base.local_task import LocalTask
from epim.util.file_object_size import *
from epim.util.logging import *

class PrintPythonInstallationReport(LocalTask):

    _previous_task_name = "CombineHostAndTargetData"
    _visible = True
    _never_skip = True

    def _run_locally(self, session):
        print(f"## Printing Python installation report... ##")
        print()

        report = PythonInstallationReport()

        # Print all files
        all_files_string = f"## FILES IN INSTALLATION ##\n"
        for file_object_path, file_object in sorted(session.python_installation.file_objects.items()):
            
            # Don't print or consider ignored files
            if file_object_path in settings.PYTHON_INSTALLATION_MANIFEST_FILE_OBJECTS_TO_IGNORE:
                continue
            
            report.add_file_object_data(file_object)
            all_files_string += file_object.get_string(file_object_size_type=FileObjectSizeType.REAL_SIZE) + "\n"
        
        print(all_files_string)
        print()

        report.print_report()

        print(f"#########################################")
        print(f"## Printed Python installation report. ##")
