import shutil
from pathlib import Path
import os
from typing import Dict
import uuid

from litesoph.common.task import (Task, TaskFailed,
                                GROUND_STATE,RT_TDDFT_DELTA,
                                RT_TDDFT_LASER, SPECTRUM,
                                TCM, MO_POPULATION,
                                MASKING)

from litesoph.common.project_status import Status
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.data_sturcture.data_classes import WorkflowInfo
from litesoph.engines.gpaw.gpaw_task import GpawTask
from litesoph.engines.nwchem.nwchem_task import NwchemTask
from litesoph.engines.octopus.octopus_task import OctopusTask



class TaskSetupError(Exception):
    """Raised when unable to creating or opening task."""

class WorkflowManager:

    def __init__(self, project_manager, workflow_info: WorkflowInfo, config: Dict[str, str]) -> None:
        
        self.project_manager = project_manager
        self.config = config
        self.workflow_type = workflow_info.name
        self.user_defined = workflow_info.user_defined
        self.engine = workflow_info.engine
        self.steps = workflow_info.steps
        self.tasks = workflow_info.tasks
        self.directory = workflow_info.path
        self.current_step = workflow_info.current_step

    def get_engine_task(self, task, user_input) -> Task:
        user_input['task'] = task

        if self.engine == 'nwchem':
            task = NwchemTask(self.directory, self.config, self.status, **user_input)
        elif self.engine == 'octopus':
            task = OctopusTask(self.directory, self.config, self.status, **user_input)
        elif self.engine == 'gpaw':
            task = GpawTask(self.directory, self.config, self.status, **user_input)

        return task

    def init_workflow(self):
        
        self.current_project_data = p_data = {}
    
        p_data['name'] = self.directory.name
        p_data['path'] = str(self.directory)
        p_data['tasks'] = []
        try:
            self.status = Status(self.directory, p_data)
        except Exception:
            p_data = {}
            raise

    def create_task_info(self):
        pass

    def get_engine(param: dict):
        pass
    
    def next(self, task_name:str= None) -> TaskInfo:
        

        if not self.tasks:
            self.init_workflow()

        if self.user_defined:
            if not task_name: 
                raise TaskSetupError("Task in not defined.")
            
            if not self.current_step:
                self.current_step.insert(0, self.steps[0])
                self.current_step.insert(1, task_name)
                self.current_step.insert(2, 0)
                self.tasks['user_defined'] = []
            else:
                self.current_step[1] = task_name 
                self.current_step[2] = self.current_step[2] + 1
                
            task_info = factory_task_info(task_name)
            self.tasks['user_defined'].append(task_info)

        else:
            return
            # workflow dict should be defined for each engine and workflow. It should specify the steps in a workflow
            # and the tasks involved in each workflow.
            if not self.current_step:
                self.current_step = [task_name , 0]
            else:
                if self.current_step[1] == (len(self.steps) - 1):
                    raise TaskSetupError('No more tasks in the workflow.')

                task_name = self.steps[self.current_step[1] + 1 ]
                self.current_step = [task_name, self.current_step[1] + 1]

            task_info = factory_task_info(task_name)
            self.tasks[task_name] = task_info

        if self.engine:
            task_info.engine = self.engine
        
                
        self.current_task_info = task_info
        return task_info

    def start_task(self, user_input):

        return self.get_engine_task(self.current_step[1], user_input)
        
    def check(self):
        pass

    def previous(self):
        pass

    def get_previous_engine(self)-> list:
        non_engine_keys = ['name', 'path', 'tasks', 'geometry']
        keys = self.current_project_data.keys()
        for key in keys:
            if key in non_engine_keys:
                continue
            else:
                return key

    def get_summary(self):
        pass
    
    def save(self):
        self.project_manager.save()
    
def factory_task_info(name: str) -> TaskInfo:

    return TaskInfo(str(uuid.uuid4()), name)