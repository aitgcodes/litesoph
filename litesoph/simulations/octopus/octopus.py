import os
import pathlib
import subprocess
from litesoph.simulations.octopus.octopus_input import generate_input

class Octopus:
    def __init__(self,infile=None, outfile=None, 
                directory=".", cmd=None, **kwargs) -> None:
        if infile:
            self.infile = infile
        else:
            self.infile = 'inp'
        self.outfile = outfile
        self.directory = directory
        self.cmd = cmd
        self.parameters = kwargs
        
    def create_input(self):
        self.template = generate_input(self.parameters)
        return self.template

    def write_input(self, template):

        self.template = template

        self.infile_path = self.directory / self.infile
        self.outfile_path = self.directory / self.outfile
        # self.infolder = pathlib.Path(self.infile_path).parent()
        # self.outfolder = pathlib.Path(self.outfolder).parent()
        
        if self.directory == ".":
            self.directory = pathlib.Path.cwd()

        if self.directory != pathlib.Path.cwd() and not pathlib.Path(self.directory).is_dir():
            os.makedirs(self.directory)

        with open(self.infile_path, 'w+') as f:
            f.write(self.template)   

    def run(self):
        if not self.cmd:
            self.cmd = 'octopus'

        self.outfile_path = self.directory / self.outfile   
        self.create_input()
        self.write_input() 

        command = f"{self.cmd} &> {self.outfile}"
        stdout, stderr = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True,
                                      shell=True, cwd=self.directory).communicate()

        print(stdout.strip(), stderr.strip()) 
        
        

        