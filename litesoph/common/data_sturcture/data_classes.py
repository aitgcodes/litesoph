from dataclasses import dataclass, field, asdict
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
        engine = data['engine']
        state = State.from_dict(data['state'])
        param = data['param']
        input = data['input']
        output = data['output']
        network = data['network']
        local = data['local']

        return cls(_uuid = uuid, 
                    _name = name,
                    path =Path(data['path']), 
                    engine= engine, 
                    state= state,
                    param= param, 
                    input= input, 
                    output= output, 
                    task_data = data['task_data'],
                    engine_param = data['engine_param'],
                    network = network, 
                    local= local)

@dataclass
class Container:
    id : int
    block_id : int
    task_type: str
    task_uuid: str
    workflow_uuid: str
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
                    env_parameters = data['env_parameters'],
                    next = data['next'],
                    previous = data['previous'])


@dataclass
class WorkflowInfo(Info):

    label: str
    path: Path
    _name: str = field(default='')
    description: str = field(default='')
    engine: Union[str, None] = field(default=None)
    user_defined: bool = field(default=False)
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
                    description= data['description'], 
                    path= Path(data['path']),
                    label =data['label'],
                    engine = data['engine'],
                    param= data['param'], 
                    state= state, 
                    user_defined = data['user_defined'],
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



def factory_task_info(name: str) -> TaskInfo:

    return TaskInfo(str(uuid.uuid1()), name)