import copy
from typing import List, Dict, Any, Union
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import TaskNotImplementedError, InputError
from litesoph.common.task_data import TaskTypes as tt                    
from litesoph.common.workflows_data import WorkflowTypes as wt     
from litesoph.common.engine_manager import EngineManager
from litesoph.engines.octopus.octopus_task import OctAveragedSpectrum, OctopusTask
from litesoph.engines.octopus.format_oct import calc_td_range
from litesoph.engines.octopus import task_data as td
from litesoph.engines.octopus.octopus_task import PumpProbePostpro

class OCTOPUSManager(EngineManager):
    """Base class for all the engine."""

    implemented_tasks: List[str] = [tt.GROUND_STATE, tt.RT_TDDFT, tt.COMPUTE_SPECTRUM,tt.COMPUTE_AVERAGED_SPECTRUM,
                                    tt.TCM, tt.MASKING, tt.MO_POPULATION, tt.COMPUTE_TAS]

    implemented_workflows: List[str] = [wt.SPECTRUM, wt.AVERAGED_SPECTRUM, wt.KOHN_SHAM_DECOMPOSITION, 
                                        wt.MO_POPULATION_TRACKING, wt.PUMP_PROBE]

    def get_task(self, config, workflow_type:str, task_info: TaskInfo, 
                        dependent_tasks: Union[List[TaskInfo], None] =None,
                        ):
        self.check_task(task_info.name)

        self.validate_workflow_task(workflow=workflow_type,task_info=task_info)
    
        if task_info.name == tt.COMPUTE_AVERAGED_SPECTRUM:
            return OctAveragedSpectrum(config, task_info, dependent_tasks)
        if task_info.name == tt.COMPUTE_TAS:
            return PumpProbePostpro(config, task_info, dependent_tasks)
        else:
            return OctopusTask(config, task_info, dependent_tasks)
    
    def get_default_task_param(self, name, dependent_tasks: Union[List[TaskInfo], None]):
        task_default_parameter_map = {
            tt.GROUND_STATE: td.get_gs_default_param,
            tt.RT_TDDFT: td.get_rt_tddft_default_param,
            tt.COMPUTE_SPECTRUM: td.get_compute_spec_param,
            tt.TCM: td.get_tcm_param,
            tt.MO_POPULATION: td.get_mo_pop_param
        }
        self.check_task(name)

        get_func = task_default_parameter_map.get(name, dict)
        if name == tt.RT_TDDFT:
            gs_info = dependent_tasks[0]
            if gs_info:
                gs_spacing = gs_info.param.get('spacing')
            
            task_default = get_func()
            task_default.update({'time_step': calc_td_range(gs_spacing)})
            return task_default
        else:
            return get_func()

    def get_workflow(self, name):
        pass
    
    def validate_workflow_task(self, workflow, task_info: TaskInfo):
        """Method to handle validation of task in context of workflow"""
        
        task = task_info.name
        param = task_info.param
        if workflow in [wt.KOHN_SHAM_DECOMPOSITION, wt.MO_POPULATION_TRACKING]:
            if task == tt.GROUND_STATE:
                gs_param = copy.deepcopy(param)
                extra_states = int(gs_param.get('bands'))  
                if extra_states <= 0:
                    raise InputError(f'Expected non zero value for Extra States.')

