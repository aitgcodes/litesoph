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
from numpy import inf

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
    txt='{directory}/gs.out',
    parallel=None)
layer.calc = calc
energy = layer.get_potential_energy()
calc.write('{directory}/gs.gpw', mode='all')

    """
    def __init__(self, user_input) -> None:
        pass

    def check(self, user_param)-> bool:
        """checks whether user given input parameters is compatable with with gpaw ground state calculation"""

        if user_param['mode'] not in ['fd', 'lcao', 'paw'] and  user_param['engine'] == 'gpaw':
            raise ValueError('This mode is not compatable with gpaw use fd, lcao or paw')
        
        if user_param['engine'] == 'gpaw':
            return  True
        else:
            return False

    def user2gpaw(self, user_input: Dict[str, Any], default_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """converts general user given parameters to gpaw specific parameters."""
        import os
        parameters = default_parameters
        
        for key in user_input:
            if key not in ['tolerance','convergance','box'] and user_input[key] is not None:
                parameters[key] = user_input[key]

            if key == 'geometry' and user_input[key] is None:
                raise ValueError('The structure file is not found')
        return parameters

    def format_template(self, para:dict):
        template = self.gs_template.format(**para)
        return template
     
class RtLcaoTddft:
    """This class contains the template  for creating gpaw 
    scripts for  real time lcao tddft calculations."""

    default_input = {'absorption_kick': [1e-5, 0.0, 0.0],
                'propagate': (20, 150),
                'module': None,
                'laser':None,
                'electric_pol': None,
                'dipole_file':'dm.dat',
                'analysis_tools': None,
                'filename':'gs.gpw',
                'propagator':None,
                'td_potential': None,
                'fxc':None,
                'parallel': None,
                'txt':'tdx.out',
                'td_out':'td.gpw'}

    analysis_tools = [
        ('DipoleMomentWriter()','from gpaw.lcaotddft.dipolemomemtwriter import DipoleMomentWriter'),
        ('WaveFunctionWriter()','from gpaw.lcaotddft.wfwriter import WaveFunctionWriter')

    ]
    
    delta_kick_template = """ 
from gpaw.lcaotddft import LCAOTDDFT
import numpy as np
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter

td_calc = LCAOTDDFT(filename='{filename}',txt='{txt}')

DipoleMomentWriter(td_calc, '{dipole_file}')

# Kick
td_calc.absorption_kick({absorption_kick})
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{directory}/{td_out}', mode='all')
    """
    
    external_field_template = """ 
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.external import ConstantElectricField
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter
from gpaw.lcaotddft.laser import GaussianPulse
pulse = GaussianPulse({strength},{time0}e3,{frequency},{sigma}, 'sin')
ext = ConstantElectricField(Hartree / Bohr,{electric_pol} )
td_potential = {{'ext': ext, 'laser': pulse}}
td_calc = LCAOTDDFT(filename='{filename}',
                    td_potential=td_potential,
                    txt='{txt}')
DipoleMomentWriter(td_calc, '{dipole_file}')
# Propagate"
td_calc.propagate{propagate}
# Save the state for restarting later"
td_calc.write('{directory}/{td_out}', mode='all')
    """

    def __init__(self, user_input) -> None:
        self.user_input = user_input
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
            template = self.delta_kick_template.format(**self.user_input)
            return template
        elif self.laser is not None and self.td_potential == True:
           self.user_input.update(self.laser)
           template = self.external_field_template.format(**self.user_input)
           return template
    
class LrTddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}




class InducedDensity:
    """Contains template to calculate induced density from density matrix."""

