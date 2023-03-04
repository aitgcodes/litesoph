 
from gpaw.lcaotddft import LCAOTDDFT
import numpy as np
from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter

td_calc = LCAOTDDFT(filename='/home/huma/repo/litesoph/example/Na2/GS/gs.gpw',txt='tdx.out')

DipoleMomentWriter(td_calc, 'dm.dat')

# Kick
td_calc.absorption_kick([0.0, 0.0, 1e-05])
# Propagate"
td_calc.propagate(10.0, 2000.0)
# Save the state for restarting later"
td_calc.write('/home/huma/repo/litesoph/example/Na2/Spectrum/td.gpw', mode='all')
    