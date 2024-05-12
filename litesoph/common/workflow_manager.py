from typing import Dict, Union, List, Any, Union 
import copy
import os
from pathlib import Path
import shutil
from litesoph.common.task import Task
from litesoph.common.workflows_data import predefined_workflow, WorkflowTypes
from litesoph.common.engine_manager import EngineManager
from litesoph.common.data_sturcture import TaskInfo, WorkflowInfo, factory_task_info, Container, Block
import importlib
from litesoph.common.task_manager import check_task_completion
from litesoph.common.decision_tree import decide_engine, EngineDecisionError
from litesoph.engines import engine_classname


class TaskSetupError(Exception):
    """Raised when unable to creating or opening task."""

class WorkflowEnded(Exception):
    """Raised when the workflow has ended."""

class WorkflowManager:   
    """This is the main interface to edit, modify and run workflows. 

    In litesoph, workflow is modeled as a chain of blocks, where each block contains a list
    of simple tasks that the user can create and run.

    For example, consider the average spectrum workflow.
    We represent the average spectrum workflow as a chain of four blocks, where 
    each block contains the same types of tasks but with different 
    input parameters.
    
    ::
        
            Block-1                  Block-2                  Block-3                  Block-4
        |---------------|      |-----------------|      |--------------------|    |----------------|
        |               |      |                 |      |                    |    |                |
        | 1. ground     |----> |  2. RT-TDDFT- x |----->| 5.compute-spectra-x|--->| 8. compute     | 
        |    state      |      |  3. RT-TDDFT- y |      | 6.compute-spectra-y|    | average spectra|
        |---------------|      |  4. RT-TDDFT- z |      | 7.compute-spectra-z|    |----------------|
                               |-----------------|      |--------------------|  
    
    The dependenices_map maps how each simple task depends on the previous tasks.
    so, for above workflow
    ::

                1 --> None : ground state doesn't depend on any tasks
                2 --> 1    : RT-TDDFT-x dependents on ground state.
                3 --> 1    : RT-TDDFT-y dependents on ground state.
                4 --> 1    : RT-TDDFT-z dependents on ground state.
                5 --> 2    : compute_spectra-x dependents on RT-TDDFT-x.
                6 --> 3    : compute_spectra-y dependents on RT-TDDFT-y.
                7 --> 4    : compute_spectra-z dependents on RT-TDDFT-z.
                8 --> (5, 6, 7) : compute average spectra dependent on compute_spectra-x. 
                                    compute_spectra-y and compute-spectra-z.


    parameters
    ----------

    project_manager: 
                The class that manages creation and deletion of workflows:
    workflow_info: 
                This objects is used to store all the information about a
                workflow.
    config: 
        The configurations used to run the tasks in the workflow.

    
    """
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
            
            if self.workflow_type == WorkflowTypes.TASK_MODE:
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
        """Chooses a default engine for a given workflow type and sets the 
        engine for the workflow."""
        self.workflow_info.engine = decide_engine(self.workflow_type)
        self.engine = self.workflow_info.engine

    
    def _get_engine_manager(self, engine_name) -> EngineManager:
        engine_class = engine_classname.get(engine_name)
        module_path = f'litesoph.engines.{engine_name}.{engine_name}_manager'  
        engine_module = importlib.import_module(module_path)
        engine_manager = getattr(engine_module, f'{engine_class}Manager')
        return engine_manager()

    
    def get_engine_task(self) -> Task:
        """This method returns the Task object of the current_task in the workflow."""
        return self._get_task(self.current_task_info, 
                            task_dependencies=self.get_task_dependencies())

    
    def _get_task(self, current_task_info, task_dependencies ) -> Task:
        engine_manager = self._get_engine_manager(self.engine)
        current_task_info.engine = self.engine
        task = engine_manager.get_task(self.config, self.workflow_type, 
                                       current_task_info, task_dependencies)
        return task

    
    def get_taskinfo(self, task_name) -> List[TaskInfo]:
        """This method returns the list of TaskInfo object with the given name
        in the workflow."""
        task_list = []

        for task_info in self.tasks.values():
            if task_info.name == task_name:
                task_list.append(task_info)
            else:
                continue
        return task_list

    
    def check_engine(self, engine)-> bool:
        """Checks whether a given engine implements the current workflow type"""
        engine_manager = self._get_engine_manager(engine)
        workflow_list = engine_manager.get_workflow_list()
        if self.workflow_type in workflow_list:
            return True
        else:
            return False

    
    def set_engine(self, engine):
        """sets the engine of the workflow"""
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
        """Returns a list of previous task_infos that the present task in dependent on."""

        dependices_uuid = self.dependencies_map.get(self.current_task_info.uuid)
        depedent_task_infos = [] 
        if isinstance(dependices_uuid ,str):
            depedent_task_infos.append(self.tasks.get(dependices_uuid))
        elif isinstance(dependices_uuid, list):
            depedent_task_infos.extend(self.tasks.get(task_uuid) for task_uuid in dependices_uuid)

        for task_info in depedent_task_infos:
            if not check_task_completion(task_info):
                raise TaskSetupError(f'The Dependent task : {task_info.name}, uuid:{task_info.uuid} is not completed.')

        return depedent_task_infos

    def next(self):
        """This method changes the current task to the next task in the workflow."""
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

    def add_block(self, 
                    block_id: int, 
                    name: str, 
                    store_same_task_type:bool = False,
                    task_type = None,
                    metadata = dict()):
        
        """ This method inserts a block into the workflow.

        parameters
        ----------

        block_id: 
            The index where block to be palce in the workflow.
        name: 
            The name of the block.
        store_same_task_type: 
            the variable which indicative if the block contain same type of the tasks.
        task_type: 
            task type if the store_same_task_type is true.
        metadata: 
            This stores information about the tasks in the blocks
            in the context of the workflow."""

        if not store_same_task_type and task_type is not None:
            raise TaskSetupError('task_type must be None if store_same_task_type is True.')

        block = Block(name, store_same_task_type,
                    task_type=task_type, metadata=metadata)

        self.steps.insert(block_id, block)

    def add_task(self, task_name: str,
                         block_id: int, 
                         step_id: int,
                         parameters= dict(),
                         env_parameters= dict(),
                         dependent_tasks_uuid: Union[str, list]= list(), container_cloneable = False):
        
        """This method adds a task into the workflow.
        
        parameters
        ----------
        task_name: 
            The task type.
        block_id: 
            The index of the block to which the task to be added.
        step_id: 
            The index in the task execution list to where task to be added.
        paremeter: 
            The default input parameters of the task.
        env_parameters: 
            This stores information about the task in the context of the workflow.
        dependent_tasks_uuid: 
            The list of task_uuids to which the task dependents on.
        """

        task_info = factory_task_info(task_name)
        
        try :
            self.steps[block_id].task_uuids.append(task_info.uuid)
        except IndexError:
            raise TaskSetupError(f'The block:{block_id} is not defined.')

        self.tasks[task_info.uuid] = task_info
        
        new_container = Container(step_id,
                                block_id,
                                task_name,
                                task_info.uuid,
                                self.workflow_info.uuid,
                                parameters,
                                env_parameters,
                                cloneable = container_cloneable)
        
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
        
        """Adds a dependency task list to the given task."""

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

    def check_block(self, block_id):
        check = True
        if block_id > len(self.steps)-1:
            check = False
        return check

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

    def change_current_task(self, task_uuid):
        self.current_task_info = self.tasks.get(task_uuid)
        
    def check(self):
        pass

    def previous(self):
        pass
    
    def clone(self, clone_workflow: WorkflowInfo,
                    branch_point: int) -> WorkflowInfo:
        
        """This method clones a new workflow_info from the existing workflow_info.
        It clones the task_info from the existing workflow_info and with that it copies all the 
        input and output files generated from that task into the new directory of the cloned task.
        """

        # The concept of the blocks was introduced later then the concept of containers, so 
        # loop over containers to clone the workflow.
        # The better solution might be to loop over blocks instead of containers.

        clone_workflow.engine = copy.deepcopy(self.engine)

        new_branch_point = 0
        branch_point_init= branch_point
        for block in self.steps:
            clone_workflow.steps.append(block.clone())
            if branch_point_init:
                new_branch_point += len(block.task_uuids)
                branch_point_init -= 1

        previous_container = None
        for _, container in enumerate(self.containers):
            if not container.cloneable:
                continue

            ctask_info = factory_task_info(container.task_type)
            clone_container = container.clone(ctask_info.uuid,
                                                self.workflow_info.uuid)
            if previous_container is not None:
                previous_container.next = clone_container.task_uuid
                clone_container.previous = previous_container.task_uuid

            clone_workflow.containers.append(clone_container)
            previous_container = clone_container

            clone_workflow.steps[clone_container.block_id].task_uuids.append(ctask_info.uuid)
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

        clone_workflow.current_step.insert(0, new_branch_point)

        return clone_workflow
            
    def get_summary(self):
        pass
    
    def run_next_task(self):
        pass

    def run_block(self,):
        pass

    def save(self):
        """ saves the workflow_info into the hard drive."""
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
            shutil.copytree(s_path, d_path, dirs_exist_ok=True)
            continue
        shutil.copy(s_path, d_path)

