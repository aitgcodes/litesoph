
from typing import Dict, List, Any
from dataclasses import dataclass, field
from litesoph.common.task_data import TaskTypes as tt                                  
from enum import Enum



class WorkflowTypes(str, Enum):
    TASK_MODE: str = 'task_mode'
    SPECTRUM: str = 'spectrum'
    AVERAGED_SPECTRUM: str = 'averaged_spectrum'
    KOHN_SHAM_DECOMPOSITION: str = 'kohn_sham_decomposition'
    MO_POPULATION_TRACKING: str = 'mo_population_tracking'
    MASKING: str = 'masking'
    PUMP_PROBE: str = 'pump_probe'



@dataclass(frozen=True)
class step:
    id: int
    block_id: int
    task_type: str
    parameters: Dict[str, str] = field(default_factory=dict)
    env_parameters: Dict[str, str] = field(default_factory=dict)


predefined_workflow = Dict[str, Any]
predefined_workflow = {
    "spectrum": {
        "name": "Spectrum",
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    {'name':'Compute Spectrum',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_SPECTRUM
                    }, 
                    {'name': 'End'}],

        "task_sequence" : [step(0 ,0, tt.GROUND_STATE),
                    step(1 ,1, tt.RT_TDDFT),
                    step(2 ,2, tt.COMPUTE_SPECTRUM)],
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '1' }
    },

    "averaged_spectrum": {
        "name": "Averaged Spectrum",
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    {'name':'Compute Spectrum',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_SPECTRUM
                    },  
                    {'name': 'Compute Averaged Spectrum',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_AVERAGED_SPECTRUM
                    },  
                    {'name': 'End'}],

        "task_sequence" : [step(0 ,0 , tt.GROUND_STATE),
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
                    step(6 ,2 ,tt.COMPUTE_SPECTRUM),
                    step(7, 3, tt.COMPUTE_AVERAGED_SPECTRUM)],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '0',
                            '3' : '0',
                            '4' : '1',
                            '5' : '2',
                            '6' : '3',
                            '7' : ['4', '5', '6'] }
    },
    "kohn_sham_decomposition": {
        "name" : "Kohn Sham Decomposition",
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    {'name':'Compute Spectrum',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_SPECTRUM
                    }, 
                    {'name':'Compute KSD',
                    'store_same_task_type': True,
                    'task_type': tt.TCM
                    }, 
                    {'name': 'End'}],

        "task_sequence" : [step(0 ,0 , tt.GROUND_STATE),
                    step(1 ,1 ,tt.RT_TDDFT,{
                                        'properties':['spectrum', 'ksd'],
                                                } ),
                    step(2 ,2 ,tt.COMPUTE_SPECTRUM),
                    step(3 ,3 ,tt.TCM)],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '1',
                            '3' : ['0', '1']}
        
    },
    "mo_population_tracking": {
        "name": "MO Population Tracking",
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    # {'name':'Compute Spectrum',
                    # 'store_same_task_type': True,
                    # 'task_type': tt.COMPUTE_SPECTRUM
                    # },  
                    {'name':'Compute MO population',
                    'store_same_task_type': True,
                    'task_type': tt.MO_POPULATION
                    }, 
                    {'name': 'End'}],

        "task_sequence" : [step(0 ,0 , tt.GROUND_STATE),
                    step(1 ,1 ,tt.RT_TDDFT,{
                                        'properties':['mo_population'],
                                                }, 
                                                {'laser': True}),
                    step(2 ,2 ,tt.MO_POPULATION),
                    ],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                        #    '2' : '1',
                            '2' : ['0', '1']}
    },
    "masking": {
        "name": "Masking", 
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    {'name':'Diople Moment Analysis',
                    'store_same_task_type': True,
                    'task_type': tt.MASKING
                    }, 
                    {'name': 'End'}],

        "task_sequence" : [step(0 ,0 , tt.GROUND_STATE),
                    step(1 ,1 ,tt.RT_TDDFT,{
                                        'properties':['spectrum'],
                                                }, 
                                                {
                                                'laser': True
                                                }),
                    step(2 ,2 ,tt.MASKING)],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '1'}
    },
    "pump_probe": {
        "name": "Pump Probe", 
        "blocks": [{'name' : 'Ground State',
                    'store_same_task_type': True,
                    'task_type': tt.GROUND_STATE
                    }, 
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    }, 
                    {'name':'Compute Spectrum',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_SPECTRUM
                    },
                    {'name':'RT TDDFT',
                    'store_same_task_type': True,
                    'task_type': tt.RT_TDDFT
                    },
                    {'name':'Compute TAS',
                    'store_same_task_type': True,
                    'task_type': tt.COMPUTE_TAS
                    },
                    {'name': 'End'}],
        "task_sequence" : [step(0 ,0 , tt.GROUND_STATE),
                    step(1, 1, tt.RT_TDDFT,{
                                            'properties':['spectrum'],
                                            }),
                    step(2, 2, tt.COMPUTE_SPECTRUM),
                    step(3 ,3 ,tt.RT_TDDFT,{
                                        'properties':['spectrum'],
                                                }, 
                                                {
                                                'laser': True
                                                }),
                    step(4 ,4 ,tt.COMPUTE_TAS)],
        
        "dependency_map": {'0' : None,
                            '1' : '0',
                            '2' : '1',
                            '3' : '0',
                            '4' : '3'}
    }
}

