from queue import LifoQueue

import epim.tasks as tasks
import settings
from epim.session import *
from epim.tasks import *


class TaskQueue(LifoQueue):
    def populate(self, target_task, add_dependencies: bool=True):

        current_task = target_task        
        if add_dependencies:
            while current_task:
                self.put(current_task)

                current_task = current_task.previous_task
        else:
            self.put(current_task)


    def run(self, target_task, force_rerun_dependencies: bool):

        # We accomplish this by removing all sessions
        if force_rerun_dependencies:
            Application.clear_sessions()

        current_task = None
        while not self.empty():
            current_task = self.get()

            # Current task should not be skipped.
            if current_task != target_task or not current_task.never_skip:
                if Session.exists(current_task.name):
                    print(f"#### Skipping already done task: {current_task.cli_name} ####")
                    print()
                    continue


            current_task_instance = current_task()

            print(f"#### Next task: {current_task.cli_name} ####")

            current_task_instance.run()

            print(f"#### Task Done: {current_task.cli_name} ####")
            print()


'''
def run(workflow_key: str):

    previous_session_path = None
    for current_task in workflows.all[workflow_key]:

        # TODO: Implement force run
        # If this task has already been run, skip it.
        session = None
        if session.exists():
            previous_session_path = current_session_path

            print(f"#### Skipping already done task: {current_task.cli_name} ####")
            print()

            continue

        print(f"#### Next task: {current_task.cli_name} ####")

        previous_session_path = current_task.run(previous_session_path, we_are_remote=False)

        print(f"#### Task Done: {current_task.cli_name} ####")
        print()
'''