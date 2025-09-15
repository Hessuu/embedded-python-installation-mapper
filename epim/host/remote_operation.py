from fabric import Connection
from pathlib import Path
from scp import SCPClient

import settings
from epim.util.logging import print

class RemoteOperation(object):

    ## SETUP ##
    @classmethod
    def __get_fabric_connection(cls):
        connect_kwargs = {"password": settings.TARGET_PASSWORD}
    
        connection = Connection(host=settings.TARGET_ADDRESS, user=settings.TARGET_USER, connect_kwargs=connect_kwargs)
    
        return connection
    
    @classmethod
    def __get_connection_for_commands(cls):
        return cls.__get_fabric_connection()
    
    @classmethod
    def __get_connection_for_files(cls):
        connection = cls.__get_fabric_connection()
        connection.open()
        spc_client = SCPClient(connection.client.get_transport())
    
        return spc_client
    
    ## COMMANDS ##
    @classmethod
    def command(cls, command: str):
        with cls.__get_connection_for_commands() as connection:
            connection.run(command)
    
    
    ## FILES & DIRECTORIES ##
    @classmethod
    def put_file(cls, local_path: Path, remote_path: Path):
        cls._put_file_object(local_path, remote_path, recursive=False)
    
    @classmethod
    def put_dir(cls, local_path: Path, remote_path: Path):
        cls._put_file_object(local_path, remote_path, recursive=True)
    
    @classmethod
    def _put_file_object(cls, local_path: Path, remote_path: Path, recursive=False):
        with cls.__get_connection_for_files() as connection:
            connection.put(str(local_path), str(remote_path), recursive)
    
    @classmethod
    def get_file(cls, remote_path: Path, local_path: Path):
        with cls.__get_connection_for_files() as connection:
            connection.get( str(remote_path), str(local_path))

