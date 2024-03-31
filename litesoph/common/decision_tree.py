from typing import Union, List, Dict

from litesoph.engines.gpaw.task_data import gpaw_gs_param_data as gpaw_data
from litesoph.engines.octopus.task_data import ground_state as octopus_data
from litesoph.engines.nwchem.task_data import nwchem_gs_param_data as nwchem_data

ls_integrated_engines = ["gpaw", "nwchem", "octopus"]
available_engines = ["gpaw","nwchem", "octopus"]
engine_priorities = ["nwchem","gpaw","octopus"]  

engine_data_base = {
    "nwchem": nwchem_data,
    "gpaw": gpaw_data,
    "octopus": octopus_data
}   

#TODO: workflows should be referenced using workflow_db class 
# instead of directly using string.
workflow_compatibility = {
    "task_mode":ls_integrated_engines,
    "spectrum": ls_integrated_engines,
    "averaged_spectrum": ls_integrated_engines,
    "kohn_sham_decomposition": ["octopus","gpaw",],
    "mo_population_tracking": ls_integrated_engines,
    "masking":["gpaw"],
    "pump_probe": ls_integrated_engines
    }

xc_hybrid = ["B3LYP", "PBE0","CAMY-B3LYP","CAM-B3LYP",
            "HSE03","HSE06","M05","M05-2X","M06-HF",
            "M08-SO","M011"]
xc_gga = ["PBE","PW91","BLYP","CAMY-BLYP","PBEsol",
            "PW91","BP86","BP91","LC-BLYP","LC-PBE","LC-wPBE"]
xc_lda = ["LDA"]

basis_sets_gaussian = ["def2SVP","6-31G","STO-2G","STO-3G"]
basis_sets_lcao = ["dzp","dz","sz","pvalence.dz","szp"]
basis_sets_fd = []
basis_sets_pw = []

priority_basis_type = ["gaussian","lcao","fd","pw"]
priority_xc = xc_hybrid + xc_gga + xc_lda
priority_basis_set = basis_sets_gaussian + basis_sets_lcao
priority_boxshape = ["minimum","sphere","cylinder","parallelepiped"]

priority_map = {
    "basis_type": priority_basis_type,
    "xc": priority_xc,
    "basis": priority_basis_set,
    "boxshape": priority_boxshape   
}

class EngineDecisionError(RecursionError):
    "Raise this exception when unable to determine the engine."

def update_engine_list(calc_param:str, choice:str, engine_data_map:dict):
    """Access the possible task_param values from engine_data_map,
    and updates the engine list if choice is present"""

    engine_list = []
    for engine, engine_data in engine_data_map.items():
        param_dict = engine_data.get(calc_param)
        if param_dict is not None:
            if 'values' in param_dict:
                values = param_dict.get('values')
            elif 'metadata'in param_dict:
                meta_data = param_dict.get('metadata')
                for key, value1 in meta_data.items():                    
                    if isinstance(value1, dict):
                        _values = []
                        for key, value2 in value1.items():
                            values = value2.get('values')
                            if isinstance(values, list):
                                _values.extend(values)
                            values = _values          
            if  values is not None:
                if choice in values:
                    engine_list.append(engine)
    return engine_list

def get_choice_engines(calc_param:str,engine_data_map:dict):
    """Returns a list of tuples of the form (calc_param_option, list of compatible engines)
    in order of decreasing priority"""

    param_list = priority_map.get(calc_param)
    _list = []
    if isinstance(param_list, list):
        for item in param_list:
            engine_list = update_engine_list(calc_param,item, engine_data_map)            
            choice_engine_pair = (item, engine_list)
            _list.append(choice_engine_pair)
        return _list

#--------------------------------------------------------------------------------------

calc_params = {
    "basis_type": get_choice_engines("basis_type",engine_data_base),
    "xc": get_choice_engines("xc",engine_data_base),
    "basis": get_choice_engines("basis",engine_data_base),
    "boxshape": get_choice_engines("boxshape",engine_data_base)
    }

def decide_engine(workflow_type:str, 
                  decision_priority:list =["basis_type", "xc","basis", "boxshape"] , 
                  decision_param_dict:dict = calc_params,
                  available_engines:list =["gpaw","nwchem", "octopus"]):
    
    compatible_engines = workflow_compatibility.get(workflow_type)
    incompatible_engines = [engine for engine in ls_integrated_engines 
                            if engine not in compatible_engines]

    for engine in available_engines:
        if engine in incompatible_engines:
            available_engines.remove(engine)
    engine_list = available_engines

    assert len(decision_priority) > 0
    choice_list = []
    for param in decision_priority:
        param_list = decision_param_dict.get(param)
        if param_list is not None:
            param_dict = dict(param_list)
            
            for i, (choice, list) in enumerate(param_dict.items()):
                common = [engine for engine in engine_list if engine in list]
                if len(common) > 0:
                    engine_list = common
                    choice_list.append(choice)
                    break

    if len(engine_list) > 0:
        priority_index = [engine_priorities.index(engine) for engine in engine_list]
        index_min = min(priority_index)
        engine_choice = engine_priorities[index_min]
        return engine_choice
    else:
        EngineDecisionError("Error in deciding engine")


def choose_engine(input_param:dict)-> Union[str, List[str]]:
    
    basis_type = input_param.get('basis_type', None)

    if basis_type is None:
        raise EngineDecisionError("Basis type is not defined.")

    boxshape = input_param.get('boxshape')
    if boxshape:
        if basis_type == "lcao":
            if boxshape == "parallelepiped":
                engine = "gpaw"
                return engine
            else:
                raise EngineDecisionError(f"Box shape:{boxshape} is not supported in LCAO basis type.")
        
        if basis_type == "fd":
            if boxshape == "parallelepiped":
                return ['gpaw', 'octopus']
            elif boxshape in ["minimum","sphere","cylinder"] : 
                engine = "octopus"
            return engine
    else:
        if basis_type == "pw":
            engine = "gpaw"
        elif basis_type == "gaussian":
            engine = "nwchem"
            return engine