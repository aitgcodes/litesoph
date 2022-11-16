
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
                "max_itr":task_default.get('max_itr'),
                "energy_conv": task_default.get('energy_conv'),
                "density_conv": task_default.get('density_conv'),
                "smearing": task_default.get('smearing'),
                "mixing": task_default.get('mixing'),
                "bands": task_default.get('bands'),
            }    
        return gui_default_dict

