from pathlib import Path
import os
from litesoph.common.data_sturcture.data_classes import TaskInfo

class TaskManager:

    def __init__(self) -> None:
        self.running_tasks = []

    def run(self):
        pass

    def get_running_task(self):
        pass



def check_task_completion(task_info: TaskInfo):

    if task_info.job_info.submit_mode == 'local':
        return not bool(task_info.job_info.job_returncode)

    if task_info.job_info.submit_mode == 'remote':
        return not bool(task_info.job_info.submit_returncode)
    
    return False