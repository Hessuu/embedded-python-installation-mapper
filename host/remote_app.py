
from  common.util import progress
import settings
from host.remote_operations import put_file, put_dir, run_command

sync_done = False

app_components = [
    "main.py",
    "settings.py",
    "common",
]

def _remove_old(remote_root_path):
    run_command(f"rm -rf {remote_root_path}")

def sync(local_root_path, remote_root_path):
    global sync_done
    if not sync_done:
        print("## SYNCING REMOTE APP... ##")

        # Remove old app
        _remove_old(remote_root_path)

        # Recreate app directory
        run_command(f"mkdir -p {remote_root_path}")

        # Progress
        component_count = len(app_components)
        progress.print_percentage(0, component_count)

        # Send components
        for number, component in enumerate(app_components, start=1):
            component_path = local_root_path / component

            if component_path.is_file():
                put_file(component_path, remote_root_path)

            elif component_path.is_dir():
                put_dir(component_path, remote_root_path)

            else:
                raise Exception(f"Invalid app component: {component_path}")

            progress.print_percentage(number, component_count)

        sync_done = True
        print("## REMOTE APP SYNC DONE. ##")
