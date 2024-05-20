from dataclasses import dataclass, field, asdict
import copy
from pathlib import Path
from typing import Any, Dict, List, Union
import json
import os
import uuid
from litesoph.common.data_sturcture.utils import WorkflowInfoEncoder

@dataclass
class State:
    """ This class store the state of jobs, tasks, workflows."""


    @classmethod
    def from_dict(cls, data: Dict[Any, Any]):
        state = cls()
        for key in data:
            setattr(state, key, data[key])
        return state

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def factory_state():

    return State()

@dataclass
class Info:
    """Base class for info objects which required unique id."""

    _uuid: str

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        raise AttributeError('Denied')

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self, cls=WorkflowInfoEncoder, indent=3)

    # def save(self, fp):
    #     try:
    #         json_txt = self.to_json()
    #     except TypeError:
    #         raise
    #     fp.write(json_txt)

@dataclass
class JobInfo:
    """This class stores information about a job.

    parameters
    ----------
    id:
      The id of the job
    directory: 
        The directory in which the job is running
    state: 
        State of the job
    job_script:
        bash script to run the job
    submit_mode: 
        whether the job was submitted locally or to a remote machine.
    job_returncode: 
        return code of the job
    submit_returncode:
        retrun code of job submitting to remote machine.
    submit_output:
        output of job submission to remote machine
    submit_errors:
        errors of job submission to remote machine
    output: 
        Output of the job.
    error: 
        Error of the job
    """
    id: Union[str, None] = field(default= None)
    directory: Union[Path, None] = field(default=None)
    state: Union[str, None] = field(default= None)
    job_script: Union[str, None] = field(default=None)
    submit_mode: Union[str, None] = field(default= 'local')
    job_returncode: Union[int, None] = field(default= None)
    submit_returncode: Union[int, None] = field(default= None)
    submit_output: Union[str, None] = field(default= None)
    submit_error: Union[str, None] = field(default=None)
    output: Union[str, None] = field(default= None)
    error: Union[str, None] = field(default= None)

    @classmethod
    def from_dict(cls, data):
        cls = cls()
        for key, value in data.items():
            if key == 'directory' and isinstance(value, str):
                value = Path(value)

            setattr(cls, key, value)
        return cls

@dataclass
class Block:
    """This class stores information about a block in a the workflow.
    The block is a collection of tasks.
    
    parameters
    ----------

    name: 
        The name of the block.
    store_same_task_type: 
        True if all tasks in the block are of same type.
    task_type: 
        The type of task if "store_same_task_type" is true else None.
    task_uuids: 
        The list of task ids associated with the task.
    metadata: 
        Any optional information about the tasks."""

    name: str
    store_same_task_type: bool = False
    task_type: Union[str, None] = field(default= None)
    task_uuids: List[str] = field(default_factory= list)
    metadata: Dict[str, str] = field(default_factory= dict)

    
    @classmethod
    def from_dict(cls, data):
        return cls(name = data['name'],
                    store_same_task_type = data.get('store_same_task_type', False),
                    task_type = data.get('task_type', None),
                    task_uuids = data.get('task_uuids', list()),
                    metadata = data.get('metadata', dict()))

    def clone(self):
        data = self.to_dict()
        data['task_uuids'].clear()
        return Block.from_dict(data)

    def to_dict(self):
        return asdict(self)

    
def factory_job_info():
    return JobInfo()
    
