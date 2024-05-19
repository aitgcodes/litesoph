# Methods for converting generalised input parameters to Octopus input variables
# Includes:
# a) Mapping for key to value pair
# b) Helper methods to assign/compute values from dependent variable

import copy
import numpy as np
from litesoph.common.task import InputError
from litesoph.utilities.units import as_to_au

# xc_pseudo maps for Octopus
xc_pseudo ={
        "lda":["lda_x + lda_c_pz_mod", "standard"],
        "pbe":["gga_x_pbe + gga_c_pbe", "pseudodojo_pbe"],
        "pbe0":["hyb_gga_xc_pbeh", "pseudodojo_pbe"],
        "pbesol":["hyb_gga_xc_pbe_sol0", "pseudodojo_pbe"],
        # "blyp":["gga_xc_oblyp_d", None],
        # "b3lyp":["hyb_gga_xc_b3lyp", None],
        # "camy-blyp":["hyb_gga_xc_camy_blyp", None],
        
    }
# ExptFeatures check
pseudo_expt = {'yes' :["pseudodojo_lda","hscv_lda","pseudodojo_lda_stringent",
                            "pseudodojo_pbe","pseudodojo_pbe_stringent","pseudodojo_pbesol","pseudodojo_pbesol_stringent","sg15", "hscv_pbe"],
                'no':["standard", "hgh_lda_sc","hgh_lda"]}

def get_gs_dict(gui_inp:dict, geom_file=None):
    key2key = {
        "XYZCoordinates":"XYZCoordinates",
        "spacing": "Spacing",
        "max_iter": "MaximumIter",
        "energy_conv": "ConvEnergy",
        "density_conv": "ConvAbsDens",
        "smearing":"Smearing",
        "mixing":"Mixing",
        "bands" : "ExtraStates",
        "spin": "SpinComponents",
        # "restart_steps": "RestartWriteInterval"
        }

    _dict = {
        "CalculationMode": "gs",
        "UnitsOutput": "ev_angstrom",
        "FromScratch": gui_inp.get("FromScratch","yes"),        
    }

    boxshape = gui_inp.get("boxshape")
    box_dim = gui_inp.get("box_dim")
    if box_dim is not None:
        select_box = True
    else:
        select_box = False
    xc = gui_inp.get("xc")
    copy_inp = copy.deepcopy(gui_inp)
    
    for i, (key, value) in enumerate(gui_inp.items()):
        if value is not None:
            if key in key2key.keys():
                _key2key_dict = dict(
                [(key2key.get(key), value)]) 
                _dict.update(_key2key_dict)
            else:
                if key == "boxshape":
                    sim_box = get_box_dim(geom_file,_boxshape= boxshape,
                                    _from_vacuum= not select_box,
                                **copy_inp)
                    _dict.update(sim_box)               
                if key == "xc":
                    try:
                        xc_pseudo_dict = get_xc_pseudo(xc_str=xc)
                        _dict.update(xc_pseudo_dict) 
                    except InputError as e:
                        raise e
                        
    spacing_value = _dict.get("Spacing")
    _dict.update({"Spacing": str(spacing_value)+'*angstrom'})
    return _dict

def get_box_dim(geom_file,_boxshape:str,_from_vacuum=False, **kwargs):
    if _from_vacuum :
        _vacuum = kwargs.get('vacuum', 6)
        if geom_file is not None:
            # Taking geom file from arguments
            _geom_file = geom_file
        else:
            try:
                _geom_file = kwargs.get("XYZCoordinates")
            except:
                raise KeyError("Geometry file not found")
        _cell = get_box_dim_from_vacuum(_geom_file,_vacuum, _boxshape)
        
        if _boxshape == "parallelepiped":
            _sim_box = {
                        "BoxShape":{"name":_boxshape,
                                    "param":{'LSize':[[
                                        str(_cell["lx"]/2)+'*angstrom',
                                        str(_cell["ly"]/2)+'*angstrom',
                                        str(_cell["lz"]/2)+'*angstrom']]}}
                            }
        elif _boxshape == "cylinder":
            _sim_box = {
                        "BoxShape":{"name":_boxshape,
                                    "param":{
                                        'Xlength':str(_cell["lx"]/2)+'*angstrom',
                                        'Radius':str(_cell["radius"])+'*angstrom'}
                                            }}
        elif _boxshape in ["sphere","minimum"]:
            _sim_box = {
                        "BoxShape":{"name":_boxshape,
                                    "param":{
                                        'Radius':str(_cell["radius"])+'*angstrom'}
                                            }}
        return _sim_box

    elif not _from_vacuum:
        box_dict = kwargs.get('box_dim', None)
        assert box_dict is not None

        if _boxshape in ['minimum','sphere']:     
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'Radius':str(box_dict.get("radius"))+'*angstrom'}}}
            return _sim_box 
        elif _boxshape == 'cylinder':
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'Radius':str(box_dict.get("radius"))+'*angstrom',
                                'Xlength':str(box_dict.get("cylinder_length")/2)+'*angstrom'}}}
            return _sim_box 
        elif _boxshape == 'parallelepiped':
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'LSize':[[
                                str(box_dict.get("box_length_x")/2)+'*angstrom',
                                str(box_dict.get("box_length_y")/2)+'*angstrom',
                                str(box_dict.get("box_length_z")/2)+'*angstrom']]}}} 
            return _sim_box                 

