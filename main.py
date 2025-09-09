import sys, os

import argparse
import importlib
import pkgutil
from pathlib import Path
from queue import LifoQueue

from common import task
from common.util.color_string import ColorString
from common.util.location import *
from common.util.logging import print, set_tag_and_color_print_func
from common.task.base.local_task import LocalTask
from common.session import Session

task_choices = task.get_all()
task_choices_with_all = task_choices.copy()
task_choices_with_all["all"] = "all"

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-r", "--run", choices=task_choices_with_all.keys())
group.add_argument("-o", "--run-only", choices=task_choices.keys())

parser.add_argument("-f", "--force-rerun-dependencies")
parser.add_argument("--remote", action='store_true', help=argparse.SUPPRESS)


args = parser.parse_args()

if args.remote:
    Location.current = Location.TARGET
    set_tag_and_color_print_func("REM", ColorString.yellow)
else:
    Location.current = Location.HOST
    set_tag_and_color_print_func("LOC", ColorString.green)

print(args)

task_queue = LifoQueue()

# Construct a task queue based on arguments
if args.run:
    if args.run == "all":
        pass
    else:
        target_task = task_choices[args.run]
        task_queue = task.populate_task_queue_for_target_task(task_queue, target_task)

elif args.run_only:
    target_task = task_choices[args.run_only]
    task_queue.put(target_task)

else:
    raise Exception("bad args")

# Run task queue
current_task = None
final_task_inst = None
while not task_queue.empty():
    current_task = task_queue.get()
    current_task_inst = current_task()

    print(f"#### Next task: {current_task_inst.cli_name} ####")

    current_task_inst.run(args.remote)

    print(f"#### Task Done: {current_task_inst.cli_name} ####")
    print()
    
    final_task_inst = current_task_inst

if not args.remote:
    final_task_inst.print_result()
