from typing import Any, Dict

from ase.calculators.calculator import InputError, Parameters
from litesoph.io.IO import write2file 
from gpaw import GPAW
from litesoph.simulations.GPAW import gpaw_template as gpaw
from abc import ABC, abstractclassmethod

class EngineStrategy(ABC):
    @abstractclassmethod
    def engine_name():
        """retruns engine name"""
        pass

    @abstractclassmethod
    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with the engine"""
        pass

    @abstractclassmethod
    def get_task_class( task: str):
        pass

    @abstractclassmethod
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    @abstractclassmethod
    def create_script(self,template: str, dict:Dict[str, Any]) -> None:
        pass

    @abstractclassmethod
    def excute():
        pass

class Enginegpaw(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'gpaw'

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""
        
        if user_param['mode'] not in ['fd', 'lcao', 'paw'] and  user_param['engine'] == 'gpaw':
            raise ValueError('This mode is not compatable with gpaw use fd, lcao or paw')
        
        if user_param['engine'] == 'gpaw':
            return  True
        else:
            return False

    def get_task_class(self, task: str):

        tasks = [gpaw.gpaw_ground_state(),
                gpaw.lr_tddft(),
                gpaw.rt_lcao_tddft(),
                gpaw.induced_density(),]

        if task == "ground state":
            return gpaw.gpaw_ground_state()
            
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        parameters = user2gpaw(user_param, default_param)
        return parameters
    
    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for gpaw"""
        filename = filename + '.py'
        write2file(directory,filename,template, dict)

    def excute():
        pass

class Engineoctopus(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'octopus '

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""

        return False

    def get_task_class(self, task: str):
        pass

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for octopus"""
        write2file(directory,filename,template, dict)

    def excute():
        pass

class Enginenwchem(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'nwchem'

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""

        return False

    def get_task_class(self, task: str):
        pass

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for nwchem"""
        write2file(directory,filename,template, dict)
    
    def excute():
        pass

def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
    list_engine = [Enginegpaw(),
                    Engineoctopus(),
                    Enginenwchem()]

    for engine in list_engine:
        if engine.check_compatability(user_input):
            return engine
        else:
            raise ValueError('engine not implemented')


class ground_state:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy) -> None:
        self.user_input = user_input
        self.engine = engine
        
        if self.engine.check_compatability(self.user_input):
            task = self.engine.get_task_class(task='ground state')
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= task.default_param)
            engine.create_script(self.user_input['work_dir'], 'gs', task.gs_template, parameters)
        else:
            raise InputError("Input parameters not compatable with the engine")

        
            
def user_para2engine_para(self, user_input:dict, engine:str):
    """It converts user input parameter to engine specific parameters."""


def user2gpaw(user_input:Dict[str, Any], default_parameters: Dict[str, Any]) -> Dict[str, Any]:
    import os
    parameters = default_parameters
    
    for key in user_input:
        if key not in ['tolerance','convergance','box'] and user_input[key] is not None:
            parameters[key] = user_input[key]
                        
        if key == 'work_dir' and user_input[key] is None:
            print('The project directory is not specified so the current directory will be taken as working directory')
            parameters.update(key = user_input['work_dir'][os.getcwd()])

        if key == 'geometry' and user_input[key] is None:
            raise ValueError('The structure file is not found')
    return parameters