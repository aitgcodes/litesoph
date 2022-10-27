
GROUND_STATE = 'ground_state'
RT_TDDFT_DELTA = 'rt_tddft_delta'
RT_TDDFT_LASER = 'rt_tddft_laser'
SPECTRUM = 'spectrum'
TCM = 'tcm'
MO_POPULATION = 'mo_population'
MASKING = 'masking'

default_ground_state_parameters = { 
        "xc":None,               
        "basis_type": None,  
        "basis": None,  
        "bands": 0,
        "spin": None,
        "spacing": None,
        "vacuum": None,
        "box": {},        
        "max_iter":300,
        "energy_conv": 1e-6 ,
        "density_conv": 1e-6 ,
        "smearing": None,
        "mixing": None,
        
}

default_rt_tddft_parameters = {
    'strength': 1e-5,
    'polarization': None,
    'time_step': None,
    'number_of_steps': None,
    'output_freq': 1,
    'properties': ['spectrum'],
    'laser': None,
    'masking': None
}