import configparser
from typing import Any, Dict
import os
import pathlib
from configparser import ConfigParser
from ase.calculators.calculator import InputError
from litesoph.simulations.engine import EngineStrategy
from litesoph.utilities.job_submit import JobSubmit

config_file = pathlib.Path.home() / "lsconfig.ini"
if config_file.is_file is False:
    raise FileNotFoundError("lsconfig.ini doesn't exists")

configs = ConfigParser()
configs.read(config_file)

class GroundState:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any],engine: EngineStrategy, status, directroy, filename) -> None:
        self.status = status
        self.user_input = user_input
        self.engine = engine
        self.directory = directroy
        self.filename = filename
        self.task = self.engine.get_task_class('ground state',self.user_input)

        if self.engine.check_compatability(self.user_input, self.task):
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= self.task.default_param, task=self.task)
            self.template = self.task.format_template(parameters)   
        else:
            raise InputError("Input parameters not compatable with the engine")
    
    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        self.status.update_status('gs_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "GS")
        os.chdir(self.directory)

    def c_status(self):
        gs_check= self.status.check_status('gs_inp', 1) 
        cal_check = self.status.check_status('gs_cal', 0)          
        if gs_check is True and cal_check is True:
            self.status.update_status('run', 1)
        else:
            if gs_check is False:
                self.status.update_status('run', 0)
            elif cal_check is False:
                self.status.update_status('run', 2)        

                
    def run(self, submit: JobSubmit):
        self.submit = submit
        #job = SubmitLocal(self.engine, configs, proc)
        self.submit.create_command()
        self.submit.run_job(self.directory)
        print(str(self.submit.result))


class RT_LCAO_TDDFT:
    
    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,submit: JobSubmit,status, directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.submit = submit
        self.filename = filename
        self.status = status
        self.task = self.engine.get_task_class('LCAO TDDFT', self.user_input)
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

        #engine.create_script(self.directory, filename, self.template)

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        self.status.update_status('td_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "TD")
        os.chdir(self.directory)
    
    def run(self, proc):
        #job = SubmitLocal(self.engine, configs, proc)
        self.submit.create_command()
        self.submit.run_job(self.directory)

class LR_TDDFT:
    pass

class Spectrum:

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,submit: JobSubmit, directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.submit = submit
        self.directory = directory
        self.task = self.engine.get_task_class("spectrum", self.user_input)
        self.template = self.task.format_template()

        #engine.create_script(self.directory, filename, self.template)

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        #self.status.update_status('td_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "Spectrum")
        os.chdir(self.directory)

    def run(self, proc):
        #job = SubmitLocal(self.engine, configs, proc)
        self.submit.create_command()
        self.submit.run_job(self.directory)

class TCM:
    
    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,submit: JobSubmit, directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.submit = submit
        self.directory = directory
        self.task = self.engine.get_task_class("tcm", self.user_input)
        self.template = self.task.format_template()

        #engine.create_script(self.directory, filename, self.template)
    
    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        self.status.update_status('td_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "TCM")
        os.chdir(self.directory)

    def run(self, proc):
        #job = SubmitLocal(self.engine, configs, proc)
        self.submit.create_command()
        self.submit.run_job(self.directory)
  

