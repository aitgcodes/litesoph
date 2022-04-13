import os
from pathlib import Path
import time

from litesoph.config import user_data_dir

project_list_file = user_data_dir / 'project_list.txt'

remote_machine_profile = user_data_dir / 'remote_profile.txt'

def update_proj_list(project: Path) -> None:
    """Added new projects to the list with timestamp. if project exists it updates the timestamp."""
    proj = ''
    cur_time = time.asctime(time.localtime())
    proj_list = read_proj_list()

    if proj_list:
        for proj_item in proj_list:
            if str(project) in proj_item:
                proj_list.remove(proj_item)
                items = proj_item.split('\t')
                items[2] = cur_time + '\n'
                proj = "\t".join(items)

    if not proj:
        proj  = project.name + '\t' + str(project) + '\t'+ cur_time + '\n'


    with open(project_list_file , 'w+') as wf:   
        proj_list.insert(0, proj)
        for line in proj_list:
            wf.writelines(line)

def read_proj_list() -> list:
    """ Reads the project list file and returns list of lines."""
    lines = []
    try:
        with open(project_list_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return lines
    else:
        return lines
        
