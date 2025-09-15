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
visible_tasks = tasks.get_visible()

# Parse arguments
parser = argparse.ArgumentParser()

parser.add_argument("task", choices=visible_tasks)
parser.add_argument("-f", "--force-rerun-dependencies", action="store_true")
parser.add_argument("--remote", action="store_true", help=argparse.SUPPRESS)

args = parser.parse_args()

# Set application metadata
if args.remote:
    Application.initialize(Location.TARGET)

    set_tag_and_color_print_func("REM", ColorString.yellow)
else:
    Application.initialize(Location.HOST)

    set_tag_and_color_print_func("LOC", ColorString.green)

print(args)

# Create and run task queue
task_queue = TaskQueue()
if args.remote:
    # On remote, only run a single task.
    task_queue.populate(visible_tasks[args.task], add_dependencies=False)

else:
    # On host, run all dependencies for the task..
    task_queue.populate(visible_tasks[args.task], add_dependencies=True)

task_queue.run()
