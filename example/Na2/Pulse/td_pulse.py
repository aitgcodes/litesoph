 
import numpy as np
from ase.units import Hartree, Bohr
from gpaw.external import ConstantElectricField
from gpaw.lcaotddft import LCAOTDDFT
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter
from gpaw.lcaotddft.laser import GaussianPulse
pulse = GaussianPulse(1e-5,21.97e3,2.03,1.24, 'sin')
ext = ConstantElectricField(Hartree / Bohr,[0.0, 0.0, 1.0] )
td_potential = {'ext': ext, 'laser': pulse}
td_calc = LCAOTDDFT(filename='/home/huma/repo/litesoph/example/Na2/GS/gs.gpw',
                    td_potential=td_potential,
                    txt='/home/huma/repo/litesoph/example/Na2/Pulse/tdpulse.out')
DipoleMomentWriter(td_calc, 'dmpulse.dat')
# Propagate"
td_calc.propagate(10.0, 3000)
# Save the state for restarting later"
td_calc.write('/home/huma/repo/litesoph/example/Na2/Pulse/tdpulse.gpw', mode='all')
    