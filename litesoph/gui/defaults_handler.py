
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

def update_gui_dict_defaults(task_type:str, task_default:dict):
    """Updates the default dict for gui widgets"""         

    gui_default_dict = {}
    if task_type == "ground_state":
        print(task_type)
        task_param_map = ground_state_map
        basis_type = task_default.get("basis_type")
        box_shape = task_default.get("boxshape")
        if basis_type is not None:
            if basis_type == "lcao":
                gui_basis_key = task_param_map["basis"]["lcao"]
            elif basis_type == "gaussian":
                gui_basis_key = task_param_map["basis"]["gaussian"]
        if box_shape is not None:
            ls_box_dim = task_default.get("box_dim")

            box_dict = {}
            for key, value in ls_box_dim.items():
                if key in ls_box_dim.keys():
                    _key2key_dict = dict(
                    [(ls_box_dim.get(key), value)]) 
                    box_dict.update(_key2key_dict)
                
        gui_default_dict ={
            "xc":task_default.get('xc'),  
            "basis_type": task_default.get('basis_type'),                                  
            str(gui_basis_key): task_default.get('basis'),  
            "spacing": task_default.get('spacing'),                           
            "spin": task_default.get('spin'),
            "boxshape": task_default.get('boxshape'),
            "select_box": False,
            "vacuum": task_default.get('vacuum'),
            "max_itr":task_default.get('max_iter'),
            "energy_conv": task_default.get('energy_conv'),
            "density_conv": task_default.get('density_conv'),
            "smearing": task_default.get('smearing'),
            "mixing": task_default.get('mixing'),
            "bands": task_default.get('bands'),
        }

    elif task_type == "tddft_delta":
        spectrum_check = False
        ksd_check = False
        population_check = False
        if "spectrum" in task_default.get('properties'):
            spectrum_check = True
        elif "ksd" in task_default.get('properties'):
            ksd_check = True
        elif "mo_population" in task_default.get('properties'):
            population_check = True
        
    gui_default_dict = {
        'laser_strength': task_default.get('strength'), 
        'time_step': task_default.get('time_step'),
        'number_of_steps': task_default.get('number_of_steps'),
        'output_freq': task_default.get('output_freq'),
        "pol_dir": None,
        "spectrum": spectrum_check,
        "ksd": ksd_check,
        "mo_population": population_check,
        
    }
    return gui_default_dict

