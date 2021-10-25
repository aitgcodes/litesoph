

class ground_state_template:
    """This class contains the template  for creating gpaw 
    scripts for ground state calculations."""
    
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
    parallel=)
layer.calc = calc
energy = layer.{properties}
calc.write('{work_dir}/gs.gpw', mode='all')

    """
    
class rt_tddft_template:
    """This class contains the template  for creating gpaw 
    scripts for  real time tddft calculations."""

    td_template = """
    # Time-propagation calculation
    from gpaw.lcaotddft import LCAOTDDFT
    from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter
    # Read converged ground-state file
    td_calc = LCAOTDDFT('gs.gpw', txt='tdx.out')
    # Attach any data recording or analysis tools
    DipoleMomentWriter(td_calc, 'dm.dat')
    # Kick

    td_calc.absorption_kick([", str(Ex), ", ", str(Ey), ", ",  str(Ez),"])
    # Propagate"
    td_calc.propagate(", str(dt), ", ", str(Nt),")
    # Save the state for restarting later"
    td_calc.write('{directory}td.gpw', mode='all')
    """
    
class lr_tddft_template:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""


class spectrum_cal_template:
    """This class contains the template  for creating gpaw 
    scripts for tddft calculations calculation."""

    spectrum_template = """
    from gpaw.tddft.spectrum import photoabsorption_spectrum
    photoabsorption_spectrum('dm.dat', 'spec_x.dat', width=0.09, e_min=0.0, e_max=15.0, delta_e=0.05)"""