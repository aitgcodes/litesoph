
from typing import Dict, List
from litesoph.common.task import (GROUND_STATE, RT_TDDFT_DELTA, RT_TDDFT_LASER,
                                    SPECTRUM, TCM, MO_POPULATION,
                                    MASKING)


workflow_types = Dict[str, List[str]]

workflow_types = {

    'Ground State': [GROUND_STATE],
    'Spectrum': [GROUND_STATE, RT_TDDFT_DELTA, SPECTRUM],    
    'Time Dependent Calculation': [GROUND_STATE, RT_TDDFT_LASER],
    'Kohn Sham Decomposition': [GROUND_STATE, RT_TDDFT_DELTA, TCM],
    'MO Population Tracking': [GROUND_STATE, RT_TDDFT_DELTA, MO_POPULATION],
    'Masking' : [GROUND_STATE, RT_TDDFT_LASER, MASKING]
  
   }
