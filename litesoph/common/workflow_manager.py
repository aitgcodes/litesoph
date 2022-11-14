import shutil
from pathlib import Path
import os
from typing import Dict, Union, List, Any
import uuid
from dataclasses import dataclass, field
from litesoph.common.task import Task, TaskFailed
from litesoph.common.task_data import (task_dependencies_map,
                                    check_properties_dependencies)
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.workflows_data import predefined_workflow
from litesoph.common.project_status import Status
from litesoph.common.engine_manager import EngineManager
from litesoph.common.data_sturcture import TaskInfo, WorkflowInfo, factory_task_info
from litesoph.engines.gpaw.gpaw_task import GpawTask
from litesoph.engines.nwchem.nwchem_task import NwchemTask
from litesoph.engines.octopus.octopus_task import OctopusTask
import importlib

engine_classname = {
    'gpaw' : 'GPAW',
    'nwchem': 'NWchem',
    'octopus': 'OCTOPUS'
}

class TaskSetupError(Exception):
    """Raised when unable to creating or opening task."""

class WorkflowManager:

    def __init__(self, 
                project_manager, 
                workflow_info: WorkflowInfo, 
                config: Dict[str, str]) -> None:
        
        self.project_manager = project_manager
        self.config = config
        self.workflowinfo = workflow_info
        self.workflow_type = workflow_info.name
        self.user_defined = workflow_info.user_defined
        self.engine = workflow_info.engine
        self.steps = workflow_info.steps
        self.tasks = workflow_info.tasks
        self.directory = workflow_info.path
        self.current_step = workflow_info.current_step
        self.dependencies_map = workflow_info.dependencies_map
        if not self.user_defined:
            if not self.tasks:
                self.workflow_from_db  = predefined_workflow.get('spectrum')
                self.container_list = get_container_list(self.workflow_from_db, workflow_id=workflow_info.uuid)
                update_workflowinfo(self.workflow_from_db, workflow_info)
        self.current_task_info = None
        

    def _get_engine_manager(self, engine_name) -> EngineManager:
        engine_class = engine_classname.get(engine_name)
        module_path = f'litesoph.engines.{engine_name}.{engine_name}_manager'  
        engine_module = importlib.import_module(module_path)
        engine_manager = getattr(engine_module, f'{engine_class}Manager')
        return engine_manager

    def get_engine_task(self) -> Task:
        
        return self._get_task(self.current_task_info, 
                            task_dependencies=self.get_task_dependencies())

    def _get_task(self, current_task_info, task_dependencies ) -> Task:
        engine_manager = self._get_engine_manager(self.engine)
        engine_manager = engine_manager()
        task = engine_manager.get_task(self.config, current_task_info, task_dependencies)
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

    def _get_taskinfo_from_uuid(self, uuids: List[str]) -> List[TaskInfo]:

        task_list = []

        for uuid in uuids:
            for taskinfo in self.tasks:
                if uuid == taskinfo.uuid:
                    task_list.append(taskinfo)
        return task_list


    def create_task_info(self):
        pass

    def get_engine(param: dict):
        pass
    
    def next(self, task_name:str= None) -> TaskInfo:
        
        self.save()

        if self.user_defined:
            if not task_name: 
                raise TaskSetupError("Task in not defined.")
            
            if not self.current_step:
                self.current_step.insert(0, list(self.steps.keys())[0])
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

    def get_summary(self):
        pass
    
    def save(self):
        self.project_manager.save()



@dataclass
class Container:
    id : int
    block_id : int
    task_type: str
    workflow_id: str
    next: Union[str, None] = field(default=None)
    previous: Union[str, None] = field(default=None)



def get_container_list(workflow_dict: dict, workflow_id) -> List[Container]:
    
    container_list = []
    steps = workflow_dict.get('steps')
    prev_cont = None
    for step in steps:
        container = Container(steps.index(step), step.id, step.task_type, workflow_id)
        
        if prev_cont is not None:
            prev_cont.next = container.task_type
            container.previous = prev_cont.task_type
        container_list.append(container)
        prev_cont = container
    return container_list



def update_workflowinfo(workflow_dict:dict, Workflowinfo: WorkflowInfo):
    
    blocks = workflow_dict.get('blocks')
    wstepslist = workflow_dict.get('steps')
    w_dependency = workflow_dict.get('dependency_map')

    steps = Workflowinfo.steps
    tasks = Workflowinfo.tasks
    dependencies = Workflowinfo.dependencies_map
    steps.clear()
    tasks.clear()
    dependencies.clear()

    for block in blocks:
        steps[block] = []

    for wstep in wstepslist:
        taskinfo = factory_task_info(wstep.task_type)
        steps[wstep.block].append(taskinfo.uuid)
        dependendt_tasks = w_dependency[str(wstepslist.index(wstep))]
        
        if dependendt_tasks is None:
            dependencies[taskinfo.uuid] = None
        elif isinstance(dependendt_tasks, str):
            dependencies[taskinfo.uuid] = tasks[int(dependendt_tasks)].uuid
        elif isinstance(dependendt_tasks, list):
            dependencies[taskinfo.uuid] = []
            for dtask_index in dependendt_tasks:
                dependencies[taskinfo.uuid].append(tasks[int(dtask_index)])

        tasks.append(taskinfo)


