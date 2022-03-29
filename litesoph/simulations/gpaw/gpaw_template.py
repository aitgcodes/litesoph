import pathlib
from typing import Any, Dict
#from litesoph.simulations.engine import EngineGpaw


class GpawGroundState:
    """This class contains the default parameters and the template for creating gpaw 
    scripts for ground state calculations."""
    NAME = 'gs.py'

    input_data_files = [('geometry', 'coordinate.xyz')]

    default_param =  {
        'geometry' : 'coordinate.xyz',
        'mode': 'fd',
        'xc': 'LDA',
        'occupations': None,
        'poissonsolver': None,
        'h': None,  # Angstrom
        'gpts': None,
        'kpts': [(0.0, 0.0, 0.0)],
        'nbands': None,
        'charge': 0,
        'setups': {},
        'basis': {},
        'spinpol': None,
        'filter': None,
        'mixer': None,
        'eigensolver': None,
        'background_charge': None,
        'experimental': {'reuse_wfs_method': 'paw',
                         'niter_fixdensity': 0,
                         'magmoms': None,
                         'soc': None,
                         'kpt_refine': None},
        'external': None,
        'random': False,
        'hund': False,
        'maxiter': 333,
        'idiotproof': True,
        'symmetry': {'point_group': True,
                     'time_reversal': True,
                     'symmorphic': True,
                     'tolerance': 1e-7,
                     'do_not_symmetrize_the_density': None},  # deprecated
        'convergence': {'energy': 0.0005,  # eV / electron
                        'density': 1.0e-4,
                        'eigenstates': 4.0e-8,  # eV^2
                        'bands': 'occupied'},  # eV / Ang
        'verbose': 0,
        'fixdensity': False,  # deprecated
        'dtype': None}  # deprecated

    gs_template = """
from ase.io import read, write
from gpaw import GPAW
from numpy import inf

# Molecule or nanostructure
atoms = read('{geometry}')
atoms.center(vacuum={vacuum})

#Ground-state calculation
calc = GPAW(mode='{mode}',
    xc='{xc}',
    h={h},  # Angstrom
    gpts={gpts},
    kpts={kpts},
    nbands= {nbands},
    charge= {charge},
    setups= {setups},
    basis={basis},
    spinpol= {spinpol},
    filter={filter},
    mixer={mixer},
    hund={hund},
    maxiter={maxiter},
    symmetry={symmetry},  
    convergence={convergence},
    txt='gs.out')
atoms.calc = calc
energy = atoms.get_potential_energy()
calc.write('gs.gpw', mode='all')

    """
    def __init__(self, user_input) -> None:
        self.user_input = self.default_param
        self.user_input.update(user_input)
   
    def format_template(self):
        template = self.gs_template.format(**self.user_input)
        return template
    
    @staticmethod
    def get_network_job_cmd():
        job_script = """
##### LITESOPH Appended Comands###########

cd GS/
mpirun -np 4  python3 gs.py\n"""
        return job_script

class GpawRTLCAOTddftDelta:
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""
    
    NAME = 'td.py'

    input_data_files = [('gfilename', 'gs.gpw')]

    default_input = {'absorption_kick': [1e-5, 0.0, 0.0],
                'propagate': (20, 150),
                'module': None,
                'laser':None,
                'electric_pol': None,
                'dipole_file':'dm.dat',
                'wavefunction_file':'wf.ulm',
                'analysis_tools': None,
                'gfilename':'gs.gpw',
                'propagator':None,
                'td_potential': None,
                'fxc':None,
                'parallel': None,
                'txt':'tdx.out',
                'td_gpw':'td.gpw'}

    analysis_tools = [
        ('DipoleMomentWriter()','from gpaw.lcaotddft.dipolemomemtwriter import DipoleMomentWriter'),
        ('WaveFunctionWriter()','from gpaw.lcaotddft.wfwriter import WaveFunctionWriter')

    ]
    
    delta_kick_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
import numpy as np
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter

td_calc = LCAOTDDFT(filename='{gfilename}',txt='{txt}')

DipoleMomentWriter(td_calc, '{dipole_file}')

# Kick
td_calc.absorption_kick({absorption_kick})
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{td_gpw}', mode='all')
    """

    def __init__(self, user_input) -> None:
        self.user_input = self.default_input
        self.user_input.update(user_input)
        # grestart = pathlib.Path(self.user_input['project_dir']) / self.user_input['gfilename']
        # # if not grestart.exists():
        # #     raise FileNotFoundError('restart file not found')
        # self.user_input['gfilename'] = str(grestart)
        self.tools = self.user_input['analysis_tools']

    def check():
        pass

    def get_analysis_tool():
        pass
    
    def set_path_to_restart_file(self):
        pass

    def format_template(self):

        template = self.delta_kick_template.format(**self.user_input)

        # if self.tools == "dipolemoment":
        #     return template
        if self.tools and "wavefunction" in self.tools:
            tlines = template.splitlines()
            tlines[4] = "from gpaw.lcaotddft.wfwriter import WaveFunctionWriter"
            tlines[9] = "WaveFunctionWriter(td_calc, 'wf.ulm')"
            template = """\n""".join(tlines)
            #return template
        
        return template

    @staticmethod
    def get_network_job_cmd():

        job_script = """
