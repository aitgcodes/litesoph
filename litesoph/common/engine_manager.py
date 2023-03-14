from abc import abstractmethod, ABC
from typing import List, Dict, Any
import copy
from litesoph.common.task import TaskNotImplementedError


class EngineManager(ABC):
    """Base class for all litesoph engines.
    
    parameters
    ----------
    Name: 
        name of the engine.
    implemented_tasks: 
        list of task identifiers of the tasks that are implemented.
    implemented_workflows: 
        list of workflow identifiers of the workflows that are implemented.
    """
    
    NAME : str = ''
    implemented_tasks: List[str] = []

    implemented_workflows: List[str] = []

    @abstractmethod
    def get_task(self, config, workflow_type, task_info, dependent_task):
        """This class checks if a task is implemented and if it is implemented
        it returns the task object else raises a TaskNotImplementedError."""
        ...

    @abstractmethod
    def get_default_task_param(self, name, dependent_task):
        """This mentods return the default parameters for a given particular task."""
        ...
    
    def get_task_list(self):
        """This method returns the list of implemented tasks in this engine"""
        task_list = copy.deepcopy(self.implemented_tasks)
        return task_list

    @abstractmethod
    def get_workflow(self, name):
        ...
    
    def get_workflow_list(self):
        """This method returns the list of implemented tasks in this engine"""
        workflow_list = copy.deepcopy(self.implemented_workflows)
        return workflow_list

    def check_task(self, name):
        """This method checks if a given task is implemented in this engine if not
        it  raises a TaskNotImplementedError"""
        if not name in self.implemented_tasks:
            raise TaskNotImplementedError(f'{name} is not implemented in {self.NAME}.')