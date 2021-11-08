from typing import Any, Dict
from ase.calculators.calculator import InputError
from litesoph.simulations.engine import EngineStrategy

class ground_state:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy) -> None:
        self.user_input = user_input
        self.engine = engine
        
        if self.engine.check_compatability(self.user_input):
            task = self.engine.get_task_class(task='ground state')
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= task.default_param, task=task)
            engine.create_script(self.user_input['work_dir'], 'gs', task.gs_template, parameters)
        else:
            raise InputError("Input parameters not compatable with the engine")

        
class rt_tddft:
    pass

class lr_tddft:
    pass

def user_para2engine_para(self, user_input:dict, engine:str):
    """It converts user input parameter to engine specific parameters."""

if __name__ == "__main__":
    print('sachin')
