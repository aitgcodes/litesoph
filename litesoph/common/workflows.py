
from typing import Dict, List
from litesoph.common.task_data import (GROUND_STATE, RT_TDDFT,
                                    SPECTRUM, TCM, MO_POPULATION,
                                    MASKING)
from litesoph.common.data_sturcture import WorkflowInfo , TaskInfo, factory_task_info

workflow_types = Dict[str, callable]



workflows = {
    'Spectrum': ['Ground State', 'RT TDDFT', 'Compute Spectrum'] ,
    'Averaged Spectrum' : ['Ground State', 'RT TDDFT', 'Compute Spectrum'],
    'Kohn Sham Decompostion' : ['Ground State', 'RT TDDFT', 'Compute Spectrum'],
    'MO Population Tracking' : ['Ground State', 'RT TDDFT', 'Compute Spectrum'],
}
workflow_steps = {
    'Spectrum' : ['Ground State', 'RT TDDFT', 'Compute Spectrum']
}


def get_spectrum_workflow(Workflowinfo: WorkflowInfo):
    Workflowinfo.name = 'Spectrum'
    steps = Workflowinfo.steps
    tasks = Workflowinfo.tasks
    
    steps.clear()
    tasks.clear()

    gs_task = factory_task_info(GROUND_STATE)
    td_task = factory_task_info(RT_TDDFT)
    spec_task = factory_task_info(SPECTRUM)
    dependencies = {
        gs_task.uuid: [],
        td_task.uuid: [gs_task.uuid],
        spec_task.uuid: [td_task.uuid]
    }
    steps.update({
        'Ground State': [gs_task.uuid],
        'RT TDDFT': [td_task.uuid],
        'Compute Spectrum': [spec_task.uuid]
    })
    Workflowinfo.dependencies_map.update(dependencies)
    for task in [gs_task, td_task, spec_task]:
        Workflowinfo.tasks.append(task)
    
    

workflow_types = {

    'Spectrum': get_spectrum_workflow,

   }