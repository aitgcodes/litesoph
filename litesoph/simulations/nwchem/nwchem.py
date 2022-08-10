from litesoph.simulations.nwchem.nwchem_input import nwchem_create_input
from litesoph.simulations.nwchem.nwchem_read_rt import nwchem_rt_parser
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

        if self.parameters:
            self.template = nwchem_create_input(**self.parameters) 
            return self.template
        else:
            raise Exception("sufficient input is not given.")

    def write_input(self, template=None):

        if template is not None:
            self.template = template
            
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

        command = f"{self.cmd} {self.infile} > {str(self.outfile)}"
        stdout, stderr = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True,
                                      shell=True, cwd=self.directory).communicate()

        print(stdout.strip(), stderr.strip())

    def read_results():
        pass

    def get_td_dipole(self, dipole_file,
                                td_out_file=None, 
                                tag='<rt_tddft>', 
                                spin="closedshell", 
                                geometry= 'system',
                                polarization = None ):

        if not td_out_file:
            td_out_file = str(self.directory / self.infile)
    
        nwchem_rt_parser(td_out_file, outfile=dipole_file,
                            tag=tag, target='dipole',
                            spin= spin, geometry=geometry,
                            polarization=polarization)

    def get_td_mooc(self, popl_file,
                        td_out_file=None, 
                        tag='<rt_tddft>'):

        if not td_out_file:
            td_out_file = str(self.directory / self.infile)
    
        nwchem_rt_parser(td_out_file, outfile=popl_file,
                            tag=tag, target='moocc')