import sys, os

import argparse
import importlib
import pkgutil
from pathlib import Path
from queue import LifoQueue

from common.util import color_string
from common.util.logging import print, set_tag_and_color_print_func
from common.step import steps
from common.step.local_step import LocalStep
from common.session import Session

step_choices = steps.all
step_choices_with_all = step_choices.copy()
step_choices_with_all["all"] = "all"

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-r", "--run", choices=step_choices_with_all.keys())
group.add_argument("-o", "--run-only", choices=step_choices.keys())

parser.add_argument("-f", "--force-rerun-dependencies")
parser.add_argument("--remote", action='store_true', help=argparse.SUPPRESS)


args = parser.parse_args()

if args.remote:
    set_tag_and_color_print_func("REM", color_string.yellow)
else:
    set_tag_and_color_print_func("LOC", color_string.green)

print(args)

step_queue = LifoQueue()

# Construct a step queue based on arguments
if args.run:
    if args.run == "all":
        pass
    else:
        target_step = step_choices[args.run]
        step_queue = steps.populate_step_queue_for_target_step(step_queue, target_step)

elif args.run_only:
    target_step = step_choices[args.run_only]
    step_queue.put(target_step)

else:
    raise Exception("bad args")

# Run step queue
current_step = None
final_step_inst = None
while not step_queue.empty():
    current_step = step_queue.get()
    current_step_inst = current_step()

    print(f"#### Next step: {current_step_inst.cli_name} ####")

    current_step_inst.run(args.remote)

    print(f"#### Step Done: {current_step_inst.cli_name} ####")
    print()
    
    final_step_inst = current_step_inst

if not args.remote:
    final_step_inst.print_result()
