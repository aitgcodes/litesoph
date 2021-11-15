from typing import Any, Dict
from litesoph.io.IO import write2file 
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

class EngineGpaw(EngineStrategy):

    tasks = [gpaw.GpawGroundState(),
                gpaw.LrTddft(),
                gpaw.RtLcaoTddft(),
                gpaw.InducedDensity(),]

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
        if task == "ground state":
            return gpaw.GpawGroundState()
            
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any], task) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        parameters = task.user2gpaw(user_param, default_param)
        return parameters
    
    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for gpaw"""
        filename = filename + '.py'
        write2file(directory,filename,template, dict)

    def excute():
        pass

class EngineOctopus(EngineStrategy):

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

class EngineNwchem(EngineStrategy):

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
    
    list_engine = [EngineGpaw(),
                    EngineOctopus(),
                    EngineNwchem()]

    for engine in list_engine:
        if engine.check_compatability(user_input):
            return engine
        else:
            raise ValueError('engine not implemented')