def get_xc_pseudo(xc_str:str):
    _xc = xc_str.lower()
    if _xc in xc_pseudo.keys():
        xc = xc_pseudo.get(_xc)[0]
        pseudo = xc_pseudo.get(_xc)[1]
        for key, values in pseudo_expt.items():
            if pseudo in values:
                expt = key
                break
        xc_dict = {
        "ExperimentalFeatures":expt,
        "XCFunctional": xc,
        "PseudopotentialSet" : pseudo,    
        }
        return xc_dict
    else:
        raise InputError(f'XC not assigned for:{xc_str}')
    
    
#---------------------------------------------------------------------------------------------------------------
pol_list2dir = [([1,0,0], 1),
                ([0,1,0], 2),
                ([0,0,1], 3)]

property_dict = {
    "default": ["energy", "multipoles"],
    "ksd": ["td_occup"],
    "mo_population": ["td_occup"]}
    #"induced_density" : ["density"]}

td_output = ["energy", "multipoles","td_occup"]
output_dict = {
    "density": {"output_format": "cube",
                "output_interval": 50,
                },
    "potential":{"output_format": "cube",
                "output_interval": 50,
                },}
output = list(output_dict.keys())

def get_oct_kw_dict(inp_dict:dict, task_name:str):
    """ Acts on the input dictionary to return Octopus specifc keyword dictionary
        inp_dict: generic input parameters dictionary 
        task_name: defined task_name
    """   

    if 'rt_tddft' in task_name:
        _dict = get_td_dict(inp_dict)
    elif task_name == 'spectrum':
        _dict = get_spectrum_dict(inp_dict)
    return _dict

def get_td_dict(inp_dict):   
    t_step = inp_dict.pop('time_step')
    property_list = inp_dict.pop('properties')
    output_freq = inp_dict.pop('output_freq')
    laser = inp_dict.pop('laser', None)
    _dict ={
    'CalculationMode': 'td', 
    'TDPropagator': 'aetrs',
    'TDMaxSteps': inp_dict.pop('number_of_steps'),
    'TDTimeStep':round(t_step*as_to_au, 3),
    'TDOutputComputeInterval': output_freq,
    # "RestartWriteInterval": inp_dict.get("restart_steps"),
    }

    # TDOutput & Output Block 
    # from properties to extract
    _list1 = []
    _list2 = []
    td_out_list = []
    output_list = []
    for item in property_list:  
        copy_output_dict = copy.deepcopy(output_dict)      
        property_keys = property_dict.get(item, ["energy", "multipoles"])
        for property in property_keys:
            if property in td_output:
                _list1.append(property)
            elif property in output:
                _list2.append(property)
                copy_output_dict.update({
                    property:{
                        "output_format": "cube",
                        "output_interval": output_freq,
                    }
                })

    td_list = list(set(_list1))
    out_list = list(set(_list2))
    
    td_out_list = [[item] for item in td_list]
    output_list = [[item, 
                    "'output_format'", 
                    copy_output_dict[item].get("output_format"),
                    "'output_interval'",
                    output_freq ,
                    ] 
                    for item in out_list]
    if len(td_out_list) > 0:
        _dict.update({'TDOutput': td_out_list})
    if len(output_list) > 0:
        _dict.update({'Output': output_list})
     
    # # TD Outputs
    # _list = []
    # td_out_list = []
    # for item in property_list:
    #     td_key = property_dict.get(item, ["energy", "multipoles"])
    #     if td_key:
    #         _list.extend(td_key)
    # td_list = list(set(_list))
    # for item in td_list:
    #     td_out_list.append([item])
    # _dict.update({'TDOutput': td_out_list})
    
    # TD External Fields
    if laser:
        # To handle multiple lasers
        # State Preparation/Pump-Probe
        assert isinstance(laser, list)
        _dict2update = {'task': 'rt_tddft_laser'}
            
        td_functions_list = []
        td_ext_fields_list = []
        for i, laser_inp in enumerate(laser):
            laser_type = laser_inp.get("type")
            pol_list = laser_inp.get('polarization')    

            if laser_type == "delta":
                # Get dict for delta pulse
                # pol_list = laser_inp.get('polarization') 
                # if isinstance(pol_list, list):      
                #     for item in pol_list2dir:
                #         if item[0] == pol_list:
                #             pol_dir = item[1]
                # _dict2update.update({
                #     "TDDeltaStrength": laser_inp.get('strength'),
                #     "TDPolarizationDirection": pol_dir,
                #     "TDDeltaKickTime":laser_inp.get('time0'),
                # })
                laser_str = "laser"+str(i)
                laser_inp['sigma'] = .001
                # laser_inp['frequency']
                td_functions_list.append(
                    get_td_function(
                        laser_dict = laser_inp,
                        laser_type = laser_type,
                        td_function_name = laser_str
                    )
                )
                td_ext_field = ['electric_field',
                            pol_list[0],pol_list[1],pol_list[2],
                            '0'+"*eV",
                            str('"'+laser_str+'"')
                            ]
                td_ext_fields_list.append(td_ext_field)
                _dict2update.update({
                    'TDFunctions': td_functions_list,
                    'TDExternalFields': td_ext_fields_list
                        })
            else:
                # for laser other than delta pulse
                # Construct the td_functions, ext fields block
                laser_str = "laser"+str(i)
                td_functions_list.append(get_td_function(laser_dict=laser_inp,
                                        laser_type= laser_type,
                                        td_function_name=laser_str
                                        ))
                td_ext_field = ['electric_field',
                            pol_list[0],pol_list[1],pol_list[2],
                            str(laser[i]['frequency'])+"*eV",
                            str('"'+laser_str+'"')
                            ]
                td_ext_fields_list.append(td_ext_field)
                _dict2update.update({
                    'TDFunctions': td_functions_list,
                    'TDExternalFields': td_ext_fields_list
                        })
    else:
        # Delta Kick for spectrum calculation
        pol_list = inp_dict.pop('polarization')
        if isinstance(pol_list, list):      
            for item in pol_list2dir:
                if item[0] == pol_list:
                    pol_dir = item[1]
        _dict2update = {
            'TDDeltaStrength':inp_dict.get('strength'),
            'TDPolarizationDirection':pol_dir,
    }
    _dict.update(_dict2update)
    return _dict

