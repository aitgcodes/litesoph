from litesoph.common.data_sturcture.data_types import DataTypes as DT



nwchem_gs_param_data = {
            "basis_type" : {'type':DT.string, 'values':['gaussian'], 'default_value': 'gaussian'},
            'xc' : {'type':DT.string, 'values':["PBE96","PBE0","B3LYP","PW91", "BP86", "BP91","BHLYP","M05","M05-2X","M06-HF","M08-SO","M011","CAM-B3LYP","LC-BLYP","LC-PBE","LC-wPBE","HSE03","HSE06"], 'default_value': "PBE0"},
            'basis' : {'type':DT.string, 'values':["6-31G","STO-2G","STO-3G","STO-6G","3-21G","3-21G*","6-31G*","6-31G**","6-311G","6-311G*","6-311G**","cc-pVDZ","aug-cc-pvtz"], 'default_value': "6-31G"},
            'max_iter' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
            'energy_conv' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density_conv' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
        }


nwchem_xc_map = {
            'B3LYP'     :'b3lyp',
            'PBE0'      :'pbe0',
            'PBE96'     :'xpbe96 cpbe96',
            'BHLYP'     :'bhlyp',
            'PW91'      :'xperdew91 perdew91',
            'BP86'      :'becke88 perdew86',
            'BP91'      :'becke88 perdew91',
            'BLYP'      :'becke88 lyp',
            'M05'       :'m05',
            'M05-2X'    :'m05-2x',
            'M06'       :'m06',
            'M06-HF'    :'m06-hf',
            'M08-SO'    :'m08-so',
            'M11'       :'m11',
            'CAM-B3LYP' :'xcamb88 1.00 lyp 0.81 vwn_5 0.19 hfexch 1.00 \n cam 0.33 cam_alpha 0.19 cam_beta 0.46',
            'LC-BLYP'   :'xcamb88 1.00 lyp 1.0 hfexch 1.00 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
            'LC-PBE'    :'xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.0 cam_beta 1.0',
            'LC-wPBE'   :'xwpbe 1.00 cpbe96 1.0 hfexch 1.00 \n cam 0.4 cam_alpha 0.00 cam_beta 1.00',
            'CAM-PBE0'  :'xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.25 cam_beta 0.75',
            'rCAM-B3LYP':'xcamb88 1.00 lyp 1.0 vwn_5 0. hfexch 1.00 becke88 nonlocal 0.13590 \n cam 0.33 cam_alpha 0.18352 cam_beta 0.94979',
            'HSE03'     :'xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
            'HSE06'     :'xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.11 cam_alpha 0.0 cam_beta 1.0',
}


def get_gs_default_param():
    return { 
        "xc":"PBE96",               
        "basis_type": 'gaussian',  
        "basis": "6-31G",  
        "max_iter":300,
        "energy_conv": 1e-6 ,
        "density_conv": 1e-6 ,        
    }


def get_rt_tddft_default_param():
    return {
    'strength': 1e-5,
    'polarization': [1,0,0],
    'time_step': 2.4,
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
        }


def get_mopop_param():
    return{
        'num_occupied_mo': None,
        'num_unoccupied_mo': None,
    }
