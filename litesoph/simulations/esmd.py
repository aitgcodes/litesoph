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

class Task:

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, type(self.task).__name__)
        os.chdir(self.directory)

    def run(self, submit: JobSubmit):
        self.submit = submit
        self.submit.create_command()
        self.submit.run_job(self.directory)
        print(str(self.submit.result))

class GeometricOptimization(Task):

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,status, directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.filename = filename
        self.status = status
        self.task = self.engine.get_task_class('Optimization', self.user_input)
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        self.status.update_status('td_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "Gopt")
        os.chdir(self.directory)
    
class GroundState(Task):
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

    def prerequisite(self):
        self.job_d = self.engine.gs
        self.job_d['cal_check'] = self.status.check_status('gs_cal', 1)                       
        gs_check= self.status.check_status('gs_inp', 1) 
        return gs_check          
        # if gs_check is True :
        #     self.run_job('gs_cal', 1, 0)
        # else:
        #     show_message(self.msg_label1, "GS inputs not found")

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


class RT_LCAO_TDDFT(Task):
    
    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,status, directory, filename, keyword:str=None) -> None:
        self.user_input = user_input
        self.engine = engine
        self.keyword = keyword
        self.filename = filename
        self.status = status
        self.task = self.get_engine_task()
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

    def get_engine_task(self):
        if self.keyword == "delta":
            return self.engine.get_task_class('LCAO TDDFT Delta', self.user_input)
        elif self.keyword == "laser":
            return self.engine.get_task_class('LCAO TDDFT Laser', self.user_input)

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
        self.status.update_status('td_inp', 1)
    
    def prerequisite(self):

        if self.keyword == "delta":
            self.job_d = self.engine.td_delta
            self.job_d['cal_check'] = self.status.check_status('td_cal', 1)
            td_check = self.status.check_status('td_inp', 1) 
            gs_cal_check = self.status.check_status('gs_cal', 1)
            return td_check, gs_cal_check 

        elif self.keyword == "laser":
            self.job_d = self.engine.pulse
            self.job_d['cal_check'] = self.st_var.check_status('td_cal', 2)
            td_check = self.st_var.check_status('td_inp', 2)
            gs_cal_check = self.st_var.check_status('gs_cal', 1)
            return td_check, gs_cal_check  

       
        
    

class LR_TDDFT(Task):
    pass

class Spectrum(Task):

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.directory = directory
        self.filename = filename
        self.task = self.engine.get_task_class("spectrum", self.user_input)
        self.template = self.task.format_template()

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)

    def prerequisite(self):
        self.job_d = self.engine.gs
        self.job_d['cal_check'] = self.status.check_status('gs_cal', 1)                       
        gs_check= self.status.check_status('gs_inp', 1) 
        return gs_check  

class TCM(Task):
    
    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy, directory, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.directory = directory
        self.filename = filename
        self.task = self.engine.get_task_class("tcm", self.user_input)
        self.template = self.task.format_template()

    def write_input(self, template=None):
        
        if template:
            self.template = template

        self.task_dir()
        self.engine.create_script(self.directory,self.filename, self.template)
    
    def prerequisite(self):
        self.job_d = self.engine.gs
        self.job_d['cal_check'] = self.status.check_status('gs_cal', 1)                       
        gs_check= self.status.check_status('gs_inp', 1) 
        return gs_check  


  

