from gpaw import GPAW

class gpaw_ground_state:
    """This class contains the default parameters and the template for creating gpaw 
    scripts for ground state calculations."""
    default_param = GPAW.default_parameters

    gs_template = """
from ase.io import read, write
from ase import Atoms
from ase.parallel import paropen
from gpaw.poisson import PoissonSolver
from gpaw.eigensolvers import CG
from gpaw import GPAW, FermiDirac
from gpaw import Mixer, MixerSum, MixerDif
from gpaw.lcao.eigensolver import DirectLCAO

# Molecule or nanostructure
layer = read('{geometry}')
layer.center(vacuum={vacuum})

#Ground-state calculation
calc = GPAW(mode='{mode}',
    xc='{xc}',
    occupations={occupations},
    poissonsolver= {poissonsolver},
    h={h},  # Angstrom
    gpts={gpts},
    kpts={kpts},
    nbands= {nbands},
    charge= {charge},
    setups= {setups},
    basis='{basis}',
    spinpol= {spinpol},
    filter={filter},
    mixer={mixer},
    eigensolver={eigensolver},
    background_charge={background_charge},
    experimental={experimental},
    external={external},
    random={random},
    hund={hund},
    maxiter={maxiter},
    idiotproof={idiotproof},
    symmetry={symmetry},  # deprecated
    convergence={convergence},
    verbose={verbose},
    fixdensity={fixdensity},  # deprecated
    dtype={dtype},  # deprecated
    txt='{work_dir}/gs.out',
    parallel=None)
layer.calc = calc
energy = layer.{properties}
calc.write('{work_dir}/gs.gpw', mode='all')

    """
    
class rt_lcao_tddft:
    """This class contains the template  for creating gpaw 
    scripts for  real time tddft calculations."""

    user_input = {}

    lcao_tddft_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
{import_module}
td_calc = LCAOTDDFT('gs.gpw', txt='tdx.out')

DipoleMomentWriter(td_calc, 'dm.dat')
{analysis_tools}
# Kick
td_calc.absorption_kick([{absorption_kick}])
# Propagate"
td_calc.propagate({propagate})
# Save the state for restarting later"
td_calc.write('{directory}td.gpw', mode='all')
    """
    analysis_tools = [
        'DipoleMomentWriter()',
        'WaveFunctionWriter()',

    ]
    
class lr_tddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}




class induced_density:
    """Contains template to calculate induced density from density matrix."""

