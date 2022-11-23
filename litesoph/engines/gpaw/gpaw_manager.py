from typing import List, Dict, Any, Union
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import TaskNotImplementedError
from litesoph.common.task_data import TaskTypes as tt                    
from litesoph.common.workflows_data import WorkflowTypes as wt        
from litesoph.common.engine_manager import EngineManager
from litesoph.engines.gpaw.gpaw_task import GpawTask
from litesoph.engines.gpaw import task_data as td



class GPAWManager(EngineManager):
    """Base class for all the engine."""
    NAME = 'GPAW'
    implemented_tasks: List[str] = [tt.GROUND_STATE, tt.RT_TDDFT, tt.COMPUTE_SPECTRUM,
                                    tt.TCM, tt.MASKING, tt.MO_POPULATION]

    implemented_workflows: List[str] = [wt.SPECTRUM, wt.AVERAGED_SPECTRUM, wt.AVERAGED_SPECTRUM,
                                        wt.MO_POPULATION_TRACKING]


    def get_task(self, config, task_info: TaskInfo, 
                        dependent_tasks: Union[List[TaskInfo], None] =None ):
        self.check_task(task_info.name)
        return GpawTask(config, task_info, dependent_tasks)
    
    def get_default_task_param(self, name, dependent_tasks: Union[List[TaskInfo], None] = None):
        task_default_parameter_map = {
            tt.GROUND_STATE: td.get_gs_default_param,
            tt.RT_TDDFT: td.get_rt_tddft_default_param,
            tt.COMPUTE_SPECTRUM: td.get_compute_spec_param,
            tt.TCM: td.get_tcm_param,
            tt.MO_POPULATION: td.get_mopop_param,
            tt.MASKING: td.get_masking_analysis,
        }
        self.check_task(name)

        get_func = task_default_parameter_map.get(name)
        return get_func()

    def get_workflow(self, name):
        pass
    


