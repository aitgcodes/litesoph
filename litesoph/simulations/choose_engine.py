from typing import Any, Dict
from litesoph.simulations.engine import EngineStrategy, EngineGpaw,EngineNwchem,EngineOctopus

def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
    list_engine = [EngineGpaw(),
                    EngineOctopus(),
                    EngineNwchem()]
    
    if user_input['mode'] == "gaussian":
        return list_engine[2]
    if user_input['mode'] == "pw":
        return list_engine[0]
    else:
        if user_input['box'] == "paralleopiped":
            return list_engine[0]
        if user_input['box'] in ['sphere', 'cylinder', 'minimum']:
            return list_engine[1]