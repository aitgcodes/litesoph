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

configs = configparser.ConfigParser({'python':'/usr/bin/python',
                                        'nwchem':'nwchem',
                                        'octopus':'octopus'}, allow_no_value=False)
configs.read(config_file)


class EngineStrategy(ABC):
    """Abstract base calss for the different engine."""

    
    @abstractclassmethod
    def get_task_class(self, task: str, user_param):
        pass

    @abstractclassmethod
    def create_script(self, template: str) -> None:
        pass

    @abstractclassmethod
    def create_command(self):
        pass

    def create_directory(self, directory):
        absdir = os.path.abspath(directory)
        if absdir != pathlib.Path.cwd and not pathlib.Path.is_dir(directory):
            os.makedirs(directory)


class EngineGpaw(EngineStrategy):

    NAME = 'gpaw'

    ground_state = {'inp':'/GS/gs.py',
            'req' : ['coordinate.xyz'],
            'out': 'GS/gs.out',
            'restart': 'GS/gs.gpw',
            'check_list':['Converged', 'Fermi level:','Total:']}

    rt_tddft_delta = {'inp':'TD_Delta/td.py',
            'req' : ['GS/gs.gpw'],
            'out': 'TD_Delta/tdx.out',
            'restart': 'TD_Delta/td.gpw',
            'check_list':['Writing','Total:']}

    rt_tddft_laser = {'inp':'TD_Laser/tdlaser.py',
            'req' : ['GS/gs.gpw'],
            'out': 'TD_Laser/tdlaser.out',
            'restart': 'TD_Laser/tdlaser.gpw',
            'check_list':['Writing','Total:']}
    
    spectrum = {'inp':'Spectrum/spec.py',
            'req' : ['TD_Delta/dm.dat'],
            'out': 'Spectrum/spec.dat',
            'restart': 'TD_Delta/dm.dat',
            'check_list':['FWHM']}

    task_dirs =[('GpawGroundState', 'GS'),
            ('GpawRTLCAOTddftDelta', 'TD_Delta'),
            ('GpawRTLCAOTddftLaser', 'TD_Laser'),
            ('GpawSpectrum', 'Spectrum'),
            ('GpawCalTCM', 'TCM')]
    
    def __init__(self,project_dir, status=None) -> None:
        self.project_dir = project_dir
        self.status = status

    def get_task_class(self, task: str, user_param, *_):
        if task == "ground_state":
            user_param['geometry']= str(pathlib.Path(self.project_dir.name) / self.ground_state['req'][0])
            return gp.GpawGroundState(user_param) 
        if task == "rt_tddft_delta":
            user_param['gfilename']= str(pathlib.Path(self.project_dir.name)  / self.rt_tddft_delta['req'][0])
            return gp.GpawRTLCAOTddftDelta(user_param)
        if task == "rt_tddft_laser":
            user_param['gfilename']= str(pathlib.Path(self.project_dir.name)  / self.rt_tddft_laser['req'][0])
            return gp.GpawRTLCAOTddftLaser(user_param)
        if task == "spectrum":
            user_param['moment_file']= str(pathlib.Path(self.project_dir.name) / self.spectrum['req'][0])
            return gp.GpawSpectrum(user_param) 
        if task == "tcm":
            return gp.GpawCalTCM(user_param)       
    
    def create_script(self,directory,template: str,filename) -> None:
        """creates the input scripts for gpaw"""
        if not filename:
            raise Exception('input filename not given')
        self.directory = directory
        self.filename = filename
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
        command = command + ' ' + str(filename) 
        if cmd:
            command = cmd + ' ' + command
            print(command)
        return command

