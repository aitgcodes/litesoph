from configparser import ConfigParser
from litesoph.simulations.engine import EngineStrategy
import subprocess  
import pathlib

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
        job.wait()
        return job
      
    
class SubmitLocal(JobSubmit):

    def __init__(self, engine: EngineStrategy, configs: ConfigParser, num_p:int) -> None:
        super().__init__(engine, configs)
        self.np = num_p 
        self.command = []
        if self.np:
            self.command.extend(self.mpi_cmd)
            self.command.append(str(self.np))
           

    def create_command(self):
        self.command = self.engine.create_command(self.command)
    
    def run_job(self,directory):
        print(self.command)
        return super().run_job(self.command, directory)
       

class SubmitNetwork(JobSubmit):
    pass            