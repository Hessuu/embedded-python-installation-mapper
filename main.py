import sys, os

import argparse
import importlib
import pkgutil
from pathlib import Path
from queue import LifoQueue

import epim.tasks as tasks
from epim.application import *
from epim.util.color_string import *
from epim.util.logging import * 
from epim.session import Session
from epim.task_queue import *
from epim.tasks import *

# Get tasks that can be shown to the user
all_tasks = tasks.get_all()
visible_tasks = tasks.get_visible()

# Parse arguments
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)

# User-facing tasks
group.add_argument("-t", "--task", choices=visible_tasks)

# All tasks
group.add_argument("--remote-task", choices=all_tasks,  help=argparse.SUPPRESS)

parser.add_argument("-f", "--force-rerun-dependencies", action="store_true")



args = parser.parse_args()

# Set application metadata
if args.remote_task:
    set_tag_and_color_print_func("REM", ColorString.yellow)

    Application.initialize(Location.TARGET)
else:
    set_tag_and_color_print_func("LOC", ColorString.green)

    Application.initialize(Location.HOST)

print(args)

# Create and run task queue
task_queue = TaskQueue()
if args.remote_task:
    # On remote, only run a single task.
    target_task = all_tasks[args.remote_task]
    task_queue.populate(target_task, add_dependencies=False)

else:
    # On host, run all dependencies for the task..
    target_task = visible_tasks[args.task]
    task_queue.populate(target_task, add_dependencies=True)

task_queue.run(target_task)
