import configparser
from logging import raiseExceptions
import pathlib
import os
from configparser import ConfigParser
from typing import Any, Dict
from litesoph.lsio.IO import write2file 
from litesoph.simulations.gpaw import gpaw_template as gp
from litesoph.simulations.nwchem import nwchem_template as nw
from litesoph.simulations.octopus import octopus_template as  ot
from abc import ABC, abstractclassmethod

config_file = pathlib.Path.home() / "lsconfig.ini"
if config_file.is_file is False:
    raise FileNotFoundError("lsconfig.ini doesn't exists")

configs = configparser.SafeConfigParser({'python':'/usr/bin/python',
                                        'nwchem':'nwchem',
                                        'octopus':'octopus'})
configs.read(config_file)


class EngineStrategy(ABC):
    """Abstract base calss for the different engine."""

    
    @abstractclassmethod
    def get_task_class(self, task: str, user_param):
        pass

    # @abstractclassmethod
    # def check_compatability(self, user_param:Dict[str, Any], task: object) -> bool:
    #     """checks the compatability of the input parameters with the engine"""
    #     pass

    # @abstractclassmethod
    # def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
    #     """updates the default input parameters with the user input"""
    #     pass

    @abstractclassmethod
    def create_script(self, template: str) -> None:
        pass

    @abstractclassmethod
    def create_command(self):
        pass

    def create_directory(self,directory):

        absdir = os.path.abspath(directory)
        if absdir != os.curdir and not os.path.isdir(directory):
            os.makedirs(directory)
        # else:
        #     raise FileExistsError


class EngineGpaw(EngineStrategy):

    
    gs = {'inp':'/GS/gs.py',
            'out': '/GS/gs.out',
            'restart': 'GS/gs.gpw',
            'check_list':['Converged', 'Fermi level:','Total:']}

    td_delta = {'inp':'/TD_Delta/td.py',
             'out': '/TD_Delta/tdx.out',
             'restart': '/TD_Delta/td.gpw',
             'check_list':['Writing','Total:']}

    laser = {'inp':'/TD_Laser/tdlaser.py',
             'out': '/TD_Laser/tdlaser.out',
             'restart': '/TD_Laser/tdlaser.gpw',
             'check_list':['Writing','Total:']}
    
    task_dirs =[('GpawGroundState', 'GS'),
            ('GpawRTLCAOTddftDelta', 'TD_Delta'),
            ('GpawRTLCAOTddftLaser', 'TD_Laser'),
            ('GpawSpectrum', 'Spectrum'),
            ('GpawCalTCM', 'TCM')]

    def get_task_class(self, task: str, user_param):
        if task == "ground state":
            return gp.GpawGroundState(user_param) 
        if task == "LCAO TDDFT Delta":
            return gp.GpawRTLCAOTddftDelta(user_param)
        if task == "LCAO TDDFT Laser":
            return gp.GpawRTLCAOTddftLaser(user_param)
        if task == "spectrum":
            return gp.GpawSpectrum(user_param) 
        if task == "tcm":
            return gp.GpawCalTCM(user_param)       

    # def check_compatability(self, user_param:Dict[str, Any], task: object ) -> bool:
    #     """checks the compatability of the input parameters with gpaw engine"""
        
    #     return task.check(user_param)
            
    # def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any], task) -> Dict[str, Any]:
    #     """updates the default input parameters with the user input"""
    #     parameters = task.user2gpaw(user_param, default_param)
    #     return parameters
    
    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for gpaw"""
        self.directory = directory
        self.filename = filename + '.py'
        write2file(self.directory,self.filename,template)

    def create_dir(self, directory, task):
        task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / task_dir
        self.create_directory(directory)
        return directory

    def get_dir_name(self,task):
        for t_dir in self.task_dirs:
            if task in t_dir:
                dir = t_dir[1]
                break
        return dir

    def create_command(self, cmd: list):

        filename = pathlib.Path(self.directory) / self.filename
        command = configs.get('programs', 'python')
        command = [command, filename]
        if cmd:
            cmd.extend(command)
            command = cmd
        return command

class EngineOctopus(EngineStrategy):


    def get_task_class(self, task: str, user_param):
        if task == "ground state":
            return ot.OctGroundState(user_param) 
        if task == "LCAO TDDFT Delta":
            return ot.OctTimedependentState(user_param)
    
    # def check_compatability(self, user_param:Dict[str, Any], task: object ) -> bool:
    #     """checks the compatability of the input parameters with gpaw engine"""
        
    #     return task.check(user_param)
            
    # def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any], task) -> Dict[str, Any]:
    #     """updates the default input parameters with the user input"""
    #     parameters = task.user2octopus(user_param, default_param)
    #     return parameters

    def create_dir(self, directory, task):
        #task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / task
        self.create_directory(directory)
        return directory

    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for gpaw"""
        self.directory = directory
        self.filename = filename 
        write2file(self.directory,self.filename,template)

    def create_command(self, cmd: list):

        filename = pathlib.Path(self.directory) / self.filename
        command = configs.get('engine', 'octopus')
        command = [command]
        if cmd:
            cmd.extend(command)
            command = cmd
        return command

class EngineNwchem(EngineStrategy):


    def get_task_class(self, task: str, user_param):
        if task == "optimization":
            return nw.NwchemOptimisation(user_param) 
        if task == "ground state":
            return nw.NwchemGroundState(user_param) 
        if task == "LCAO TDDFT Delta":
            return nw.NwchemDeltaKick(user_param)

    # def check_compatability(self, user_param:Dict[str, Any], task: object ) -> bool:
    #     """checks the compatability of the input parameters with gpaw engine"""
        
    #     return task.check(user_param)
            
    # def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any], task) -> Dict[str, Any]:
    #     """updates the default input parameters with the user input"""
    #     parameters = task.user2nwchem(user_param, default_param)
    #     return parameters

    def create_dir(self, directory, task):
        #task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / task
        self.create_directory(directory)
        return directory

    def create_script(self,directory,filename,template: str) -> None:
        """creates the input scripts for nwchem"""
        self.directory = directory
        self.filename = filename + '.nwi'
        write2file(self.directory,self.filename,template)
    
    def create_command(self, cmd: list):

        filename = pathlib.Path(self.directory) / self.filename
        command = configs.get('engine', 'nwchem')
        command = [command, filename]
        if cmd:
            cmd.extend(command)
            command = cmd
        return command

def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
    list_engine = [EngineGpaw(),
                    EngineOctopus(),
                    EngineNwchem()]
    return list_engine[2]
    # for engine in list_engine:
    #     #task = engine.get_task_class("ground state", user_input)
    #     #if engine.check_compatability(user_input, task):
    #         return engine
    #     else:
    #         raise ValueError('engine not implemented')

#def get_engine_after_gs(status)