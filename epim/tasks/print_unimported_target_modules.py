'''
from epim.tasks.base.local_task import LocalTask
from epim.util.logging import *

class PrintUnimportedTargetModules(LocalTask):

    _previous_task_name = "MapTargetPythonDependencies"
    _visible = True

    def _run_locally(self, session):
        print(f"## Mapping unimported target Python modules... ##")

        unneeded_modules = session.python_modules.get_unimported_modules()
        unneeded_modules.print_all("unneeded_modules")

        print(f"## Mapped unimported target Python modules. ##")
        print()
'''