
from typing import Dict, List
from litesoph.common.task import (GROUND_STATE, RT_TDDFT_DELTA, RT_TDDFT_LASER,
                                    SPECTRUM, TCM, MO_POPULATION,
                                    MASKING)
from litesoph.common.data_sturcture import WorkflowInfo , TaskInfo, factory_task_info

workflow_types = Dict[str, Dict[str, List[str]]]

workflow_types = {

    'Spectrum':{ 'ground_state': [GROUND_STATE],
                    'rt_tddft': [RT_TDDFT_DELTA],
                    'compute_spectra': [SPECTRUM]},
    'Averaged Spectrum': { 'ground_state': [GROUND_STATE],
                    'rt_tddft': [RT_TDDFT_DELTA, RT_TDDFT_DELTA, RT_TDDFT_DELTA],
                    'compute_spectra': [SPECTRUM, SPECTRUM, SPECTRUM]},    
  
   }



def get_workflow_type(Workflowinfo: WorkflowInfo) -> WorkflowInfo:
    name = Workflowinfo.name
    workflow_dict = workflow_types.get(name)
    steps = Workflowinfo.steps
    tasks = Workflowinfo.tasks
    
    steps.clear()
    tasks.clear()
    for step in workflow_dict.keys():
        steps.append(step)

    for step in steps:
        tasks[step] = [factory_task_info(task_name) for task_name in workflow_dict[step]]

    return Workflowinfo
