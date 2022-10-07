
def create_oct_gs_inp(gui_inp:dict):
    import copy

    key2key = {
        # "ExcessCharge": "",
        "max itr": "MaximumIter",
        "energy conv": "ConvEnergy",
        "density conv": "ConvAbsDens",
        "smearing":"Smearing",
        "mixing":"Mixing",
        "bands" : "ExtraStates"
        }

    _dict = {
        "CalculationMode": "gs",
        "UnitsOutput": "ev_angstrom"
    }


    boxshape = gui_inp.get("box shape")
    select_box = gui_inp.get("select box")
    xc = gui_inp.get("xc family")
    copy_inp = copy.deepcopy(gui_inp)
    
    for i, (key, value) in enumerate(gui_inp.items()):
        if value is not None:
            if key in key2key.keys():
                _key2key_dict = dict(
                [(key2key.get(key), value) 
                for key, value in copy_inp.items()])
                _dict.update(_key2key_dict)
            else:
                sim_box = get_box_dim(_boxshape= boxshape,
                                     _from_vacuum= not select_box,
                                    **copy_inp)
                _dict.update(sim_box)
                _dict.update(get_xc_pseudo(xc_str=xc)) 
    return _dict

def get_box_dim(_boxshape:str,_from_vacuum=False, **kwargs):
    if _from_vacuum and _boxshape == "parallelepiped":
        try:
            _geom_file = kwargs.get("geom_file")
            _vacuum = kwargs.get('vacuum', 6)
        except:
            pass
        _cell = get_box_dim_from_vacuum(_geom_file,_vacuum, _boxshape)
        _sim_box = {
                    "BoxShape":{"name":_boxshape,
                    "param":{'LSize':[[
                        str(_cell[0]/2)+'*angstrom',
                        str(_cell[1]/2)+'*angstrom',
                        str(_cell[2]/2)+'*angstrom']]}}
                        }
        return _sim_box
    elif not _from_vacuum:
        if _boxshape in ['minimum','sphere']:            
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'Radius':kwargs.get("radius")+'*angstrom'}}}
            return _sim_box 
        elif _boxshape == 'cylinder':
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'Radius':kwargs.get("radius")+'*angstrom',
                                'Xlength':str(kwargs.get("cylinder length")/2)+'*angstrom'}}}
            return _sim_box 
        elif _boxshape == 'parallelepiped':
            _sim_box = {
            "BoxShape":{"name":_boxshape,
                        "param":{'LSize':[[
                                str(kwargs.get("box length_x")/2)+'*angstrom',
                                str(kwargs.get("box length_y")/2)+'*angstrom',
                                str(kwargs.get("box length_z")/2)+'*angstrom']]}}} 
            return _sim_box                 

def get_box_dim_from_vacuum(geom_file, vacuum:float,box_shape,):
    from ase.io import read
    atoms = read(geom_file)
    atoms.center(vacuum=vacuum)
    if box_shape == "parallepiped":
        cell = atoms.get_cell()

        lx = cell[0][0]
        ly = cell[0][1]
        lz = cell[0][2]

        return cell
    else:
        raise ValueError("Not implemented")

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
        xc_dict = {
        "ExperimentalFeatures":expt,
        "XCFunctional": xc,
        "PseudopotentialSet" : pseudo,    
        }
    return xc_dict

    
def convert_unit():
    pass