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

    net_output = task_info.network
    local = task_info.local

    if local:
        returncode = local.get('returncode', 1)
        return not bool(returncode)

    returncode = net_output.get('sub_returncode', 1)
    return not bool(returncode)