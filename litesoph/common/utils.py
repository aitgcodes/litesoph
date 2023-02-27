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


def get_new_directory(path:Path) -> Path:
    """Checks if the directory exists and addeds a number to name untill
    a new name is found."""
    parent = path.parent
    name = path.name
    i = 1
    while True:
        if path.exists():
            if i == 1:
                name = name + f'{i}'
            else:    
                name = name[:-(len(str(i)))] + f'{i}'
            path = parent / name
            i += 1
        else:
            break
    return path

#----------------------------------------------
def get_pol_list(pol_var:str):
    assert pol_var in ["X", "Y", "Z"] 
    if pol_var == "X":
        pol_list = [1,0,0]         
    elif pol_var == "Y":
        pol_list = [0,1,0] 
    elif pol_var == "Z":
        pol_list = [0,0,1]                
    return pol_list

def get_pol_var(pol_list:list):
    if pol_list == [1,0,0]:
        pol_var = "X"          
    elif pol_list == [0,1,0]:
        pol_var = "Y" 
    elif pol_list == [0,0,1]    :
        pol_var = "Z"                
    return pol_var