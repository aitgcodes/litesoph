from abc import abstractmethod, ABC
from typing import List, Dict, Any
import copy


class EngineManager(ABC):
    """Base class for all the engine."""

    implemented_tasks: List[str] = []

    implemented_workflows: List[str] = []

    @abstractmethod
    def get_task(self, config, task_info, dependent_task):
        ...

    @abstractmethod
    def get_default_task_param(self, name):
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

