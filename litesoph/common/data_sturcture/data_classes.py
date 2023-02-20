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

@dataclass()
class Info:

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
class TaskInfo(Info):

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

        local_copy_files = data.get('local_copy_list', list())
        remote_copy_files = data.get('remote_copy_list', list())
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
    id : int
    block_id : int
    task_type: str
    task_uuid: str
    workflow_uuid: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    env_parameters: Dict[str, Any] = field(default_factory=dict)
    next: Union[str, None] = field(default=None)
    previous: Union[str, None] = field(default=None)

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
                    previous = data.get('previous', None))

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

    label: str
    path: Path
    _name: str = field(default='')
    description: str = field(default='')
    engine: Union[str, None] = field(default=None)
    task_mode: bool = field(default=False)
    param: Dict[Any, Any] = field(default_factory=dict)
    steps: List[str] = field(default_factory=list)
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
        return cls(_uuid = data['_uuid'],
                     _name=data['_name'], 
                    description= data.get('description'), 
                    path= Path(data['path']),
                    label =data.get('label'),
                    engine = data.get('engine'),
                    param= data.get('param'), 
                    state= state, 
                    task_mode = data.get('task_mode', False),
                    steps = data['steps'],
                    containers = containers,
                    tasks= tasks, 
                    dependencies_map = data['dependencies_map'], 
                    current_step=current_step)
        
@dataclass
class ProjectInfo(Info):

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