##### LITESOPH Appended Comands###########

cd TD_Delta/
mpirun -np 4  python3 td.py\n"""
        return job_script
       
class GpawRTLCAOTddftLaser:
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""

    NAME = 'tdlaser.py'

    input_data_files = [('gfilename', 'gs.gpw')]

    default_input = {
                'propagate': (20, 150),
                'module': None,
                'laser':None,
                'electric_pol': None,
                'dipole_file':'dm.dat',
                'wavefunction_file':'wf.ulm',
                'analysis_tools': None,
                'gfilename':'gs.gpw',
                'propagator':None,
                'td_potential': None,
                'fxc':None,
                'parallel': None,
                'txt':'tdx.out',
                'td_gpw':'td.gpw'}

    analysis_tools = [
        ('DipoleMomentWriter()','from gpaw.lcaotddft.dipolemomemtwriter import DipoleMomentWriter'),
        ('WaveFunctionWriter()','from gpaw.lcaotddft.wfwriter import WaveFunctionWriter')

    ]
    
    external_field_template = """ 
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.external import ConstantElectricField
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter
from gpaw.lcaotddft.laser import GaussianPulse
pulse = GaussianPulse({strength},{time0},{frequency},{sigma}, 'sin')
ext = ConstantElectricField(Hartree / Bohr,{electric_pol} )
td_potential = {{'ext': ext, 'laser': pulse}}
td_calc = LCAOTDDFT(filename='{gfilename}',
                    td_potential=td_potential,
                    txt='{txt}')
DipoleMomentWriter(td_calc, '{dipole_file}')
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{td_gpw}', mode='all')
    """

    def __init__(self, user_input) -> None:
        self.user_input = self.default_input
        self.user_input.update(user_input)
        # grestart = pathlib.Path(self.user_input['project_dir']) / self.user_input['gfilename']
        # # if not grestart.exists():
        # #     raise FileNotFoundError('restart file not found')
        # self.user_input['gfilename'] = str(grestart)
        self.laser = self.user_input['laser']
        self.tools = self.user_input['analysis_tools']
        self.td_potential = self.user_input['td_potential']

    def check():
        pass
    
    def pulse(pulse_para: dict)-> str:
        para = {
            'strength':None,
            'time0':None,
            'frequency': None,
            'sigma': None,
            'sincos':'sin',
            'stoptime':'np.inf'
        }
        para.update(pulse_para)
        
        pulse = "pulse = GaussianPulse({strength},{time0},{frequency},{sigma},{sincos},{stoptime})".format(**para)
        return pulse

    def get_analysis_tool():
        pass

    def mask():
        pass
    
    def format_template(self):

        if self.laser is None:
            template = self.external_field_template.format(**self.user_input)

            if self.tools == "dipolemoment":
                return template
            elif self.tools == "wavefunction":
                tlines = template.splitlines()
                tlines[8] = "WaveFunctionWriter(td_calc, 'wf.ulm')"
                template = """\n""".join(tlines)
                return template

        elif self.laser is not None and self.td_potential == True:
           self.user_input.update(self.laser)
           template = self.external_field_template.format(**self.user_input)
           return template 

    @staticmethod
    def get_network_job_cmd():

        job_script = """
##### LITESOPH Appended Comands###########

cd TD_Laser/
mpirun -np 4  python3 tdlaser.py\n"""
        return job_script


class GpawSpectrum:

    NAME = 'spec.py'

    input_data_files = [('moment_file', 'dm.dat')]

    default_input = {
                   'moment_file': 'dm.dat',
                   'spectrum_file': 'spec.dat',
                   'folding': 'Gauss',
                   'width' : 0.2123,
                   'e_min' : 0.0,
                   'e_max' : 30.0,
                   'delta_e' : 0.05
                }

    dm2spec="""
from gpaw.tddft.spectrum import photoabsorption_spectrum
photoabsorption_spectrum('{moment_file}', '{spectrum_file}',folding='{folding}', width={width},e_min={e_min}, e_max={e_max}, delta_e={delta_e})
"""
  
    def __init__(self, input_para: dict) -> None:
        self.dict = self.default_input
        self.dict.update(input_para)
        
    def format_template(self):
        template = self.dm2spec.format(**self.dict)
        return template

    @staticmethod
    def get_network_job_cmd():

        job_script = """
##### LITESOPH Appended Comands###########

