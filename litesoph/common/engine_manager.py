from abc import abstractmethod, ABC
from typing import List, Dict, Any
import copy
from litesoph.common.task import TaskNotImplementedError


class EngineManager(ABC):
    """Base class for all the engine."""
    NAME : str = ''
    implemented_tasks: List[str] = []

    implemented_workflows: List[str] = []

    @abstractmethod
    def get_task(self, config, task_info, dependent_task):
        ...

    @abstractmethod
    def get_default_task_param(self, name, dependent_task):
        ...
    
    def get_task_list(self):
        task_list = copy.deepcopy(self.implemented_tasks)
        return task_list

    @abstractmethod
    def get_workflow(self, name):
        ...
    
    def get_workflow_list(self):
        task_list = copy.deepcopy(self.implemented_workflows)
        return task_list

    def check_task(self, name):
        if not name in self.implemented_tasks:
            raise TaskNotImplementedError(f'{name} is not implemented in {self.NAME}.')