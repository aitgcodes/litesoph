import shutil
from pathlib import Path
import os
from typing import Dict, Union, List
import uuid

from litesoph.common.task import Task, TaskFailed
from litesoph.common.task_data import (GROUND_STATE,RT_TDDFT,
                                    SPECTRUM,
                                    TCM, MO_POPULATION,
                                    MASKING, task_dependencies_map,
                                    check_properties_dependencies)

from litesoph.common.project_status import Status
from litesoph.common.data_sturcture import TaskInfo, WorkflowInfo, factory_task_info
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
        self.current_task_info = None
        self.status = None

    def get_engine_task(self) -> Task:
        
        task_dependencies = self.get_task_dependencies()
        # if self.engine == 'nwchem':
        #     task = NwchemTask(self.directory, self.config, self.status, **user_input)
        # elif self.engine == 'octopus':
        #     task = OctopusTask(self.directory, self.config, self.status, **user_input)
        # elif self.engine == 'gpaw':
        task = GpawTask(self.config, self.current_task_info, task_dependencies)

        return task

    def get_task_dependencies(self):
        
        if not self.current_task_info:
            raise TaskSetupError('Task in not selected yet.')
        task_name = self.current_task_info.name
        dependencies_data = task_dependencies_map.get(task_name)
        if not dependencies_data:
            return []

        dependent_tasks = []
        for task in dependencies_data:
            if isinstance(task, str):
                dependent_tasks.append(task)
            elif isinstance(task, dict):
                dependent_tasks.extend([key for key  in task.keys()])

        task_list = self._get_taskinfo(dependent_tasks[0])

        if not task_list:
            raise TaskSetupError(f"Dependent task:{dependent_tasks} not done")

        check, msg = check_properties_dependencies(task_name, task_list[0])
        if not check:
            raise TaskSetupError(msg)
        
            
        return task_list

    def _get_taskinfo(self, task_name) -> List[TaskInfo]:

        task_list = []

        for task_info in self.tasks:
            if task_info.name == task_name:
                task_list.append(task_info)
            else:
                continue
        return task_list

    def create_task_info(self):
        pass

    def get_engine(param: dict):
        pass
    
    def next(self, task_name:str= None) -> TaskInfo:
        

        if self.user_defined:
            if not task_name: 
                raise TaskSetupError("Task in not defined.")
            
            if not self.current_step:
                self.current_step.insert(0, self.steps[0])
                self.current_step.insert(1, task_name)
                self.current_step.insert(2, 0)
            else:
                self.current_step[1] = task_name 
                self.current_step[2] = self.current_step[2] + 1
                
            task_info = factory_task_info(task_name)
            self.tasks.append(task_info)

        else:
            # workflow dict should be defined for each engine and workflow. It should specify the steps in a workflow
            # and the tasks involved in each workflow.
            if not self.current_step:
                self.current_step.insert(0, self.steps[0])
                self.current_step.insert(1, self.tasks[self.steps[0]])
                self.current_step.insert(2, 0)
            else:
                if self.current_step[1] == (len(self.steps) - 1):
                    raise TaskSetupError('No more tasks in the workflow.')

                task_name = self.steps[self.current_step[1] + 1 ]
                self.current_step = [task_name, self.current_step[1] + 1]

        if self.engine:
            print(self.engine)
            task_info.engine = self.engine

                
        self.current_task_info = task_info
        self.current_task_info.path = self.directory
        return task_info

    # def start_task(self):

    #     return self.get_engine_task()
        
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
