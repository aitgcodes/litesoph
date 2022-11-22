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
from litesoph.common.engine_manager import EngineManager
from litesoph.common.data_sturcture import TaskInfo, WorkflowInfo, factory_task_info, Container
import importlib
from litesoph.common.decision_tree import decide_engine, EngineDecisionError

engine_classname = {
    'gpaw' : 'GPAW',
    'nwchem': 'NWChem',
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
        self.workflow_info = workflow_info
        self.workflow_type = workflow_info.name
        self.user_defined = workflow_info.user_defined
        self.engine = workflow_info.engine
        self.steps = workflow_info.steps
        self.containers = workflow_info.containers
        self.tasks = workflow_info.tasks
        self.directory = workflow_info.path
        self.current_step = workflow_info.current_step
        self.dependencies_map = workflow_info.dependencies_map
        self.user_defined = workflow_info.user_defined = True
        self.current_task_info = None
        self.choose_default_engine()
        
    def choose_default_engine(self):
        engine = self.workflow_info.param.get('engine', None)
        if engine and (engine != 'auto-mode'):
            self.workflow_info.engine = engine
            self.engine = self.workflow_info.engine

    def _get_engine_manager(self, engine_name) -> EngineManager:
        engine_class = engine_classname.get(engine_name)
        module_path = f'litesoph.engines.{engine_name}.{engine_name}_manager'  
        engine_module = importlib.import_module(module_path)
        engine_manager = getattr(engine_module, f'{engine_class}Manager')
        return engine_manager()

    def get_engine_task(self) -> Task:
        
        return self._get_task(self.current_task_info, 
                            task_dependencies=self.get_task_dependencies())

    def _get_task(self, current_task_info, task_dependencies ) -> Task:
        engine_manager = self._get_engine_manager(self.engine)
        current_task_info.engine = self.engine
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

        for task_info in self.tasks.values():
            if task_info.name == task_name:
                task_list.append(task_info)
            else:
                continue
        return task_list

    def set_engine(self, engine):
        self.workflow_info.engine = engine
    
    def create_task_info(self):
        pass

    def get_engine(param: dict):
        pass
    
    def next(self, task_name:str= None) -> TaskInfo:
        
        self.save()

        if not task_name: 
            raise TaskSetupError("Task in not defined.")
        
        if not self.current_step:
            self.current_step.insert(0, 'user_defined')
            self.current_step.insert(1, task_name)
            self.current_step.insert(2, 0)
        else:
            self.current_step[1] = task_name 
            self.current_step[2] = self.current_step[2] + 1
            
        task_info = factory_task_info(task_name)
        self.tasks[task_info.uuid]=  task_info

        if self.engine:
            task_info.engine = self.engine

                
        self.current_task_info = task_info
        self.current_task_info.path = self.directory
        return task_info

    def update_task_param(self, step_id: int, param: dict):
        pass

    def add_task(self, task_name,
                         block_id, 
                         step_id,
                         dependent_task_step_id):
        pass

    def add_block(self, block_id, block_name):
        pass

    def check(self):
        pass

    def previous(self):
        pass

    def get_summary(self):
        pass
    
    def run_next_task(self):
        pass

    def run_block(self,):
        pass

    def save(self):
        self.project_manager.save()


class WorkflowMode(WorkflowManager):

    def __init__(self, 
                project_manager, 
                workflow_info: WorkflowInfo, 
                config: Dict[str, str]) -> None:
        
        
        super().__init__(project_manager,
                        workflow_info,
                        config)
        self.workflow_info.user_defined = False
        if not self.tasks:
            self.workflow_from_db  = predefined_workflow.get(self.workflow_type)
            update_workflowinfo(self.workflow_from_db, workflow_info)

    def choose_default_engine(self):
        self.workflow_info.engine = decide_engine(self.workflow_type)
        self.engine = self.workflow_info.engine        

    def get_task_dependencies(self,):
        denpendices_uuid = self.dependencies_map.get(self.current_task_info.uuid)
        if denpendices_uuid is None:
            return []
        elif isinstance(denpendices_uuid ,str):
            return [self.tasks.get(denpendices_uuid)]
        elif isinstance(denpendices_uuid, list):
            return [self.tasks.get(task_uuid) for task_uuid in denpendices_uuid]

    def next(self) -> TaskInfo:
        
        self.save()

        if not self.current_step:
            container = self.containers[0]
            self.current_step.insert(0, 0)
            task_id = container.task_uuid
        else:
            container = self.containers[self.current_step[0]]
            if container.next is None:
                raise TaskSetupError('No more tasks in the workflow.')
            task_id = container.next
            self.current_step[0] += 1
            container  = self.containers[self.current_step[0]]
        self.current_task_info = self.tasks.get(task_id)
        
        if self.engine:
            self.current_task_info.engine = self.engine
            engine_manager = self._get_engine_manager(self.engine)
            param = engine_manager.get_default_task_param(self.current_task_info.name, self.get_task_dependencies())
            param.update(container.env_parameters)
            self.current_task_info.param.update(param)
        self.current_task_info.path = self.directory
        return self.current_task_info

    def check_engine(self, engine)-> bool:
        engine_manager = self._get_engine_manager(engine)
        workflow_list = engine_manager.get_workflow_list()
        if self.workflow_type in workflow_list:
            return True
        else:
            return False
    
    def set_engine(self, engine):
        check = self.check_engine(engine)
        if check:
            self.workflow_info.engine = engine
            self.engine = self.workflow_info.engine
        else:
            raise EngineDecisionError(f'workflow: {self.workflow_type} is not supported implemented in {engine}')

def update_workflowinfo(workflow_dict:dict, workflowinfo: WorkflowInfo):
    
    blocks = workflow_dict.get('blocks')
    wstepslist = workflow_dict.get('steps')
    w_dependency = workflow_dict.get('dependency_map')

    steps = workflowinfo.steps
    tasks = workflowinfo.tasks
    containers = workflowinfo.containers
    dependencies = workflowinfo.dependencies_map
    tasks.clear()
    dependencies.clear()

    steps.extend(blocks)
    prev_cont = None
    for wstep in wstepslist:
        taskinfo = factory_task_info(wstep.task_type)
        container = Container(wstepslist.index(wstep), 
                                wstep.block_id, 
                                wstep.task_type, 
                                taskinfo.uuid, 
                                workflowinfo.uuid,
                                wstep.env_parameters)
        if prev_cont is not None:
            prev_cont.next = container.task_uuid
            container.previous = prev_cont.task_uuid
        containers.append(container)
        prev_cont = container
        dependent_tasks = w_dependency.get(str(wstepslist.index(wstep)))
        if dependent_tasks is None:
            dependencies[taskinfo.uuid] = None
        elif isinstance(dependent_tasks, str):
            dependencies[taskinfo.uuid] = containers[int(dependent_tasks)].task_uuid
        elif isinstance(dependent_tasks, list):
            dependencies[taskinfo.uuid] = []
            for dtask_index in dependent_tasks:
                dependencies[taskinfo.uuid].append(containers[int(dtask_index)].task_uuid)

        tasks[taskinfo.uuid] = taskinfo