@dataclass
class TaskInfo(Info):
    """This class stores all the information about a task.
    
    parameters
    ----------
    name: 
        Task identifier.
    engine: 
        Which engine to use to run the task.
    state: 
        store information about the state of the task.
    path: 
        path of the workflow directory.
    task_data: 
        It store any miscellaneous information about the task that 
        depends on the engine.
    param: 
        The input parameters of the task.
    engine_param: 
        The input parameters of the task in the format of the
        engine used.
    input: 
        It's a dictionary store that stores input files generated for the task.
    output: 
        It stores output files generated for by the task.
    local_copy_files: 
        list of relative paths of files to be copied to clone a task.
    remote_copy_files: 
        list of relative paths of files to be copied from the remote machine.
    job_info: 
        Containes all the information about submitting and running the job. (This is new feature in development)
    network: 
        Contains information about the job that was submitted to network. 
    local: 
        Contains information about the job that was submitted locally.
        (network and the local variable will be removed once the job_info is incorporated.)   
        
    """

    _name: str
    engine: Union[str, None] = field(default=None)
    state: State = field(default_factory= factory_state)
    path: Union[Path, None] = field(default=None)
    task_data: Dict[Any, Any] = field(default_factory= dict)
    param: Dict[Any, Any] = field(default_factory=dict) 
    engine_param: Dict[Any, Any] = field(default_factory=dict)
    input: Dict[Any, Any] = field(default_factory=dict)
    output: Dict[Any, Any] = field(default_factory=dict)
    local_copy_files: List[Any] = field(default_factory=list)
    remote_copy_files: List[Any] = field(default_factory=list)
    job_info: JobInfo = field(default_factory= factory_job_info)
    network: Dict[Any, Any] = field(default_factory=dict)
    local : Dict[Any, Any] = field(default_factory=dict)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        raise AttributeError('Denied')


    @classmethod
    def from_dict(cls, data: Dict[Any, Any]):
        uuid = data['_uuid']
        name = data['_name']
        engine = data.get('engine', None)
        state = State.from_dict(data.get('state', dict()))
        param = data.get('param', dict())
        input = data.get('input', dict())
        output = data.get('output', dict())
        network = data.get('network', dict())
        local = data.get('local', dict())
        path = data.get('path', None)
        if path is not None:
            path = Path(path)

        local_copy_files = data.get('local_copy_files', list())
        remote_copy_files = data.get('remote_copy_files', list())
        
        job_info = data.get('job_info', JobInfo())
        if isinstance(job_info, dict):
            job_info = JobInfo.from_dict(job_info)

        return cls(_uuid = uuid, 
                    _name = name,
                    path =path, 
                    engine= engine, 
                    state= state,
                    param= param, 
                    input= input, 
                    output= output, 
                    local_copy_files = local_copy_files,
                    remote_copy_files = remote_copy_files,
                    task_data = data['task_data'],
                    engine_param = data['engine_param'],
                    job_info = job_info,
                    network = network, 
                    local= local)
    
    def clone(self, task_info):
        for key, vlaue in self.__dict__.items():
            if key in ['_uuid']:
                continue
            setattr(task_info, key, copy.deepcopy(vlaue))

        return task_info

