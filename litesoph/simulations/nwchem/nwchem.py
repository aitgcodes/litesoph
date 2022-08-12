from litesoph.simulations.nwchem.nwchem_input import nwchem_create_input
from litesoph.simulations.nwchem.nwchem_read_rt import nwchem_rt_parser
from litesoph.post_processing.mo_population import extract_pop_window
import subprocess
import pathlib
import os
import numpy as np

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
            td_out_file = str(self.directory / self.outfile)
    
        nwchem_rt_parser(td_out_file, outfile=dipole_file,
                            tag=tag, target='dipole',
                            spin= spin, geometry=geometry,
                            polarization=polarization)

    
    def get_eigen_energy(self, td_out_file=None):

        if not td_out_file:
            td_out_file = str(self.directory / self.outfile)

        labels = ['Vector','Occupation', 'Eigenvalue']
        with open(td_out_file, 'r') as f:
            lines = f.readlines()

        data = []
        check = False
        for line in lines:

            if all([tag in line for tag in labels]):
                check = True
                continue

            if check:
                if '------' in line:
                    continue

                vals = line.strip().split()
                if not vals:
                    break
                data.append([float(val) for val in vals])
        return data

    def get_td_moocc(self, popl_file,
                        td_out_file=None, 
                        tag='<rt_tddft>',
                        homo_index=None, below_homo=None,
                        above_lumo=None):

        if not td_out_file:
            td_out_file = str(self.directory / self.outfile)

        if homo_index:
            pop_data = nwchem_rt_parser(td_out_file, outfile=popl_file,
                            tag=tag, target='moocc', retrun_data=True)
            print(np.shape(pop_data))
            
            extract_pop_window(pop_data, popl_file, homo_index, below_homo, above_lumo)
        else:
            nwchem_rt_parser(td_out_file, outfile=popl_file,
                            tag=tag, target='moocc')

