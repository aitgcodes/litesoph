from typing import Any, Dict
from ase.calculators.calculator import InputError
from litesoph.simulations.engine import EngineStrategy

class GroundState:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any],filename, engine: EngineStrategy) -> None:
        self.user_input = user_input
        self.engine = engine
        self.task = self.engine.get_task_class('ground state',self.user_input)

        if self.engine.check_compatability(self.user_input, self.task):
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= self.task.default_param, task=self.task)
            self.template = self.task.format_template(parameters)
            engine.create_script(self.user_input['directory'],filename, self.template)
        else:
            raise InputError("Input parameters not compatable with the engine")


class RT_LCAO_TDDFT:
    
    def __init__(self, user_input: Dict[str, Any],filename, engine: EngineStrategy, directory) -> None:
        self.user_input = user_input
        self.engine = engine
        self.task = self.engine.get_task_class('LCAO TDDFT', self.user_input)
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

        engine.create_script(self.directory, filename, self.template)
        
class LR_TDDFT:
    pass

