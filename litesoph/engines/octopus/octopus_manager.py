from abc import abstractmethod, ABC
from typing import List, Dict, Any
from litesoph.common.task_data import TaskTypes as tt                    
from litesoph.common.workflows_data import WorkflowTypes as wt        
from litesoph.common.engine_manager import EngineManager

class OCTOPUSManager(EngineManager):
    """Base class for all the engine."""

    implemented_tasks: List[str] = [tt.GROUND_STATE, tt.RT_TDDFT, tt.COMPUTE_SPECTRUM,
                                    tt.TCM, tt.MASKING, tt.MO_POPULATION]

    implemented_workflows: List[str] = [wt.SPECTRUM, wt.AVERAGED_SPECTRUM, wt.KOHN_SHAM_DECOMPOSITION, 
                                        wt.MO_POPULATION_TRACKING]

    @abstractmethod
    def get_task(self, task_info, dependent_task):
        ...

    @abstractmethod
    def get_default_task_param(self, name):
        ...

    @abstractmethod
    def get_task_list():
        ...

    @abstractmethod
    def get_workflow(self, name):
        ...
    
    @abstractmethod
    def get_workflow_list():
        ...

