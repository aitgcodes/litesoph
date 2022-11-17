
from typing import Dict, List, Any
from dataclasses import dataclass, field
from litesoph.common.task_data import TaskTypes as tt                                  
from enum import Enum



class WorkflowTypes(str, Enum):
    SPECTRUM: str = 'spectrum'
    AVERAGED_SPECTRUM: str = 'averaged_spectrum'
    KOHN_SHAM_DECOMPOSITION: str = 'kohn_sham_decomposition'
    MO_POPULATION_TRACKING: str = 'mo_population_tracking'



@dataclass(frozen=True)
class step:
    id: int
    block_id: int
    task_type: str
    env_parameters: Dict[str, str] = field(default_factory=dict)


predefined_workflow = Dict[str, Any]
predefined_workflow = {
    "spectrum": {
        "blocks": ['Ground State', 'RT TDDFT', 'Compute Spectrum'],
        "steps" : [step(0 ,0, tt.GROUND_STATE),
                    step(1 ,1, tt.RT_TDDFT),
                    step(2 ,2, tt.COMPUTE_SPECTRUM)],
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '1' }
    },

    "averaged_spectrum": {
        "blocks": ['Ground State', 'RT TDDFT', 'Compute Spectrum'],
        "steps" : [step(0 ,0 , tt.GROUND_STATE),
                    step(1 ,1 ,tt.RT_TDDFT, {
                                        'polarization':[1,0,0],
                                                }),
                    step(2 ,1 ,tt.RT_TDDFT, {
                                        'polarization': [0,1,0],
                                                }),
                    step(3 ,1 ,tt.RT_TDDFT, {
                                        'polarization': [0,0,1],
                                                }),
                    step(4 ,2 ,tt.COMPUTE_SPECTRUM),
                    step(5 ,2 ,tt.COMPUTE_SPECTRUM),
                    step(6 ,2 ,tt.COMPUTE_SPECTRUM)],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '0',
                            '3' : '0',
                            '4' : '1',
                            '5' : '2',
                            '6' : '3' }
    },
    "kohn_sham_decomposition": {
        "blocks": ['Ground State', 'RT TDDFT', 'Compute Spectrum', 'Compute KSD', 'Plot'],
        
    },
    "mo_population_tracking": {
        "blocks": ['Ground State', 'RT TDDFT', 'Compute Spectrum', 'Compute MO population']
        
    },

}

