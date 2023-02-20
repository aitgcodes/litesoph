from typing import Dict, Union, List, Any, Union 
import copy
import os
from pathlib import Path
import shutil
from litesoph.common.task import Task
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

class WorkflowEnded(Exception):
    """Raised when the workflow has ended."""

class WorkflowManager:

    def __init__(self, 
                project_manager, 
                workflow_info: WorkflowInfo, 
                config: Dict[str, str]) -> None:
        
        self.project_manager = project_manager
        self.config = config
        self.workflow_info = workflow_info
        self.workflow_type = workflow_info.name
        self.task_mode = workflow_info.task_mode
        self.engine = workflow_info.engine
        self.steps = workflow_info.steps
        self.containers = workflow_info.containers
        self.tasks = workflow_info.tasks
        self.directory = workflow_info.path
        self.current_step = workflow_info.current_step
        self.dependencies_map = workflow_info.dependencies_map
        self.current_task_info = None

        if not self.workflow_info.engine:
            self.choose_default_engine()

        if not self.current_step:
            
            if self.workflow_type == 'task_mode':
                self.task_mode = workflow_info.task_mode = True
            
            else:
                self.workflow_from_db  = predefined_workflow.get(self.workflow_type)
                update_workflowinfo(self.workflow_from_db, workflow_info)
                self.current_container = self.containers[0]
                self.current_step.insert(0, 0)
                self.current_task_info = self.tasks.get(self.current_container.task_uuid)
                self.prepare_task()
        else:
            self.current_container = self.containers[self.current_step[0]]
            self.current_task_info = self.tasks.get(self.current_container.task_uuid)

        
    def choose_default_engine(self):
        self.workflow_info.engine = decide_engine(self.workflow_type)
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

    
    def get_taskinfo(self, task_name) -> List[TaskInfo]:

        task_list = []

        for task_info in self.tasks.values():
            if task_info.name == task_name:
                task_list.append(task_info)
            else:
                continue
        return task_list

    
    def check_engine(self, engine)-> bool:
        engine_manager = self._get_engine_manager(engine)
        workflow_list = engine_manager.get_workflow_list()
        if self.workflow_type in workflow_list:
            return True
        else:
            return False

    
    def set_engine(self, engine):
        
        if self.workflow_info.task_mode:
            self.workflow_info.engine = engine
            self.engine = self.workflow_info.engine
        else:
            check = self.check_engine(engine)
            if check:
                self.workflow_info.engine = engine
                self.engine = self.workflow_info.engine
            else:
                raise EngineDecisionError(f'workflow: {self.workflow_type} is not supported implemented in {engine}')

    
    def get_task_dependencies(self):
        denpendices_uuid = self.dependencies_map.get(self.current_task_info.uuid)
        if denpendices_uuid is None:
            return []
        elif isinstance(denpendices_uuid ,str):
            return [self.tasks.get(denpendices_uuid)]
        elif isinstance(denpendices_uuid, list):
            return [self.tasks.get(task_uuid) for task_uuid in denpendices_uuid]

    def next(self):
        
        self.save()
        if not self.current_step:
            self.current_container = self.containers[0]
            self.current_step.insert(0, 0)
            self.current_task_info = self.tasks.get(self.current_container.task_uuid)
            self.prepare_task()
            return
        
        if self.current_container.next is None:
            raise WorkflowEnded('No more tasks in the workflow.')
        
        self.current_step[0] += 1
        self.current_container = self.containers[self.current_step[0]]
        self.current_task_info = self.tasks.get(self.current_container.task_uuid)
        self.prepare_task()


    def add_task(self, task_name: str,
                         block_id: int, 
                         step_id: int,
                         parameters= dict(),
                         env_parameters= dict(),
                         dependent_tasks_uuid: Union[str, list]= list()):

        task_info = factory_task_info(task_name)
        self.tasks[task_info.uuid] = task_info
        
        new_container = Container(step_id,
                                block_id,
                                task_name,
                                task_info.uuid,
                                self.workflow_info.uuid,
                                parameters,
                                env_parameters)
        
        if step_id == 0:
            self.containers.append(new_container)
    
        elif step_id == len(self.containers):
            self.containers.append(new_container)
            new_container.previous = self.containers[-2].task_uuid
            self.containers[-2].next = new_container.task_uuid
        else:
            self.containers.insert(step_id, new_container)
            new_container.previous = self.containers[step_id-1].task_uuid
            self.containers[step_id-1].next = new_container.task_uuid
            new_container.next = self.containers[step_id +1].task_uuid
            for container in self.containers[step_id+1:]:
                container.id += 1

        self.add_dependency(task_info.uuid, dependent_tasks_uuid)


    def add_dependency(self, task_uuid: str, 
                        dependent_tasks_uuid: Union[str, list]= list()):

        dependent_list =[]
        if isinstance(dependent_tasks_uuid, str):
            dependent_list.append(dependent_tasks_uuid)
        else:
            dependent_list.extend(dependent_tasks_uuid)
        dependent_id = self.dependencies_map.get(task_uuid, None)
        if not dependent_id:
            self.dependencies_map.update({task_uuid: dependent_list})
            return

        if isinstance(dependent_id, str):
            dependent_list.insert(0, dependent_id)
            self.dependencies_map.update({task_uuid: dependent_list})
        else:
            dependent_id.extend(dependent_list)
            self.dependencies_map.update({task_uuid: dependent_id})

    
    def get_continer_by_task_uuid(self, task_uuid):
        for container in self.containers:
            if container.task_uuid == task_uuid:
                return container
        raise ValueError(f'task_uuid:{task_uuid} not present in containers')

    def get_container_index(self, task_uuid):
        container = self.get_continer_by_task_uuid(task_uuid)
        return container.id
        
    def get_continer_by_block_id(self, block_id):
        for container in self.containers:
            if container.task_uuid == block_id:
                return container
        
    def prepare_task(self):
        if self.engine:
            self.current_task_info.engine = self.engine
            engine_manager = self._get_engine_manager(self.engine)
            param = engine_manager.get_default_task_param(self.current_task_info.name, self.get_task_dependencies())
            param.update(self.current_container.parameters)
            self.current_task_info.param.update(param)
        self.current_task_info.path = self.directory

    def add_block(self, block_id, block_name):
        pass

    def check(self):
        pass

    def previous(self):
        pass
    
    def clone(self, clone_workflow: WorkflowInfo,
                    branch_point: int) -> WorkflowInfo:


        previous_container = None
        for _, container in enumerate(self.containers):

            ctask_info = factory_task_info(container.task_type)
            clone_container = container.clone(ctask_info.uuid,
                                                self.workflow_info.uuid)
            if previous_container is not None:
                previous_container.next = clone_container.task_uuid
                clone_container.previous = previous_container.task_uuid

            clone_workflow.containers.append(clone_container)
            previous_container = clone_container

            parent_task_info = self.tasks.get(container.task_uuid)

            if container.block_id <= branch_point:
                ctask_info = parent_task_info.clone(ctask_info)
                ctask_info.path = copy.deepcopy(clone_workflow.path)
                copy_task_files(self.directory, 
                                parent_task_info.local_copy_files,
                                clone_workflow.path)

            clone_workflow.tasks[ctask_info.uuid] = ctask_info

            dependent_tasks = self.dependencies_map.get(container.task_uuid)

            if not dependent_tasks:
                clone_workflow.dependencies_map[ctask_info.uuid] = None

            elif isinstance(dependent_tasks, str):
                index = self.get_container_index(dependent_tasks)
                clone_workflow.dependencies_map[ctask_info.uuid] = clone_workflow.containers[index].task_uuid

            elif isinstance(dependent_tasks, list):
                clone_workflow.dependencies_map[ctask_info.uuid] = []
                for dtask in dependent_tasks:
                    index = self.get_container_index(dtask)
                    clone_workflow.dependencies_map[ctask_info.uuid].append(clone_workflow.containers[index].task_uuid)

        clone_workflow.current_step.insert(0, branch_point)

        return clone_workflow
            
    def get_summary(self):
        pass
    
    def run_next_task(self):
        pass

    def run_block(self,):
        pass

    def save(self):
        self.project_manager.save()

def copy_task_files(source ,file_list, destination):
    workflow_path = Path(source)
    destination_path = Path(destination)
    for path in file_list:
        s_path = Path.joinpath(workflow_path, path)
        d_path = Path.joinpath(destination_path, path)
        sub_path = destination_path
        for part in Path(path).parent.parts:
            sub_path = sub_path / part
            if not sub_path.exists():
                os.mkdir(sub_path)
                continue
        if s_path.is_dir():
            shutil.copytree(s_path, d_path)
            continue
        shutil.copy(s_path, d_path)

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
                                wstep.parameters,
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