cd Spectrum/
python3 spec.py\n"""  
        return job_script


class GpawCalTCM:

    NAME = 'tcm.py'
    
    input_data_file = [('gfilename', 'gs.gpw'),
                        ('wfilename', 'wf.ulm')]

    default_input = {
                    'gfilename' : 'gs.gpw',
                    'wfilename' : 'wf.ulm',
                    'frequencies' : [],
                    'name' : " "
                    }

    tcm_temp = """
from litesoph.simulations.gpaw.gpawtcm import TCMGpaw
freq = {{frequencies}}
ground_state = '{gfilename}'
wave_function = '{wfilename}'
tcm = TCMGpaw(ground_state, wave_function ,freq,'{name}')
tcm.run()
tcm.plot()
"""

    tcm_temp1 = """

from gpaw.lcaotddft import LCAOTDDFT

from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
from gpaw.tddft.folding import frequencies

import numpy as np
from matplotlib import pyplot as plt

from gpaw import GPAW
from gpaw.tddft.units import au_to_eV
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.densitymatrix import DensityMatrix
from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
from gpaw.lcaotddft.tcm import TCMPlotter

# Read the ground-state file
td_calc = LCAOTDDFT('{gfilename}')

frequency_list = {frequency_list}

# Attach analysis tools
dmat = DensityMatrix(td_calc)
freqs = frequencies(frequency_list, 'Gauss', 0.1)
fdm = FrequencyDensityMatrix(td_calc, dmat, frequencies=freqs)

# Replay the propagation
td_calc.replay(name='{wfilename}', update='none')

# Store the density matrix
fdm.write('fdm.ulm')

from gpaw import GPAW
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition

# Calculate ground state with full unoccupied space
calc = GPAW('{gfilename}', txt=None).fixed_density(nbands='nao', txt='unocc.out')
calc.write('unocc.gpw', mode='all')

# Construct KS electron-hole basis
ksd = KohnShamDecomposition(calc)
ksd.initialize(calc)
ksd.write('ksd.ulm')

# Load the objects
calc = GPAW('unocc.gpw', txt=None)
ksd = KohnShamDecomposition(calc, 'ksd.ulm')
dmat = DensityMatrix(calc)
fdm = FrequencyDensityMatrix(calc, dmat, 'fdm.ulm')

plt.figure(figsize=(8, 8))


def do(w):
    # Select the frequency and the density matrix
    rho_uMM = fdm.FReDrho_wuMM[w]
    freq = fdm.freq_w[w]
    frequency = freq.freq * au_to_eV
    print(f'Frequency: {{frequency:.2f}} eV')
    print(f'Folding: {{freq.folding}}')

    # Transform the LCAO density matrix to KS basis
    rho_up = ksd.transform(rho_uMM)

    # Photoabsorption decomposition
    dmrho_vp = ksd.get_dipole_moment_contributions(rho_up)
    weight_p = 2 * freq.freq / np.pi * dmrho_vp[0].imag / au_to_eV * 1e5
    print(f'Total absorption: {{np.sum(weight_p):.2f}} eV^-1')

    # Print contributions as a table
    table = ksd.get_contributions_table(weight_p, minweight=0.1)
    print(table)
    with open(f'table_{{frequency:.2f}}.txt', 'w') as f:
        f.write(f'Frequency: {{frequency:.2f}} eV\\n')
        f.write(f'Folding: {{freq.folding}}\\n')
        f.write(f'Total absorption: {{np.sum(weight_p):.2f}} eV^-1\\n')
        f.write(table)

    # Plot the decomposition as a TCM
    de = 0.01
    energy_o = np.arange(-3, 0.1 + 1e-6, de)
    energy_u = np.arange(-0.1, 3 + 1e-6, de)
    plt.clf()
    plotter = TCMPlotter(ksd, energy_o, energy_u, sigma=0.1)
    plotter.plot_TCM(weight_p)
    plotter.plot_DOS(fill={{'color': '0.8'}}, line={{'color': 'k'}})
    plotter.plot_TCM_diagonal(freq.freq * au_to_eV, color='k')
    plotter.set_title(f'Photoabsorption TCM {name} at {{frequency:.2f}} eV')

    # Check that TCM integrates to correct absorption
    tcm_ou = ksd.get_TCM(weight_p, ksd.get_eig_n()[0],
                         energy_o, energy_u, sigma=0.1)
    print(f'TCM absorption: {{np.sum(tcm_ou) * de ** 2:.2f}} eV^-1')

    # Save the plot
    plt.savefig(f'tcm_{{frequency:.2f}}.png')

def run (frequency_list):
    for i, item enumerate(frequency_list)
        do(i)

    """

    def __init__(self, input_para:dict) -> None:
        self.dict = self.default_input
        self.dict.update(input_para)

    def format_template(self):
        template = self.tcm_temp1.format(**self.dict)
        return template


class GpawLrTddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}




class GpawInducedDensity:
    """Contains template to calculate induced density from density matrix."""

