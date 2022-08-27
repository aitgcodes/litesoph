data = {
    'ground_state': {
        'import':[  'from ase.io import read, write',
                    'from gpaw import GPAW',
                    'from numpy import inf']
    },
    'rt_tddft': {
        'lcao':{
            'import':[  'from gpaw.lcaotddft import LCAOTDDFT',
                        'from gpaw.lcaotddft.diplemomentwriter import DipoleMomentWriter']
        }, 
        'fd' : { 'import':[ 'from gpaw.lcaotddft import LCAOTDDFT',
                            'from gpaw.lcaotddft.diplemomentwriter import DipoleMomentWriter']            
        }
    }
}

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
    txt='{txt_out}')
atoms.calc = calc
energy = atoms.get_potential_energy()
calc.write('{gpw_out}', mode='all')
"""

delta_kick_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
import numpy as np
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter

td_calc = LCAOTDDFT(filename='{gfilename}',txt='{txt_out}')


td_calc.absorption_kick({absorption_kick})
# Propagate"
td_calc.propagate{propagate}
td_calc.write('{gpw_out}', mode='all')
"""

external_field_template = """ 
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.external import ConstantElectricField
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter
from gpaw.lcaotddft.laser import GaussianPulse
pulse = GaussianPulse({strength},{time0},{frequency},{sigma}, 'sin')
ext = ConstantElectricField(Hartree / Bohr,{polarization} )
td_potential = {{'ext': ext, 'laser': pulse}}
td_calc = LCAOTDDFT(filename='{gfilename}',
                    td_potential=td_potential,
                    txt='{txt_out}')

# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{gpw_out}', mode='all')
"""

dm2spec="""
from gpaw.tddft.spectrum import photoabsorption_spectrum
photoabsorption_spectrum('{dm_file}', '{spectrum_file}',folding='{folding}', width={width},e_min={e_min}, e_max={e_max}, delta_e={delta_e})
"""
mo_population ="""
from gpaw import GPAW
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
from gpaw.lcaotddft.densitymatrix import DensityMatrix
from litesoph.post_processing.gpaw.mopopulationwriter import MoPopulationWriter

calc = GPAW('{gfilename}', txt=None).fixed_density(nbands='nao', txt='unocc.out')
calc.write('unocc.gpw', mode='all')

td_calc = LCAOTDDFT('unocc.gpw', txt=None)

dmat = DensityMatrix(td_calc)
ksd = KohnShamDecomposition(td_calc)
ksd.initialize(td_calc)
MoPopulationWriter(td_calc, dmat, ksd, filename='{mopop_file}')
# Replay the propagation
td_calc.replay(name='{wfile}', update='none')

"""
tcm_temp = """
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
td_calc = LCAOTDDFT('{gfilename}', txt=None)

frequency_list = {frequency_list}

# Attach analysis tools
dmat = DensityMatrix(td_calc)
freqs = frequencies(frequency_list, 'Gauss', 0.1)
fdm = FrequencyDensityMatrix(td_calc, dmat, frequencies=freqs)

# Replay the propagation
td_calc.replay(name='{wfile}', update='none')

# Store the density matrix
fdm.write('fdm.ulm')


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

task_map = {
    'ground_state': gs_template,
    'rt_tddft' :{'delta': delta_kick_template,
                    'laser': external_field_template},
    'spectrum' : dm2spec,
    'tcm' : tcm_temp,
    'mo_population': mo_population
}
def assemable_rt(**kwargs):
    tools = kwargs.pop('analysis_tools', None)
    if 'laser' in kwargs:
        laser = kwargs.pop('laser')
        kwargs.update(laser)
        template = external_field_template.format(**kwargs)
    else:
       
        template = delta_kick_template.format(**kwargs)

    tlines = template.splitlines()
    
    if 'dipole' in tools:
        tlines.insert(0, 'from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter')
        tlines.insert(-5, f"DipoleMomentWriter(td_calc, '{kwargs.get('dm_file', 'dipole.dat')}', interval={kwargs.get('output_freq', 1)})")
        
    if "wavefunction" in tools:  
        tlines.insert(0, "from gpaw.lcaotddft.wfwriter import WaveFunctionWriter")
        tlines.insert(-5, f"WaveFunctionWriter(td_calc, '{kwargs.get('wfile', 'wf.ulm')}', interval={kwargs.get('output_freq', 1)})")
        
    if 'mo_population' in tools:
        tlines.insert(0, 'from gpaw.lcaotddft.densitymatrix import DensityMatrix')
        tlines.insert(0, 'from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition')
        tlines.insert(0, 'from litesoph.simulations.gpaw.mopopulationwriter import MoPopulationWriter')
        tlines.insert(-5, "dmat = DensityMatrix(td_calc)")
        tlines.insert(-5, "ksd = KohnShamDecomposition(td_calc)")
        tlines.insert(-5, "ksd.initialize(td_calc)")
        tlines.insert(-5,  f"MoPopulationWriter(td_calc, dmat, ksd, filename='{kwargs.get('mopop_file', 'mo_population.dat')}', interval={kwargs.get('output_freq', 1)})")
    
    template = """\n""".join(tlines)
    
    return template

def gpaw_create_input(**kwargs):
    task_name = kwargs.pop('task', 'ground_state')

    if 'rt_tddft' in task_name:
        return assemable_rt(**kwargs) 

    if 'ground_state' == task_name:
        default_param.update(kwargs)
        kwargs = default_param
    template = task_map.get(task_name)
    template = template.format(**kwargs)
    return template