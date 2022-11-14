from typing import List, Dict, Any, Union
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import TaskNotImplementedError
from litesoph.common.task_data import TaskTypes as tt                    
from litesoph.common.workflows_data import WorkflowTypes as wt        
from litesoph.common.engine_manager import EngineManager
from litesoph.engines.gpaw.gpaw_task import GpawTask

class GPAWManager(EngineManager):
    """Base class for all the engine."""

    implemented_tasks: List[str] = [tt.GROUND_STATE, tt.RT_TDDFT, tt.COMPUTE_SPECTRUM,
                                    tt.TCM, tt.MASKING, tt.MO_POPULATION]

    implemented_workflows: List[str] = [wt.SPECTRUM, wt.AVERAGED_SPECTRUM, wt.AVERAGED_SPECTRUM,
                                        wt.MO_POPULATION_TRACKING]


    def get_task(self, config, task_info: TaskInfo, 
                        dependent_tasks: Union[List[TaskInfo], None] =None ):
        if not task_info.name in self.implemented_tasks: 
            raise TaskNotImplementedError(f'{task_info.name} is not implemented in GPAW.')
        return GpawTask(config, task_info, dependent_tasks)
    
    def get_default_task_param(self, name):
        pass

    def get_workflow(self, name):
        pass
    

