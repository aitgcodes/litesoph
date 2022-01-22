import pathlib
import os

class WorkManagerModel:
    
    def __init__(self) -> None:
        pass
        
    @staticmethod
    def check_dir_exists(project_path):
        """ check if directory exists. """
        project_path = pathlib.Path(project_path)
        dir_exists = os.access(project_path, os.F_OK)
        return dir_exists
            

    @staticmethod
    def create_dir(project_path):
        """ Creates project directory. """
        project_path = pathlib.Path(project_path)
        parent_writeable = os.access(project_path.parent, os.W_OK)

        if not parent_writeable:
            msg = f'Permission denied creating directory: {project_path}'
            raise PermissionError(msg)

        project_path = pathlib.Path(project_path)
        os.makedirs(project_path)

class SettingsModel:
    pass