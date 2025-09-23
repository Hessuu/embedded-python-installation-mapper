import sysconfig

from epim.file_object import *
from epim.tasks.base.remote_task import *
from epim.util.logging import *

##############
## TASK 9 A ##
##############
class MapTargetPythonInstallation(RemoteTask):

    _previous_task_name = "ConstructPythonInstallation"
    visible = False

    def _run_locally(self, session):
        print(f"## Mapping target Python installation... ##")

        # Add file objects from target that were not already part of Yocto packages.
        for additional_directory_path in settings.PYTHON_INSTALLATION_MANIFEST_ADDITIONAL_DIRECTORIES_ON_TARGET:

            if not additional_directory_path.is_dir():
                raise Exception(f"Additional directory is not a directory: {additional_directory_path}")

            for file_object_path in additional_directory_path.rglob("*"):
                if not file_object_path in session.python_installation:

                    file_object = FileObject(file_object_path, None)
                    file_object.update_real_size_on_target()

                    session.python_installation_from_target[file_object_path] = file_object

        print(f"## Mapped target Python installation. ##")
        print()
