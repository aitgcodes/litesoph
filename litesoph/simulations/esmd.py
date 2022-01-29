from typing import Any, Dict
import os
import pathlib
import re
from configparser import ConfigParser
from litesoph.simulations.engine import EngineStrategy,EngineGpaw,EngineNwchem,EngineOctopus
from litesoph.utilities.job_submit import JobSubmit

config_file = pathlib.Path.home() / "lsconfig.ini"
if config_file.is_file is False:
    raise FileNotFoundError("lsconfig.ini doesn't exists")

configs = ConfigParser()
configs.read(config_file)

def get_engine_obj(engine, *args)-> EngineStrategy:
    """ It takes engine name and returns coresponding EngineStrategy class"""

    if engine == 'gpaw':
        return EngineGpaw(*args)
    elif engine == 'octopus':
        return  EngineOctopus(*args)
    elif engine == 'nwchem':
        return EngineNwchem(*args)

class Task:

    """It takes in the user input dictionary as input."""

    def __init__(self,status, project_dir) -> None:
        
        self.status = status
        self.engine_name = None
        self.engine = None
        self.project_dir = project_dir
        self.task_dir = None
        self.task_name = None
        self.task = None
        self.filename = None
        self.template = None
        self.task_state = None
        self.results = None

    def set_engine(self, engine):
        self.engine_name = engine
        self.engine = get_engine_obj(engine,self.project_dir, self.status)

    def set_task(self, task, user_input: Dict[str, Any], filename=None):
        self.task_name = task
        self.user_input = user_input
        self.user_input['project_dir'] = str(self.project_dir)
        try:
            self.task = self.engine.get_task_class(task, self.user_input)
        except Exception as e:
            raise Exception(e)

        if filename:
            self.filename = filename
        else:
            self.filename = self.task.NAME
    
    def load_template(self, filename):
        with open(filename, 'r') as f:
            text = f.read()
            self.template = text

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
        self.engine.create_script(self.task_dir, self.template,self.filename)
        self.file_path = pathlib.Path(self.task_dir) / self.engine.filename

    def create_task_dir(self):
        self.task_dir = self.engine.create_dir(self.project_dir, type(self.task).__name__)
        #os.chdir(self.directory)

    # def run(self, submit: JobSubmit):
    #     self.submit = submit
    #     self.submit.create_command()
    #     self.submit.run_job(self.task_dir)
        #print(str(self.submit.result))





def replacetext(search_text,replace_text):

	with open('gs.py','r+') as f:
		file = f.read()
		file = re.sub(search_text, replace_text, file)
		f.seek(0)
		f.write(file)
		f.truncate()






  