def get_td_function(laser_dict:dict,laser_type:str,td_function_name:str = "envelope_gauss"):
    laser_td_function_map = {
        "gaussian": "tdf_gaussian",
        "delta"   : "tdf_gaussian" # Currently using gaussian as delta pulse
    }
    # td_function block for gaussian pulse
    td_func = [str('"'+td_function_name+'"'),
                    laser_td_function_map.get(laser_type),
                    laser_dict.get('strength'),
                    laser_dict['sigma'],
                    laser_dict['time0']
                    ]
    return td_func

def get_spectrum_dict(inp_dict:dict):
    delta_e = inp_dict.pop('delta_e')
    e_max = inp_dict.pop('e_max')
    e_min = inp_dict.pop('e_min') 
    
    _dict = {
    "UnitsOutput": 'eV_angstrom',
    "PropagationSpectrumEnergyStep": str(delta_e)+"*eV",
    "PropagationSpectrumMaxEnergy": str(e_max)+"*eV",
    "PropagationSpectrumMinEnergy": str(e_min)+"*eV"
    }
    return _dict

#----------------------------------------------------------------------------------------------

def get_box_dim_from_vacuum(geom_file, vacuum:float,box_shape):
    from ase.io import read
    atoms = read(geom_file)
    
    if box_shape == "parallelepiped":
        atoms.center(vacuum=vacuum)
        cell_param = atoms.cell.cellpar()
        lx =round(cell_param[0], 2)
        ly =round(cell_param[1], 2)
        lz =round(cell_param[2], 2)
        box_dict = {
            "lx":lx,
            "ly":ly,
            "lz":lz
        }

    elif box_shape == "cylinder":
        atoms.center(vacuum=vacuum)
        cell_param = atoms.cell.cellpar()
        lx =round(cell_param[0], 2)
        r = max(cell_param[1], cell_param[2])/2
        box_dict = {"lx":lx,
                    "radius":round(r, 2)}

    elif box_shape == "sphere":
        disp = atoms.get_all_distances()
        radius = np.ndarray.max(disp)/2 + vacuum
        box_dict = {"radius":round(radius, 2)}

    elif box_shape == "minimum":
        box_dict = {"radius":vacuum}

    return box_dict

def calc_td_range(spacing:float):
    """ spacing:float = Grid-spacing in angstrom\n
    calculates max limit(in as) for time step specific to Octopus engine
    """

    from litesoph.utilities.units import ang_to_au, au_to_as
    h = spacing*ang_to_au
    dt = 0.0426-0.207*h+0.808*h*h
    max_dt_as = round(dt*au_to_as, 2)
    return max_dt_as

def convert_unit():
    pass
