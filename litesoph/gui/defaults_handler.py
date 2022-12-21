
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
    pass