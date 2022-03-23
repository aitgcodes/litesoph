from configparser import ConfigParser
from typing import Any, Dict
import os
import pathlib
import re

from litesoph.simulations.engine import EngineStrategy,EngineGpaw,EngineNwchem,EngineOctopus

def get_engine_obj(engine, *args, **kwargs)-> EngineStrategy:
    """ It takes engine name and returns coresponding EngineStrategy class"""

    if engine == 'gpaw':
        return EngineGpaw(*args, **kwargs)
    elif engine == 'octopus':
        return  EngineOctopus(*args, **kwargs)
    elif engine == 'nwchem':
        return EngineNwchem(*args, **kwargs)

class Task:

    """It takes in the user input dictionary as input."""

    bash_filename = 'job_script.sh'

    def __init__(self, status, project_dir:pathlib.Path, lsconfig:ConfigParser) -> None:
        
        self.status = status
        self.lsconfig = lsconfig
        self.engine_name = None
        self.engine = None
        self.project_dir = project_dir
        self.task_dir = None
        self.task_name = None
        self.task = None
        self.filename = None
        self.template = None
        self.input_data_files = []
        self.output_data_file = []
        self.task_state = None
        self.results = None

    def set_engine(self, engine):
        self.engine_name = engine
        self.engine = get_engine_obj(engine, project_dir = self.project_dir, lsconfig = self.lsconfig, status=self.status)

    def set_task(self, task, user_input: Dict[str, Any]):
        self.task_name = task
        self.user_input = user_input
        self.user_input['project_dir'] = str(self.project_dir)
        try:
            self.task = self.engine.get_task_class(task, self.user_input)
        except Exception as e:
            raise Exception(e)

        inp_data = getattr(self.engine, task)
    
        self.filename = pathlib.Path(f"{self.project_dir.name}/{inp_data['inp']}")
        for item in inp_data['req']:
            item = pathlib.Path(self.project_dir.name) / item
            self.input_data_files.append(item)
       
    def load_template(self, filename):
        self.file_path = filename

    def create_template(self):
        if self.task:
            self.template = self.task.format_template() 
        else:
            raise AttributeError('task is not set.')

    def write_input(self, template=None):
        
        if template:
            self.template = template
        if not self.task_dir:
            self.create_task_dir()
        if not self.template:
            msg = 'Template not given or created'
            raise Exception(msg)
        self.engine.create_script(self.task_dir, self.template, self.filename.name)
        #self.file_path = pathlib.Path(self.task_dir) / self.engine.filename

    def check_prerequisite(self, network=False) -> bool:
        """ checks if the input files and required data files for the present task are present"""
        
        inupt_file = self.project_dir.parent / self.filename
        
        if not pathlib.Path(inupt_file).exists():
            check = False
            msg = f"Input file:{inupt_file} not found."
            raise FileNotFoundError(msg)

        if network:
            bash_file = self.project_dir / self.bash_filename
            if not bash_file.exists():
                msg = f"job_script:{bash_file} not found."
                raise FileNotFoundError(msg)
            self.bash_filename = bash_file.relative_to(self.project_dir.parent)
        
        for item in self.input_data_files:
            item = self.project_dir.parent / item
            if not pathlib.Path(item).exists():
                msg = f"Data file:{item} not found."
                raise FileNotFoundError(msg)
        
        

    # def prepare_input(self,path, filename):
    #     path = pathlib.Path(path)
    #     try:
    #         self.input_data_files = getattr(self.engine, self.task_name)
    #         self.input_data_files = self.input_data_files['req']
    #     except AttributeError as e:
    #         raise AttributeError(e)

    #     with open(filename , 'r+') as f:
    #         text = f.read()
    #         for item in self.input_data_files:
    #             data_path = path / item
    #             item = item.split('/')[-1]
    #             text = re.sub(item, str(data_path), text)
    #         f.seek(0)
    #         f.write(text)
    #         f.truncate()        
    
    def create_task_dir(self):
        self.task_dir = self.engine.create_dir(self.project_dir, type(self.task).__name__)


    def replacetext(filename, search_text,replace_text):

        with open(filename,'r+') as f:
            file = f.read()
            file = re.sub(search_text, replace_text, file)
            f.seek(0)
            f.write(file)
            f.truncate()






  

