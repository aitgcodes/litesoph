import configparser
from typing import Any, Dict
import pathlib
from configparser import ConfigParser
from ase.calculators.calculator import InputError
from litesoph.simulations.engine import EngineStrategy
from litesoph.utilities.job_submit import SubmitLocal

config_file = pathlib.Path.home() / "lsconfig.ini"
if config_file.is_file is False:
    raise FileNotFoundError("lsconfig.ini doesn't exists")

configs = ConfigParser()
configs.read(config_file)

class GroundState:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any],engine: EngineStrategy, directroy, filename) -> None:
        self.user_input = user_input
        self.engine = engine
        self.directory = directroy
        self.task = self.engine.get_task_class('ground state',self.user_input)

        if self.engine.check_compatability(self.user_input, self.task):
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= self.task.default_param, task=self.task)
            self.template = self.task.format_template(parameters)
            engine.create_script(self.user_input['directory'],filename, self.template)
        else:
            raise InputError("Input parameters not compatable with the engine")

    def run(self, proc):
        job = SubmitLocal(self.engine, configs, proc)
        job.create_command()
        job.run_job(self.directory)


class RT_LCAO_TDDFT:
    
    def __init__(self, user_input: Dict[str, Any],filename, engine: EngineStrategy, directory) -> None:
        self.user_input = user_input
        self.engine = engine
        self.task = self.engine.get_task_class('LCAO TDDFT', self.user_input)
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

        engine.create_script(self.directory, filename, self.template)
    
    def run(self, proc):
        job = SubmitLocal(self.engine, configs, proc)
        job.create_command()
        job.run_job(self.directory)

class LR_TDDFT:
    pass

class Spectrum:

    def __init__(self,user_input: Dict[str, Any],filename,engine: EngineStrategy, directory) -> None:
        self.user_input = user_input
        self.engine = engine
        self.directory = directory
        self.task = self.engine.get_task_class("spectrum", self.user_input)
        self.template = self.task.format_template()

        engine.create_script(self.directory, filename, self.template)

    def run(self, proc):
        job = SubmitLocal(self.engine, configs, proc)
        job.create_command()
        job.run_job(self.directory)

class TCM:
    
    def __init__(self,user_input: Dict[str, Any],filename,engine: EngineStrategy, directory) -> None:
        self.user_input = user_input
        self.engine = engine
        self.directory = directory
        self.task = self.engine.get_task_class("tcm", self.user_input)
        self.template = self.task.format_template()

        engine.create_script(self.directory, filename, self.template)

    def run(self, proc):
        job = SubmitLocal(self.engine, configs, proc)
        job.create_command()
        job.run_job(self.directory)
  

