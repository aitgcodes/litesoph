from litesoph.common.data_sturcture.data_types import DataTypes as DT
from litesoph.common.task_data import template_ground_state_parameters

gpaw_gs_param_data ={ 
        "xc": {'type':DT.string, 'values':["LDA",
                                            "PBE",
                                            "PBE0",
                                            "PBEsol",
                                            "BLYP",
                                            "B3LYP",
                                            "CAMY-BLYP",
                                            "CAMY-B3LYP"], 
                                            'default_value': 'LDA'},               
        "basis_type": {'type':DT.string, 'values':['lcao',
                                                     'fd', 
                                                     'pw'], 
                                                     'default_value': 'lcao'},  
        "basis": {'type':DT.string, 'metadata':{'basis_type': {'lcao' : {'values':["dzp","sz","dz","szp","pvalence.dz"], 'default_value': 'dzp'},
                                                'fd' : {'default_value': None},
                                                'pw': {'default_value': None}}}},  
        "bands": 0,
        "spin": None,
        "spacing": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
        "vacuum": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
        "boxshape": {'type':DT.string, 'values':['parallelepiped'], 'default_value':'parallelepiped'},
        "box_dim" : None,        
        "max_iter":{'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
        "energy_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7} ,
        "density_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6} ,
        "smearing_fun":{'type':DT.string, 'values':["","improved-tetrahedron-method","tetrahedron-method","fermi-dirac","marzari-vanderbilt"], 'default_value': ''},
        "smearing_width": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.05},
        "mixing": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.03},
        
}


def get_gs_default_param():
    return { 
        "xc":"PBE",               
        "basis_type": "lcao",  
        "basis": "dzp",  
        "bands": 0,
        "spin": 'unpolarized',
        "spacing": 0.3,
        "vacuum": 6,
        "boxshape": "parallelepiped",
        "box_dim" : None,        
        "max_iter":300,
        "energy_conv": 1e-6 ,
        "density_conv": 1e-6 ,
        "smearing_fun": '',
        "smearing_width": 0.0,
        "mixing": None,
        
    }


def get_rt_tddft_default_param():
    return {
    'strength': 1e-5,
    'polarization': [1,0,0],
    'time_step': 10,
    'number_of_steps': 1000,
    'output_freq': 1,
    'properties': ['spectrum'],
    'laser': None,
    'masking': None
}

def get_compute_spec_param():
    return{
            'delta_e': 0.05,
            'e_max':30.0,
            'e_min': 0.0, 
            'width': 0.1,      
        }


def get_tcm_param():
    return{
            'frequency_list' : [],
            'axis_limit': 3,
    } 

def get_mopop_param():
    return{
        'num_occupied_mo': None,
        'num_unoccupied_mo': None,
    }

def get_masking_analysis():
    return{
        'region':None,
        'direction':None,
        'envelope':None,
    }
