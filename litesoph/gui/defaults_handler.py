from litesoph.utilities.units import as_to_au

ground_state_map = {    
    "basis":{
        "lcao":"basis:lcao",
        "gaussian":"basis:gaussian"        
        },    
    "box_dim": {
        'parallelepiped':{
            "xlength":"box_length_x",
            "ylength":"box_length_y",
            "zlength":"box length_z"
            },
            'sphere':{                
                "radius":"radius"
                },
            'cylinder':{
                "xlength":"cylinder_length",
                "radius":"radius"},
            'minimum':{
                "radius":"radius"}
            },
    # "xc":"xc",
    # "basis_type":"basis_type",
    # "box_shape":"box_shape",
    # "max_itr": "max_itr",
    # "energy_conv": "energy_conv",
    # "density_conv":"density_conv",
    # "spin":"spin" ,
    # "spacing":"spacing",   
    # "vacuum": "vacuum",
    # "smearing": "smearing",
    # "mixing": "mixing",
    # "bands": "bands",
    }

def update_gs_defaults(task_default:dict):
    """Updates the default dict for GS gui widgets"""  
    
    task_param_map = ground_state_map
    basis_type = task_default.get("basis_type")
    box_shape = task_default.get("boxshape")

    gui_default_dict ={
                "xc":task_default.get('xc')}
    if basis_type is not None:
        gui_default_dict.update({
            "basis_type": task_default.get('basis_type')})
        if basis_type == "lcao":
            gui_basis_key = task_param_map["basis"]["lcao"]
            gui_default_dict.update({                                 
            str(gui_basis_key): task_default.get('basis'),
        })
        elif basis_type == "gaussian":
            gui_basis_key = task_param_map["basis"]["gaussian"]
            gui_default_dict.update({                                 
            str(gui_basis_key): task_default.get('basis'),
        })
        
    if box_shape is not None:
        gui_default_dict.update({"boxshape": box_shape})
      
    return gui_default_dict

def update_td_delta_defaults(td_default:dict):
    pol_list = td_default.get("polarization")
    
    if pol_list == [1,0,0] :
        pol_dir = "X"         
    elif pol_list == [0,1,0] :
        pol_dir = "Y"   
    elif pol_list == [0,0,1] :
        pol_dir = "Z" 

    spectrum_check = False
    ksd_check = False
    population_check = False
    if "spectrum" in td_default.get('properties'):
        spectrum_check = True
    if "ksd" in td_default.get('properties'):
        ksd_check = True
    if "mo_population" in td_default.get('properties'):
        population_check = True
    
    gui_default_dict = {
        'laser_strength': td_default.get('strength'), 
        'time_step': td_default.get('time_step'),
        'number_of_steps': td_default.get('number_of_steps'),
        'output_freq': td_default.get('output_freq'),
        "pol_dir": pol_dir,
        "spectrum": spectrum_check,
        "ksd": ksd_check,
        "mo_population": population_check,
        
    }
    return gui_default_dict

def update_td_laser_defaults(td_default:dict):
    #TODO: update widget defined input defaults to set initial set of param
    spectrum_check = False
    ksd_check = False
    population_check = False

    properties = td_default.pop('properties')
    if "spectrum" in properties:
        spectrum_check = True
    if "ksd" in properties:
        ksd_check = True
    if "mo_population" in properties:
        population_check = True
    
    gui_default_dict = {
        'time_step': td_default.get('time_step'),
        'number_of_steps': td_default.get('number_of_steps'),
        'output_freq': td_default.get('output_freq'),
        "spectrum": spectrum_check,
        "ksd": ksd_check,
        "mo_population": population_check,        
    }
    if td_default.get("field_type", None) is not None:
        gui_default_dict['field_type'] = td_default.get('field_type')
    if td_default.get('exp_type', None) is not None:
        gui_default_dict['exp_type'] = td_default.get('exp_type')    
    return gui_default_dict

def update_laser_defaults(laser_default:dict):
    """updates widget defined input defaults to set initial set of param"""
    mask_axis_name_var_map = {
            "0": "X",
            "1": "Y",
            "2": "Z"}
    gui_default_dict = {
        'log_val': laser_default.get('inval'),
        'fwhm': laser_default.get('fwhm'),
        'freq': laser_default.get('frequency'),
    }
    masking_default = {}

    pump_probe_tag = laser_default.get('tag')
    laser_type = laser_default.get('type')
    time_origin = laser_default.get('tin') / as_to_au
    strength = laser_default.get('strength')
    if pump_probe_tag is not None:
        gui_default_dict.update({'pump-probe_tag': pump_probe_tag})
    if laser_type == "delta":
        gui_default_dict.update({'laser_type': "Delta Pulse"})
    elif laser_type == "gaussian":
        gui_default_dict.update({'laser_type': "Gaussian Pulse"})

    pol_dir = laser_default.get('polarization')
    gui_default_dict.update({"pol_dir": pol_dir})

    if pump_probe_tag == "Probe":
        gui_default_dict.update({"time_origin:probe": time_origin})
    else:  
        gui_default_dict.update({"time_origin": time_origin})

    # TODO: Remove this condition for strength
    if laser_type == "delta":
       gui_default_dict.update({"delta_strength": strength})
    else:
        gui_default_dict.update({"laser_strength": strength})

    mask = laser_default.get('mask')    
    if mask is None:
        masking_default ={"masking": False}
    else:
        if isinstance(mask, dict):            
            type = mask.get("Type")
            boundary = mask.get("Boundary")
            masking_default.update(
                {
                "masking": True,
                "mask_type":type,
                "boundary_type": boundary,
                }
            )

            if boundary == "Smooth":
                masking_default.update({"r_sig": mask.get("Rsig")})

            if type == "Plane":
                axis_var = str(mask.get("Axis"))
                masking_default.update({"mask_plane:axis": mask_axis_name_var_map.get(axis_var),
                                        "mask_plane:origin": mask.get("X0")
                                    })
            elif mask.get("Type") == "Sphere":
                centre = mask.get("Centre")
                masking_default.update({
                    "mask_sphere:radius": mask.get("Radius"),
                    "mask_sphere:origin_x": centre[0],
                    "mask_sphere:origin_y": centre[1],
                    "mask_sphere:origin_z": centre[2],
                })

    gui_default_dict.update(masking_default)
    return gui_default_dict