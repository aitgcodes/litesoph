from enum import Enum



class TaskTypes(str, Enum):
    GROUND_STATE: str = 'ground_state'
    RT_TDDFT: str = 'rt_tddft'
    COMPUTE_SPECTRUM: str = 'spectrum'
    COMPUTE_AVERAGED_SPECTRUM: str = 'compute_average_spectrum'
    TCM: str = 'tcm'
    MO_POPULATION: str = 'mo_population'
    MASKING: str = 'masking'
    COMPUTE_TAS: str = 'compute_tas'

class TaskParamDB:

    @staticmethod
    def get_template_task_param(self, name):
        pass


template_ground_state_parameters = {
        'restart' : True, 
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

template_rt_tddft_parameters = {
    'restart' : True,
    'strength': 1e-5,
    'polarization': None,
    'time_step': None,
    'number_of_steps': None,
    'output_freq': 1,
    'properties': ['spectrum'],
    'laser': None,
    'masking': None
}

template_compute_spectrum_parameters = {
            'delta_e': 0.05,
            'e_max':30.0,
            'e_min': 0.0, 
            'width': 0.1,      
        }

task_dependencies_map = {
    TaskTypes.GROUND_STATE: None,
    TaskTypes.RT_TDDFT: [TaskTypes.GROUND_STATE],
    TaskTypes.COMPUTE_SPECTRUM: [{TaskTypes.RT_TDDFT:{'delta_kick': True,
                            "spectrum" : True}}],
    TaskTypes.TCM: [TaskTypes.GROUND_STATE, {TaskTypes.RT_TDDFT: {"ksd": True}}],
    TaskTypes.MO_POPULATION: [TaskTypes.GROUND_STATE, {TaskTypes.RT_TDDFT: {"mo_population": True}}],
    TaskTypes.MASKING: [{TaskTypes.RT_TDDFT: {"laser": True,
                            "masking": True}}]
}


def check_properties_dependencies(task_name, task) -> tuple:
    
    if task_name == TaskTypes.COMPUTE_SPECTRUM:
        laser = task.param.get('laser', None)
        if laser:
            return (False, "spectrum only works with delta kick.")
        if "spectrum" not in task.param['properties']:
            return (False, "spectrum was not chosen in TD simulation")

    if task_name == TaskTypes.TCM:
        laser = task.param.get('laser', None)
        if laser and task.engine != 'gpaw':
            return (False, "TCM only works with delta kick. However support for this in gpaw is there.")
        if 'ksd' not in task.param['properties']:
            return (False, "TCM was not chosen in TD simulation")

    if task_name == TaskTypes.MO_POPULATION:
        laser = task.param.get('laser', None)
        if laser and task.engine != 'gpaw':
            return (False, "Mo population only works with delta kick. However support for this in gpaw is there.")
        if "mo_population" not in task.param['properties']:
            return (False, "Mo population was not chosen in TD simulation")

    if task_name == TaskTypes.MASKING:
        laser = task.param.get('laser', None)
        # masking = task.param.get('masking', None)
        if not laser:
            return (False, "masking was not chosen in TD simulation")

    return (True, '')
