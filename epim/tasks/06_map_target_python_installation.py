import sysconfig

from epim.file_object import *
from epim.tasks.base.remote_task import *
from epim.util.logging import *

############
## TASK 6 ##
############
class MapTargetPythonInstallation(RemoteTask):

    _previous_task_name = "ConstructPythonInstallation"
    _visible = False

    def _run_locally(self, session):
        print(f"## Mapping target Python installation... ##")

        session.python_installation.add_additional_file_objects_on_target(
            settings.PYTHON_INSTALLATION_MANIFEST_ADDITIONAL_DIRECTORIES_ON_TARGET
        )
        
        session.python_installation.update_file_object_data_on_target()

        print(f"## Mapped target Python installation. ##")
        print()
