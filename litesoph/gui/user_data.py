import os
from pathlib import Path
import time

from litesoph.config import user_data_dir

project_list_file = user_data_dir / 'project_list.txt'

remote_machine_profile = user_data_dir / 'remote_profile.txt'

def update_proj_list(project: Path) -> None:
    """Added new projects to the list with timestamp. if the project exists it updates the timestamp."""
    proj = ''
    proj_list = []
    cur_time = time.asctime(time.localtime())

    try:
        with open(project_list_file, 'r') as f:
            proj_list = f.readlines()
    except FileNotFoundError:
        pass


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
            wf.write(line)

        
def update_remote_profile_list(profile: dict) -> None:
    """It adds new profile to the list. If the profile is already present it's moved to the top. """

    line  = profile['username'] + '\t' + profile['ip'] + '\t'+ str(profile['port']) + '\t' + profile['remote_path'] + '\n'
    profile_list = []

    try:
        with open(remote_machine_profile, 'r') as f:
            profile_list = f.readlines()
    except FileNotFoundError:
        pass
          
    if  line in profile_list:
        profile_list.remove(line)
        profile_list.insert(0, line)
    else:
        profile_list.insert(0, line)

    with open(remote_machine_profile , 'w+') as wf:   
        for line in profile_list:
            wf.write(line)

def get_remote_profile() -> dict:

    try:
        with open(remote_machine_profile, 'r') as f:
            profile_list = f.readlines()
            if not profile_list:
                return
    except FileNotFoundError:
        return
    else:
        profile_list = profile_list[0].strip('\n').split('\t')
        profile = {
            'username' : profile_list[0],
            'ip' : profile_list[1],
            'port': profile_list[2],
            'remote_path' : profile_list[3]
        } 
        return profile
