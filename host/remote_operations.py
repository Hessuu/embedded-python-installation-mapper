import settings
from fabric import Connection
from pathlib import Path
from scp import SCPClient

## SETUP ##
def __get_fabric_connection():
    connect_kwargs = {"password": settings.TARGET_PASSWORD}

    connection = Connection(host=settings.TARGET_ADDRESS, user=settings.TARGET_USER, connect_kwargs=connect_kwargs)

    return connection

def __get_connection_for_commands():
    return __get_fabric_connection()

def __get_connection_for_files():
    connection = __get_fabric_connection()
    connection.open()
    spc_client = SCPClient(connection.client.get_transport())

    return spc_client

## COMMANDS ##
def run_command(command: str):
    with __get_connection_for_commands() as connection:
        connection.run(command)


## FILES & DIRECTORIES ##
def put_file(local_path: Path, remote_path: Path):
    _put_file_object(local_path, remote_path, recursive=False)

def put_dir(local_path: Path, remote_path: Path):
    _put_file_object(local_path, remote_path, recursive=True)

def _put_file_object(local_path: Path, remote_path: Path, recursive=False):
    with __get_connection_for_files() as connection:
        connection.put(str(local_path), str(remote_path), recursive)

def get_file(remote_path: Path, local_path: Path):
    with __get_connection_for_files() as connection:
        connection.get( str(remote_path), str(local_path))

