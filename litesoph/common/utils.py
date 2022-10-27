from pathlib import Path
import os

PROJECT_INFO_DIR_NAME = '.litesoph'

PROJECT_DATA_FILE_NAME = 'project_data.json'
PROJECT_DATA_FILE_RELATIVE_PATH = os.fspath(Path(PROJECT_INFO_DIR_NAME) / PROJECT_DATA_FILE_NAME)


WORKFLOW_DATA_FILE_NAME = '.workflow.json'

def check_dir_exists(project_path):
    """ check if directory exists. """
    project_path = Path(project_path)
    dir_exists = os.access(project_path, os.F_OK)
    return dir_exists
        

def create_dir(project_path):
    """ Creates project directory. """
    project_path = Path(project_path)
    parent_writeable = os.access(project_path.parent, os.W_OK)

    if not parent_writeable:
        msg = f'Permission denied creating directory: {project_path}'
        raise PermissionError(msg)

    project_path = Path(project_path)
    os.makedirs(project_path)