@dataclass
class Container:
    """This class stores inforamtions about a task in the context of the workflow.
        Each container can be associated with only on task.

    parameters
    ----------

    id: 
        index of the container in the containers list.
    block_id: 
        index of the block which the task belong to.
    task_type: 
        the type of the task it is associated with.
    task_uuid: 
        the uuid of the task it is associated with.
    workflow_uuid: 
        the uuid of the workflow the task is present in.
    parameters: 
        It dictionary that contains the parameters of the task in 
        in context of the workflow.
    env_parameters: 
        stores any miscellaneous information in context with with workflow.
    next : 
        stores uuid of the next task.
    previous : 
        stores uuid of the previous task."""

    id : int
    block_id : int
    task_type: str
    task_uuid: str
    workflow_uuid: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    env_parameters: Dict[str, Any] = field(default_factory=dict)
    next: Union[str, None] = field(default=None)
    previous: Union[str, None] = field(default=None)
    cloneable : bool = True

    @classmethod
    def from_dict(cls, data: Dict[Any, Any]):
        return cls(id = data['id'],
                    block_id = data['block_id'],
                    task_type = data['task_type'],
                    task_uuid = data['task_uuid'],
                    workflow_uuid = data['workflow_uuid'],
                    parameters = data.get('parameters', dict()),
                    env_parameters = data.get('env_parameters',  dict()),
                    next = data.get('next', None),
                    previous = data.get('previous', None),
                    cloneable = data.get('cloneable', True))

    def clone(self, task_uuid, 
                    workflow_uuid):
        data = self.to_dict()
        data.update(dict(task_uuid = task_uuid,
                    workflow_uuid = workflow_uuid))
        return Container.from_dict(data)


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowInfo(Info):
    """This class store all the information of a workflow.


    The workflow is modeled ordered sequence of blocks, where each contains
    a list of same type of task but with different parameters.
    For example Average specrtrum workflow is::
    
        block_1(Ground state tasks) -> block_2(RT TDDFT tasks) -> block_3(compute spectrum tasks) -> block_4(compute average spectrum)
                ground_state               rt tddft in x             compute spectrum in x                   compute average spectrum
                                            rt tddft in y             compute spectrun in y 
                                            rt tddft in z             compute spectrun in z
    
    parameters
    ----------

    label: 
        User given name of the workflow.
    path: 
        Path to workflow directory.
    name: 
        The type of workflow, for example: spectrum, ksd.
    description: 
        string, description about the workflow.
    engine: 
        The engine used in the workflow.
    task_mode: 
        If false, the workflow comes with a defined sequence of tasks.
        For example, the spectrum workflow is: ground_state -> RT TDDFT -> compute spectrum.
        If true, the user is given full control over the workflow to add any kind of
        task to it.
    param: 
        any parameters related to the workflow.
    steps: 
        It's a list of blocks. 
    containers: 
        It's a list of containers. In a workflow, each task is associated with a container,
        which stores information about the task in context of the workflow.
        Currently, this list is used to navigate one task to another in a workflow.
    state: 
        It stores information about what tasks are running and what step the workflow is in.
        (currently this variable is not in use)
    dependencies_map: 
        It's a dictionary that maps each tasks with the list of tasks that it depend on it.
    tasks: 
        It's a dictionary that maps that task uuid  with the task_info objects.
    current_step: 
        It's a list that store the current task the workflow is in.
    """

    label: str
    path: Path
    _name: str = field(default='')
    description: str = field(default='')
    engine: Union[str, None] = field(default=None)
    task_mode: bool = field(default=False)
    param: Dict[Any, Any] = field(default_factory=dict)
    steps: List[Block] = field(default_factory=list)
    containers: List[Container] = field(default_factory=list)
    state: State = field(default_factory= factory_state)
    dependencies_map : Dict[str, str] = field(default_factory=dict)
    tasks: Dict[str , TaskInfo] = field(default_factory=dict)
    current_step: list = field(default_factory=list)
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name == '':
            self._name = value
        else:
            raise AttributeError('Denied')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        state = data.pop('state')
        state = State.from_dict(state)
        tasks = {uuid : TaskInfo.from_dict(task) for uuid, task in data['tasks'].items()} 
        containers = [Container.from_dict(container) for container in data['containers']]
        current_step = data['current_step']
        steps_data = data['steps']
        steps = []
        if not steps_data:
            steps.append(Block(name= 'task_mode'))
            
            for container in containers:
                steps[0].task_uuids.append(container.task_uuid)

        elif isinstance(steps_data[0], str):
            for block in steps_data:
                steps.append(Block(name= block,
                                    store_same_task_type=True))

            for container in containers:
                steps[container.block_id].task_uuids.append(container.task_uuid)
        
        else:
            steps = [Block.from_dict(block) for block in steps_data]

        steps_data = steps
        return cls(_uuid = data['_uuid'],
                     _name=data['_name'], 
                    description= data.get('description'), 
                    path= Path(data['path']),
                    label =data.get('label'),
                    engine = data.get('engine'),
                    param= data.get('param'), 
                    state= state, 
                    task_mode = data.get('task_mode', False),
                    steps = steps,
                    containers = containers,
                    tasks= tasks, 
                    dependencies_map = data['dependencies_map'], 
                    current_step=current_step)
        
@dataclass
class ProjectInfo(Info):
    """This class stores all the information about a project.
    
    parameters
    ----------
    label: 
        Name of the project.
    path: 
        Path to the project directory.
    description: 
        string describing the project.
    config: 
        configuration used in the project.
    workflows: 
        List of all the workflow_info of workflows in the project."""

    label: str
    path: Path
    description: str = field(default='')
    config: Dict[Any, Any] = field(default_factory=dict)
    workflows: List[WorkflowInfo]= field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        workflows = [WorkflowInfo.from_dict(workflow) for workflow in data['workflows']]
        return cls(_uuid = data['_uuid'], 
                    label=data['label'], 
                    description= data['description'],
                    path =Path(data['path']), 
                    workflows= workflows)

    @classmethod
    def clone(cls, project_info):
        return cls

def factory_task_info(name: str) -> TaskInfo:

    return TaskInfo(str(uuid.uuid4()), name)