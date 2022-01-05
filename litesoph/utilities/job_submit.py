from configparser import ConfigParser
from litesoph.simulations.engine import EngineStrategy
import subprocess  
import pathlib

def get_submit_class(network=None, **kwargs):
    
    if network:
        return SubmitNetwork(**kwargs)
    else:
        return SubmitLocal(**kwargs)

class JobSubmit:
    
    def __init__(self, engine: EngineStrategy, configs: ConfigParser, keyword:str=None) -> None:
        self.engine = engine
        self.configs = configs
        if configs.items('mpi'):
            self.mpi_cmd = list(configs.items('mpi'))[0][1]
            print(self.mpi_cmd)
            self.mpi_cmd = [self.mpi_cmd, '-np']
        
    def run_job(self, command, directory):
        job = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd= directory)
        
        return job
      
    
class SubmitLocal(JobSubmit):

    def __init__(self, engine: EngineStrategy, configs: ConfigParser, nprocessors:int) -> None:
        super().__init__(engine, configs)
        self.np = nprocessors
        self.command = []
        if self.np > 1:
            self.command.extend(self.mpi_cmd)
            self.command.append(str(self.np))
           

    def create_command(self):
        self.command = self.engine.create_command(self.command)
    
    def run_job(self,directory):
        print(self.command)
        self.j = super().run_job(self.command, directory)
        self.result = self.j.communicate()[1]
       

class SubmitNetwork(JobSubmit):
    pass            