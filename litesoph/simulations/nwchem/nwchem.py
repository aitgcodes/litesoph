from litesoph.simulations.nwchem.nwchem_input import nwchem_create_input
import subprocess
import pathlib
import os

class NWChem:

    def __init__(self,infile=None, outfile=None, 
                label='nwchem', directory=".", cmd=None, **kwargs) -> None:
        
        self.infile = infile
        self.outfile = outfile
        self.label = label
        self.cmd = cmd
        self.directory = directory
        self.parameters = kwargs
        self.parameters['label'] = label
        self.results = {}

    def create_input(self):
        self.template = nwchem_create_input(**self.parameters) 
        return self.template

    def write_input(self, template=None):

        if self.directory == ".":
            self.directory = pathlib.Path.cwd()

        infile = self.directory / self.infile

        restart_dir = self.parameters.get('perm', self.label)
        scratch_dir = self.parameters.get('scratch', restart_dir)
        
        for dir in [restart_dir, scratch_dir]:
            
            if dir != pathlib.Path.cwd() and not pathlib.Path(dir).is_dir():
                os.makedirs(dir)

        with open(infile , 'w+') as f:
            f.write(self.template)

    def run(self):

        self.create_input()
        self.write_input()       
        if not self.cmd:
            self.cmd = 'nwchem'

        command = f"{self.cmd} {self.infile} > {self.outfile}"
        stdout, stderr = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True,
                                      shell=True, cwd=self.directory).communicate()

        print(stdout.strip(), stderr.strip())

    def read_results():
        pass

    def get_timedependent_dipole(self,filename=None):

        pass
    