
GROUND_STATE = 'ground_state'
RT_TDDFT = 'rt_tddft'
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
        "boxshape": None,
        "box_dim" : None,        
        "max_iter":300,
        "energy_conv": 1e-6 ,
        "density_conv": 1e-6 ,
        "smearing_fun": None,
        "smearing_width": None,
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

task_dependencies_map = {
    GROUND_STATE: None,
    RT_TDDFT: [GROUND_STATE],
    SPECTRUM: [{RT_TDDFT:{'delta_kick': True,
                            "spectrum" : True}}],
    TCM: [{RT_TDDFT: {"ksd": True}}],
    MO_POPULATION: [{RT_TDDFT: {"mo_population": True}}],
    MASKING: [{RT_TDDFT: {"laser": True,
                            "masking": True}}]
}


def check_properties_dependencies(task_name, task) -> tuple:
    
    if task_name == SPECTRUM:
        laser = task.param.get('laser', None)
        if laser:
            return (False, "spectrum only works with delta kick.")
        if "spectrum" not in task.param['properties']:
            return (False, "spectrum was not choosen in TD simulation")

    if task_name == TCM:
        if 'ksd' not in task.param['properties']:
            return (False, "ksd was not choosen in TD simulation")

    if task_name == MO_POPULATION:
        if "mo_population" not in task.param['properties']:
            return (False, "mo_population was not choosen in TD simulation")

    if task_name == MASKING:
        laser = task.param.get('laser', None)
        masking = task.param.get('masking', None)
        if not laser or not masking:
            return (False, "masking was not choosen in TD simulation")

    return (True, '')