from pathlib import Path

import settings
from common.util import progress
from common.util.logging import print
from host.remote_operations import put_file, put_dir, run_command

sync_done = False

app_components = [
    "main.py",
    "settings.py",
    "known_imports.py",
    "common",
    "remote",
]

requirements_dir = "requirements"

def _remove_old(remote_root_path):
    run_command(f"rm -rf {remote_root_path}")

def sync(local_root_path, remote_root_path):
    global sync_done
    if not sync_done:
        print("## SYNCING REMOTE APP... ##")

        # Remove old app
        _remove_old(remote_root_path)

        # Recreate app directory
        print(f"# Removing old remote app from: {remote_root_path}")
        run_command(f"mkdir -p {remote_root_path}")

        # Get all components
        components = []
        for app_component in app_components:
            components.append(local_root_path / app_component)

        requirements_dir_path = local_root_path / requirements_dir
        for requirement_path in requirements_dir_path.iterdir():
            components.append(requirement_path)

        # Progress
        component_count = len(components)
        progress.print_percentage(0, component_count)

        # Send components
        for number, component in enumerate(components, start=1):

            if component.is_file():
                put_file(component, remote_root_path)

            elif component.is_dir():
                put_dir(component, remote_root_path)

            else:
                raise Exception(f"Invalid component: {component}")

            progress.print_percentage(number, component_count)

        sync_done = True
        print("## REMOTE APP SYNC DONE. ##")
