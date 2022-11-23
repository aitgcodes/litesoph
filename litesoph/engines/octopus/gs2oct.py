import numpy as np

def create_oct_gs_inp(gui_inp:dict):
    import copy
    # Add Validation for available options
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
                    sim_box = get_box_dim(_boxshape= boxshape,
                                    _from_vacuum= not select_box,
                                **copy_inp)
                    _dict.update(sim_box)               
                if key == "xc":
                    _dict.update(get_xc_pseudo(xc_str=xc)) 
    
    spacing_value = _dict.get("Spacing")
    _dict.update({"Spacing": str(spacing_value)+'*angstrom'})
    return _dict

def get_box_dim(_boxshape:str,_from_vacuum=False, **kwargs):
    if _from_vacuum :
        try:
            _geom_file = kwargs.get("XYZCoordinates")
            _vacuum = kwargs.get('vacuum', 6)
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
                                'Xlength':str(box_dict.get("cylinder length")/2)+'*angstrom'}}}
            return _sim_box 
        elif _boxshape == 'parallelepiped':
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'LSize':[[
                                str(box_dict.get("box length_x")/2)+'*angstrom',
                                str(box_dict.get("box length_y")/2)+'*angstrom',
                                str(box_dict.get("box length_z")/2)+'*angstrom']]}}} 
            return _sim_box                 

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

def set_expt_features():
    pass

def get_xc_pseudo(xc_str:str):
    _xc = xc_str.lower()
    xc_pseudo ={
        "lda":["lda_x + lda_c_pz_mod", "standard"],
        "pbe":["gga_x_pbe + gga_c_pbe", "pseudodojo_pbe"]
    }
    pseudo_expt = {'yes' :["pseudodojo_lda","hscv_lda","pseudodojo_lda_stringent",
                                "pseudodojo_pbe","pseudodojo_pbe_stringent","pseudodojo_pbesol","pseudodojo_pbesol_stringent","sg15", "hscv_pbe"],
                    'no':["standard", "hgh_lda_sc","hgh_lda"]
                    }
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
    
def convert_unit():
    pass

