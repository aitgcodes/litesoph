
from litesoph.config import get_mpi_command
from litesoph.simulations.gpaw import gpaw_data
from litesoph.simulations.esmd import Task
from pathlib import Path

class GpawGroundState(Task):
    """This class contains the default parameters and the template for creating gpaw 
    scripts for ground state calculations."""
    task_data = gpaw_data.ground_state

    task_name = 'ground_state'

    NAME = Path(gpaw_data.ground_state['inp']).name

    path = str(Path(gpaw_data.ground_state['inp']).parent)

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
    occupations = {occupations},
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
    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('gpaw',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.user_input['geometry']= str(Path(project_dir.name) / gpaw_data.ground_state['req'][0])
        

    def create_template(self):
        self.template = self.gs_template.format(**self.user_input)
       
    
    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
        

class GpawRTLCAOTddftDelta(Task):
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""
    
    task_data = gpaw_data.rt_tddft_delta
    task_name = 'rt_tddft_delta'
    NAME = Path(task_data['inp']).name

    path = Path(task_data['inp']).parent

    default_param = {'absorption_kick': [1e-5, 0.0, 0.0],
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

DipoleMomentWriter(td_calc, '{dipole_file}', interval={output_freq})

# Kick
td_calc.absorption_kick({absorption_kick})
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{td_gpw}', mode='all')
    """

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('gpaw',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.user_input['gfilename'] = str(Path(project_dir.name) / gpaw_data.rt_tddft_delta['req'][0])
        self.tools = self.user_input['analysis_tools']


    def create_template(self):

        template = self.delta_kick_template.format(**self.user_input)

        if self.tools and "ksd" in self.tools:
            tlines = template.splitlines()
            tlines[4] = "from gpaw.lcaotddft.wfwriter import WaveFunctionWriter"
            tlines[9] = f"WaveFunctionWriter(td_calc, 'wf.ulm', interval={self.user_input['output_freq']})"
            template = """\n""".join(tlines)
        
        self.template =  template

    def create_local_cmd(self, *args):
        return self.engine.create_command(*args)

    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script
        

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

    def get_network_job_cmd(self, np):
        job_script = f"""
##### LITESOPH Appended Comands###########

cd {self.path}
mpirun -np {np:d}  python3 {self.NAME}\n"""
        return job_script
       
class GpawRTLCAOTddftLaser(Task):
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""
    
    task_data = gpaw_data.rt_tddft_laser
    task_name = 'rt_tddft_laser'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)


    default_param = {
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

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('gpaw',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.user_input['gfilename'] = str(Path(project_dir.name) / gpaw_data.rt_tddft_laser['req'][0])
        self.laser = self.user_input['laser']
        self.tools = self.user_input['analysis_tools']
        self.td_potential = self.user_input['td_potential']

    
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

    
    def create_template(self):

        if self.laser is None:
            template = self.external_field_template.format(**self.user_input)

            if self.tools == "dipolemoment":
                self.template =  template
            elif self.tools == "wavefunction":
                tlines = template.splitlines()
                tlines[8] = "WaveFunctionWriter(td_calc, 'wf.ulm')"
                template = """\n""".join(tlines)
                self.template =  template

        elif self.laser is not None and self.td_potential == True:
            self.user_input.update(self.laser)
            template = self.external_field_template.format(**self.user_input)
            self.template =  template 

    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script
        
    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

    
class GpawSpectrum(Task):
    
    task_data = gpaw_data.spectrum
    task_name = 'spectrum'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)

    default_param = {
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
  
    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('gpaw',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.pol =  status.get_status('gpaw.rt_tddft_delta.param.pol_dir')
        self.user_input['spectrum_file'] = f'spec_{str(self.pol[1])}.dat'
        self.user_input['moment_file']= str(Path(project_dir.name) / gpaw_data.spectrum['req'][0])
        
    def create_template(self):
        self.template = self.dm2spec.format(**self.user_input)
       
    
    def prepare_input(self):
        self.create_template()
        self.write_input()

    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np, self.NAME,path=lpath)
        
        self.job_script = "\n".join(job_script)
        return self.job_script
        

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

    def plot(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        spec_file = self.task_data['spectra_file'][self.pol[0]]
        file = Path(self.project_dir) / spec_file
        img = file.parent / f"spec_{self.pol[1]}.png"
        plot_spectrum(file,img,0, self.pol[0]+1, "Energy (in eV)", "Strength(in /eV)")

class GpawCalTCM(Task):

    task_data = gpaw_data.tcm
    task_name = 'tcm'
    NAME = Path(task_data['inp']).name

    path = str(Path(task_data['inp']).parent)

    default_param = {
                    'gfilename' : 'gs.gpw',
                    'wfilename' : 'wf.ulm',
                    'frequency_list' : [],
                    'name' : " ",
                    'axis_limit': 10
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
    energy_o = np.arange(-{axis_limit:.2f}, 0.1 + 1e-6, de)
    energy_u = np.arange(-0.1, {axis_limit:.2f} + 1e-6, de)
    plt.clf()
    plotter = TCMPlotter(ksd, energy_o, energy_u, sigma=0.1)
    plotter.plot_TCM(weight_p)
    plotter.plot_DOS(fill={{'color': '0.8'}}, line={{'color': 'k'}})
    plotter.plot_TCM_diagonal(freq.freq * au_to_eV, color='k')
    plotter.set_title(f'Photoabsorption TCM at {{frequency:.2f}} eV')

    # Check that TCM integrates to correct absorption
    tcm_ou = ksd.get_TCM(weight_p, ksd.get_eig_n()[0],
                         energy_o, energy_u, sigma=0.1)
    print(f'TCM absorption: {{np.sum(tcm_ou) * de ** 2:.2f}} eV^-1')

    # Save the plot
    plt.savefig(f'tcm_{{frequency:.2f}}.png')

def run(frequency_list):
    for i, item in enumerate(frequency_list):
        do(i)
run(frequency_list)

    """

    def __init__(self, status, project_dir, lsconfig, user_input) -> None:
        super().__init__('gpaw',status, project_dir, lsconfig)
        self.user_input = self.default_param
        self.user_input.update(user_input)
        self.user_input['gfilename']= str(Path(project_dir.name)  / gpaw_data.tcm['req'][0])
        self.user_input['wfilename']= str(Path(project_dir.name)  / gpaw_data.tcm['req'][1])

    def create_template(self):
        self.template = self.tcm_temp1.format(**self.user_input)
        
    def create_job_script(self, np, remote_path = None, remote=False) -> str:
        """Create the bash script to run the job and "touch Done" command to it"""
        job_script = super().create_job_script()

        if remote_path:
            rpath = Path(remote_path) / self.project_dir.name / self.path
            job_script = self.engine.create_command(job_script, np=1, filename =self.NAME,path=rpath,remote=True)
            job_script.append(self.remote_job_script_last_line)
        else:
            lpath = self.project_dir / self.path
            job_script = self.engine.create_command(job_script, np=1,filename=self.NAME,path=lpath)
        self.job_script = "\n".join(job_script)
        return self.job_script

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)

    def plot(self):
        from PIL import Image
       
        for item in self.user_input.get('frequency_list'):
            img_file = Path(self.project_dir) / 'gpaw' / 'TCM' / f'tcm_{item:.2f}.png'
            
            image = Image.open(img_file)
            image.show()

class GpawLrTddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}


class GpawInducedDensity:
    """Contains template to calculate induced density from density matrix."""

