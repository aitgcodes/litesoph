from typing import List, Dict, Any, Union
from litesoph.common.task_data import TaskTypes as tt   
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import TaskNotImplementedError                 
from litesoph.common.workflows_data import WorkflowTypes as wt        
from litesoph.common.engine_manager import EngineManager
from litesoph.engines.nwchem.nwchem_task import NwchemTask, PumpProbePostpro
from litesoph.engines.nwchem import task_data as td
from .spectrum_task import ComputeAvgSpectrum, ComputeSpectrum

class NWChemManager(EngineManager):
    """Base class for all the engine."""

    implemented_tasks: List[str] = [tt.GROUND_STATE, tt.RT_TDDFT, tt.COMPUTE_SPECTRUM,
                                    tt.TCM, tt.MASKING, tt.MO_POPULATION, tt.COMPUTE_AVERAGED_SPECTRUM,
                                    tt.COMPUTE_TAS]

    implemented_workflows: List[str] = [wt.SPECTRUM, wt.AVERAGED_SPECTRUM,
                                        wt.MO_POPULATION_TRACKING, wt.PUMP_PROBE]

    def get_task(self, config, workflow_type:str, task_info: TaskInfo, 
                        dependent_tasks: Union[List[TaskInfo], None] =None ):
        
        self.check_task(task_info.name)
        
        if task_info.name == tt.COMPUTE_SPECTRUM:
            return ComputeSpectrum(config, task_info, dependent_tasks)
        if task_info.name == tt.COMPUTE_AVERAGED_SPECTRUM:
            return ComputeAvgSpectrum(config, task_info, dependent_tasks)
        if task_info.name == tt.COMPUTE_TAS:
            return PumpProbePostpro(config, task_info, dependent_tasks)
        else:
            return NwchemTask(config, task_info, dependent_tasks)

    def get_default_task_param(self, name, dependent_tasks: Union[List[TaskInfo], None] = None):
        task_default_parameter_map = {
            tt.GROUND_STATE: td.get_gs_default_param,
            tt.RT_TDDFT: td.get_rt_tddft_default_param,
            tt.COMPUTE_SPECTRUM: td.get_compute_spec_param,
            tt.MO_POPULATION: td.get_mopop_param,
        }
        self.check_task(name)

        get_func = task_default_parameter_map.get(name, dict)
        return get_func()

    def get_workflow(self, name):
        pass        
    