class EngineOctopus(EngineStrategy):

    NAME = 'octopus'

    ground_state = {'out': '/Octopus/log',
        'req' : ['coordinate.xyz'],
        'check_list':['SCF converged']}

    rt_tddft_delta = {'out': '/Octopus/log',
             'req' : ['coordinate.xyz'],
             'check_list':['Finished writing information', 'Calculation ended']}    
    
    rt_tddft_laser = {'out': '/Octopus/log',
             'req' : ['coordinate.xyz']}

    def __init__(self,project_dir, status=None) -> None:
        self.project_dir = project_dir
        self.status = status

    def get_task_class(self, task: str, user_param):
        if task == "ground_state":
            user_param['geometry']= str(pathlib.Path(self.project_dir.name) / self.ground_state['req'][0])
            return ot.OctGroundState(user_param) 
        if task == "rt_tddft_delta":
            if self.status:
                gs_inp = self.status.get_status('ground_state.param')
                user_param.update(gs_inp)
            return ot.OctTimedependentState(user_param)
        if task == "rt_tddft_laser":
            if self.status:
                gs_inp = self.status.get_status('ground_state.param')
                user_param.update(gs_inp)
            return ot.OctTimedependentLaser(user_param)    
        if task == "spectrum":
            return ot.OctSpectrum(user_param)

    def create_dir(self, directory, *_):
        #task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / 'Octopus'
        self.create_directory(directory)
        return directory

    def create_script(self,directory,template: str, *_) -> None:
        """creates the input scripts for gpaw"""
        self.directory = directory
        self.filename = 'inp' 
        write2file(self.directory,self.filename,template)

    def create_command(self, cmd: list):

        ofilename = "log"
        command = configs.get('engine', 'octopus')
        if not command:
            command = 'octopus'
        command = command + ' ' + '>' + ' ' + str(ofilename)
        if cmd:
            command = cmd + ' ' + command
        return command

class EngineNwchem(EngineStrategy):

    NAME = 'nwchem'

    ground_state = {'inp':'/NwchemGroundState/gs.nwi',
            'req' : ['coordinate.xyz', 'nwchem_restart'],
            'check_list':['Converged', 'Fermi level:','Total:']}

    rt_tddft_delta = {'inp':'/NwchemGroundState/gs.nwi',
            'req' : ['coordinate.xyz', 'nwchem_restart'],
            'check_list':['Converged', 'Fermi level:','Total:']}

    rt_tddft_laser = {'inp':'/NwchemGroundState/gs.nwi',
            'req' : ['coordinate.xyz', 'nwchem_restart'],
            'check_list':['Converged', 'Fermi level:','Total:']}

    restart = 'nwchem_restart'

    def __init__(self,project_dir, status=None) -> None:
        self.project_dir = project_dir
        self.status = status
        self.restart = pathlib.Path(self.project_dir.name) / self.restart

    def get_task_class(self, task: str, user_param):
        if task == "optimization":
            user_param['permanent_dir']= str(self.restart)
            return nw.NwchemOptimisation(user_param) 
        if task == "ground_state":
            user_param['geometry']= str(pathlib.Path(self.project_dir.name) / self.ground_state['req'][0])
            user_param['permanent_dir']= str(self.restart)
            return nw.NwchemGroundState(user_param) 
        if task == "rt_tddft_delta":
            if self.status:
                gs_inp = self.status.get_status('ground_state.param')
                user_param.update(gs_inp)
            return nw.NwchemDeltaKick(user_param)
        if task == "rt_tddft_laser":
            if self.status:
                gs_inp = self.status.get_status('ground_state.param')
                user_param.update(gs_inp)
            return nw.NwchemGaussianPulse(user_param)

    def create_restart_dir(self):
        self.restart = self.project_dir.parent / self.restart
        self.create_directory(self.restart)

    def create_dir(self, directory, task):
        #task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / task
        self.create_directory(directory)
        return directory

    def create_script(self,directory,template: str,filename) -> None:
        """creates the input scripts for nwchem"""
        if not filename:
            raise Exception('input filename not given')
        self.directory = directory
        self.filename = filename 
        write2file(self.directory,self.filename,template)
    
    def create_command(self, cmd: list):

        filename = pathlib.Path(self.directory) / self.filename
        ofilename = pathlib.Path(filename).stem + '.nwo'
        command = configs.get('engine', 'nwchem')
        if not command:
            command = 'nwchem'
        command = command + ' ' + str(filename) + ' ' + '>' + ' ' + str(ofilename)
        if cmd:
            command = cmd + ' ' + command
        return command
