import os
from pathlib import Path
import time

from litesoph.config import user_data_dir

project_list_file = user_data_dir / 'project_list.txt'

remote_machine_profile = user_data_dir / 'remote_profile.txt'

def update_proj_list(project: Path) -> None:

    proj_time = time.asctime(time.localtime())

    list  = project.name + '\t' + str(project) + '\t'+ proj_time + '\n'

    proj_list = read_proj_list()

    with open(project_list_file , 'w+') as wf:   
        proj_list.insert(0, list)
        for line in proj_list:
            wf.writelines(line)

def read_proj_list():
    
    lines = []
    try:
        with open(project_list_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return lines
    else:
        return lines
        
