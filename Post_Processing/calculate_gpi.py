'''
 This script calculates the frequency dependent induced 
 potential and the Generalized Plasmonicity Index of the
 chosen excitations in a system. Cube files for imaginary
 part of the induced potential are written and the GPI
 values are printed out.
'''

import sys
import numpy as np
import cmath

from ase.io import write
from gpaw import GPAW
from gpaw.tddft.units import au_to_eV
from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
from densitymatrix_VS import DensityMatrix
from plasmons import GenPlasmonicityIndex as GPI

# External field is as per the original excitation read in as argument
extfield=[float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])]

#This calculation starts after an unoccupied states calculation is done
#usually for  KSD calculation.
# Load the calculator and density matrix objects
calc = GPAW('Na2_gs_unocc.gpw', txt=None)
calc.initialize_positions()  # Initialize in order to calculate density
dmat = DensityMatrix(calc)
fdm = FrequencyDensityMatrix(calc, dmat, 'Na2_fdm.ulm')
gd = dmat.density.gd


# Choose the range of frequencies to be probed as a list of
# indices. Requires the knowledge of the spectrum.
# No wrange is set then the code automatically calculates
# the GPI for all frequencies in the original fdm list.
#wrange=range(2)

plasmon=GPI(dmat,fdm,calc.atoms,extfield,extend=True)
plasmon.calculate_induced_potential()
plasmon.write_indpot(calc.atoms)
gpi=plasmon.calculate_gpi()
