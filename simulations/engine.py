from typing import Any, Dict
from litesoph.lsio.IO import write2file 
from litesoph.simulations.GPAW import gpaw_template as gp
from abc import ABC, abstractclassmethod


class EngineStrategy(ABC):
    """Abstract base calss for the different engine."""

    tasks =[]

    @abstractclassmethod
    def engine_name():
        """retruns engine name"""
        pass
    
    @abstractclassmethod
    def get_task_class( task: str, user_param):
        pass

    @abstractclassmethod
    def check_compatability(self, user_param:Dict[str, Any], task: object) -> bool:
        """checks the compatability of the input parameters with the engine"""
        pass

    @abstractclassmethod
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    @abstractclassmethod
    def create_script(self, template: str) -> None:
        pass

    @abstractclassmethod
    def excute():
        pass

class EngineGpaw(EngineStrategy):

    tasks = [gp.GpawGroundState(),
                gp.LrTddft(),
                gp.RtLcaoTddft(),
                gp.InducedDensity()]

    def engine_name():
        """retruns engine name"""
        return 'gpaw'

    def get_task_class(self, task: str, user_param):
        if task == "ground state":
            return gp.GpawGroundState(user_param)
        if task == "LCAO TDDFT":
            return gp.RtLcaoTddft(user_param)

    def check_compatability(self, user_param:Dict[str, Any], task: object ) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""
        
        return task.check(user_param)
            
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any], task) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        parameters = task.user2gpaw(user_param, default_param)
        return parameters
    
    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for gpaw"""
        filename = filename + '.py'
        write2file(directory,filename,template)

    def excute():
        pass

class EngineOctopus(EngineStrategy):

    tasks = []

    def engine_name():
        """retruns engine name"""
        return 'octopus '

    def get_task_class(self, task: str):
        pass
    
    def check_compatability(self, user_param:Dict[str, Any], task: object) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""
        return False

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for octopus"""
        write2file(directory,filename,template)

    def excute():
        pass

class EngineNwchem(EngineStrategy):

    tasks = []

    def engine_name():
        """retruns engine name"""
        return 'nwchem'

    def get_task_class(self, task: str):
        pass

    def check_compatability(self, user_param:Dict[str, Any], task: object) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""

        return False

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for nwchem"""
        write2file(directory,filename,template)
    
    def excute():
        pass

def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
    list_engine = [EngineGpaw(),
                    EngineOctopus(),
                    EngineNwchem()]

    for engine in list_engine:
        task = engine.get_task_class("ground state", user_input)
        if engine.check_compatability(user_input, task):
            return engine
        else:
            raise ValueError('engine not implemented')