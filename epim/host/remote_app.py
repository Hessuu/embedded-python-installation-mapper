from pathlib import Path

import settings
from epim.host.remote_operation import *
from epim.util import progress
from epim.util.logging import print

sync_done = False

app_components = [
    "main.py",
    "settings.py",
    "known_imports.py",
    "epim",
]

requirements_dir = f"requirements/{settings.TARGET_PYTHON_VERSION}"

class RemoteApp(object):
        
    @classmethod    
    def sync(cls, local_root_path, remote_root_path):
        global sync_done
        if not sync_done:
            print("## SYNCING REMOTE APP... ##")
    
            # Remove old app
            cls.__remove_old(remote_root_path)
    
            # Recreate app directory
            print(f"# Removing old remote app from: {remote_root_path}")
            RemoteOperation.command(f"mkdir -p {remote_root_path}")
    
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
                    RemoteOperation.put_file(component, remote_root_path)
    
                elif component.is_dir():
                    RemoteOperation.put_dir(component, remote_root_path)
    
                else:
                    raise Exception(f"Invalid component: {component}")
    
                progress.print_percentage(number, component_count)
    
            sync_done = True
            print("## REMOTE APP SYNC DONE. ##")
    
    @classmethod
    def __remove_old(cls, remote_root_path):
        RemoteOperation.command(f"rm -rf {remote_root_path}")

