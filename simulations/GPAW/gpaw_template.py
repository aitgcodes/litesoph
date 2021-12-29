import pathlib
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

        if user_param['mode'] not in ['fd', 'lcao', 'pw'] and  user_param['engine'] == 'gpaw':
            raise ValueError('This mode is not compatable with gpaw use fd, lcao or paw')
        
        if user_param['engine'] == 'gpaw':
            return  True
        else:
            return False

    def user2gpaw(self, user_input: Dict[str, Any], default_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """converts general user given parameters to gpaw specific parameters."""
        import os
        parameters = default_parameters
        
        for key in user_input.keys():
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
                'wavefunction_file':'wf.ulm',
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
from gpaw.lcaotddft.wfwriter import WaveFunctionWriter
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
td_calc.write('{td_out}', mode='all')
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

def write_laser(laser_input:dict, filename, directory):

    from gpaw.lcaotddft.laser import GaussianPulse
    import numpy as np

    filename = filename + ".dat"
    filename = pathlib.Path(directory) / filename
    pulse = GaussianPulse(float(laser_input['strength']), float(laser_input['time0']),float(laser_input['frequency']), float(laser_input['sigma']), laser_input['sincos'])
    pulse.write(filename, np.arange(laser_input['range']))

class Cal_TCM:

    def __init__(self, gfilename, wfilename, frequencies:list, name:str) -> None:
        self.gfilename = gfilename
        self.wfilename = wfilename
        self.frequencies = frequencies
        self.name = name

    def create_frequency_density_matrix(self):
        #fdm_filename = fdm_filename + ".ulm"
        from gpaw.lcaotddft import LCAOTDDFT
        from gpaw.lcaotddft.densitymatrix import DensityMatrix
        from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
        from gpaw.tddft.folding import frequencies

        td_calc = LCAOTDDFT(self.gfilename)

        dmat = DensityMatrix(td_calc)
        freqs = frequencies(self.frequencies, 'Gauss', 0.1)
        fdm = FrequencyDensityMatrix(td_calc, dmat, frequencies=freqs)

        td_calc.replay(name=self.wfilename, update='none')

        fdm.write('fdm.ulm')
        return fdm
        
    def read_unocc(self):
        from gpaw import GPAW
        calc = GPAW(self.gfilename, txt=None)
        return calc

    def cal_unoccupied_states(self,calc):
        calc = calc.fixed_density(nbands='nao', txt='unocc.out')
        calc.write('unocc.gpw', mode='all')
        return calc
    
    def create_ks_basis(self, calc):
        from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
        ksd = KohnShamDecomposition(calc)
        ksd.initialize(calc)
        ksd.write('ksd.ulm')
        return ksd

    def plot_tcm(self, ksd, fdm,fnum, title):
        import numpy as np
        from matplotlib import pyplot as plt
        from gpaw.tddft.units import au_to_eV
        from gpaw.lcaotddft.tcm import TCMPlotter

        rho_uMM = fdm.FReDrho_wuMM[fnum]
        freq = fdm.freq_w[fnum]
        frequency = freq.freq * au_to_eV

        rho_up = ksd.transform(rho_uMM)

        dmrho_vp = ksd.get_dipole_moment_contributions(rho_up)
        weight_p = 2 * freq.freq / np.pi * dmrho_vp[0].imag / au_to_eV * 1e5

        de = 0.01
        energy_o = np.arange(-3, 0.1 + 1e-6, de)
        energy_u = np.arange(-0.1, 3 + 1e-6, de)
        plt.clf()
        plotter = TCMPlotter(ksd, energy_o, energy_u, sigma=0.1)
        plotter.plot_TCM(weight_p)
        plotter.plot_DOS(fill={'color': '0.8'}, line={'color': 'k'})
        plotter.plot_TCM_diagonal(freq.freq * au_to_eV, color='k')
        plotter.set_title(f'Photoabsorption TCM of {title} at {frequency:.2f} eV')

        # Check that TCM integrates to correct absorption
        tcm_ou = ksd.get_TCM(weight_p, ksd.get_eig_n()[0],
                            energy_o, energy_u, sigma=0.1)
        print(f'TCM absorption: {np.sum(tcm_ou) * de ** 2:.2f} eV^-1')
        plt.show()
    
    def run_calc(self):
        calc_dict ={}
        fdm = self.create_frequency_density_matrix()
        calc = self.read_unocc()
        calc = self.cal_unoccupied_states(calc)
        ksd = self.create_ks_basis(calc)
        calc_dict['fdm'] = fdm
        calc_dict['ksd'] = ksd    
        return(calc_dict)

    def plot(self,calc_dict,fnum):
        self.plot_tcm(calc_dict['ksd'],calc_dict['fdm'],fnum, self.name)



class LrTddft:
    """This class contains the template  for creating gpaw 
    scripts for  linear response tddft calculations."""

    user_input = {}




class InducedDensity:
    """Contains template to calculate induced density from density matrix."""

