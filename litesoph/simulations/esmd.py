from typing import Any, Dict
import os
import pathlib
from configparser import ConfigParser
from litesoph.simulations.engine import EngineStrategy,EngineGpaw,EngineNwchem,EngineOctopus
from litesoph.utilities.job_submit import JobSubmit

config_file = pathlib.Path.home() / "lsconfig.ini"
if config_file.is_file is False:
    raise FileNotFoundError("lsconfig.ini doesn't exists")

configs = ConfigParser()
configs.read(config_file)

def get_engine_obj(engine)-> EngineStrategy:
    """ It takes engine name and returns coresponding EngineStrategy class"""

    list_engine = [EngineGpaw(),
                    EngineOctopus(),
                    EngineNwchem()]
    if engine == 'gpaw':
        return list_engine[0]
    elif engine == 'octopus':
        return list_engine[1]
    elif engine == 'nwchem':
        return list_engine[2]

class Task:

    def create_task_dir(self):
        self.task_dir = self.engine.create_dir(self.project_dir, type(self.task).__name__)
        #os.chdir(self.directory)

    def run(self, submit: JobSubmit):
        self.submit = submit
        self.submit.create_command()
        self.submit.run_job(self.task_dir)
        #print(str(self.submit.result))

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
        #self.status.update_status('td_inp', 1)

    def task_dir(self):
        self.directory = self.engine.create_dir(self.directory, "Gopt")
        os.chdir(self.directory)
    
class GroundState(Task):
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any],engine,status, project_dir, filename) -> None:
        self.status = status
        self.user_input = user_input
        self.engine_name = engine
        self.engine = get_engine_obj(engine)
        self.project_dir = project_dir
        self.task_dir = None
        self.filename = filename
        self.task = self.engine.get_task_class('ground state',self.user_input)
        self.template = self.task.format_template()  

    
    def write_input(self, template=None):
        
        if template:
            self.template = template
        if not self.task_dir:
            self.create_task_dir()
        self.engine.create_script(self.task_dir,self.filename, self.template)
        self.file_path = pathlib.Path(self.task_dir) / self.engine.filename
        self.status.update_status('gs_inp', 1)
        self.status.update_status('engine', self.engine_name)
        self.status.update_status('gs_dict', self.user_input)

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
    
    def __init__(self, user_input: Dict[str, Any], engine, status, project_dir, filename, keyword:str=None) -> None:
        self.user_input = user_input
        self.engine = get_engine_obj(engine)
        self.keyword = keyword
        self.filename = filename
        self.status = status
        self.task = self.get_engine_task()
        self.project_dir = project_dir
        self.task_dir = None
        self.user_input['directory']=self.project_dir
        self.template = self.task.format_template()

    def get_engine_task(self):
        if self.keyword == "delta":
            return self.engine.get_task_class('LCAO TDDFT Delta', self.user_input, self.status)
        elif self.keyword == "laser":
            return self.engine.get_task_class('LCAO TDDFT Laser', self.user_input, self.status)

    def write_input(self, template=None):
        
        if template:
            self.template = template
        if not self.task_dir:
            self.create_task_dir()
        self.engine.create_script(self.task_dir,self.filename, self.template)
        self.update_status()
        
    def update_status(self):
        if self.keyword == "delta":
            self.status.update_status('td_inp', 1)
        elif self.keyword == "laser":
            self.status.update_status('td_inp', 2)

class LR_TDDFT(Task):
    pass

class Spectrum(Task):

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy,project_dir, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.project_dir = project_dir
        self.task_dir = None
        self.filename = filename
        self.task = self.engine.get_task_class("spectrum", self.user_input)
        self.template = self.task.format_template()

    def write_input(self, template=None):
        
        if template:
            self.template = template
        if not self.task_dir:
            self.create_task_dir()
        self.engine.create_script(self.task_dir,self.filename, self.template)

class TCM(Task):
    
    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy, project_dir, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.project_dir = project_dir
        self.task_dir = None
        self.filename = filename
        self.task = self.engine.get_task_class("tcm", self.user_input)
        self.template = self.task.format_template()

    def write_input(self, template=None):
        
        if template:
            self.template = template
        if not self.task_dir:
            self.create_task_dir()
        self.engine.create_script(self.task_dir,self.filename, self.template)
     


  

