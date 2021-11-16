from typing import Any, Dict
from gpaw import GPAW

class GpawGroundState:
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
energy = layer.get_potential_energy()
calc.write('{work_dir}/gs.gpw', mode='all')

    """
    def check(self, user_param):

        if user_param['mode'] not in ['fd', 'lcao', 'paw'] and  user_param['engine'] == 'gpaw':
            raise ValueError('This mode is not compatable with gpaw use fd, lcao or paw')
        
        if user_param['engine'] == 'gpaw':
            return  True
        else:
            return False

    def user2gpaw(self, user_input: Dict[str, Any], default_parameters: Dict[str, Any]) -> Dict[str, Any]:
        import os
        parameters = default_parameters
        
        for key in user_input:
            if key not in ['tolerance','convergance','box'] and user_input[key] is not None:
                parameters[key] = user_input[key]
                            
            if key == 'work_dir' and user_input[key] is None:
                print('The project directory is not specified so the current directory will be taken as working directory')
                parameters.update(key = user_input['work_dir'][os.getcwd()])

            if key == 'geometry' and user_input[key] is None:
                raise ValueError('The structure file is not found')
        return parameters

     
class RtLcaoTddft:
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""

    user_input = {'absorption_kick': None,
                'propagate': None,
                'directroy': None}

    analysis_tools = [
        'DipoleMomentWriter()',
        'WaveFunctionWriter()',

    ]
    
    lcao_tddft_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.dipolemomemtwriter import DipoleMomentWriter
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
    

    
class LrTddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}




class InducedDensity:
    """Contains template to calculate induced density from density matrix."""