def update_workflowinfo(workflow_dict:dict, workflowinfo: WorkflowInfo):
    
    blocks = workflow_dict.get('blocks')
    task_sequence = workflow_dict.get('task_sequence')
    w_dependency = workflow_dict.get('dependency_map')

    steps = workflowinfo.steps
    tasks = workflowinfo.tasks
    containers = workflowinfo.containers
    dependencies = workflowinfo.dependencies_map
    tasks.clear()
    dependencies.clear()

    for block in blocks: 
        steps.append(Block(name= block['name'],
                            store_same_task_type= block.get('store_same_task_type', True),
                            task_type=block.get('task_type'),
                            metadata= block.get('metadata', dict())))
    prev_cont = None
    for wstep in task_sequence:
        taskinfo = factory_task_info(wstep.task_type)
        container = Container(task_sequence.index(wstep), 
                                wstep.block_id, 
                                wstep.task_type, 
                                taskinfo.uuid, 
                                workflowinfo.uuid,
                                wstep.parameters,
                                wstep.env_parameters)
        
        steps[wstep.block_id].task_uuids.append(taskinfo.uuid)
        
        if prev_cont is not None:
            prev_cont.next = container.task_uuid
            container.previous = prev_cont.task_uuid
        containers.append(container)
        prev_cont = container
        dependent_tasks = w_dependency.get(str(task_sequence.index(wstep)))
        if dependent_tasks is None:
            dependencies[taskinfo.uuid] = None
        elif isinstance(dependent_tasks, str):
            dependencies[taskinfo.uuid] = containers[int(dependent_tasks)].task_uuid
        elif isinstance(dependent_tasks, list):
            dependencies[taskinfo.uuid] = []
            for dtask_index in dependent_tasks:
                dependencies[taskinfo.uuid].append(containers[int(dtask_index)].task_uuid)

        tasks[taskinfo.uuid] = taskinfo


