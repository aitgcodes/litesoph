
from ase.io import read, write
from gpaw import GPAW
from numpy import inf

# Molecule or nanostructure
atoms = read('../../coordinate.xyz')
atoms.center(vacuum=6.0)


#Ground-state calculation
calc = GPAW(
    mode='lcao',
    xc='PBE',
    occupations = {'name': '', 'width': 0.0},
    h=0.3,  # Angstrom
    gpts=None,
    kpts=[(0.0, 0.0, 0.0)],
    nbands= None,
    charge= 0,
    setups= {},
    basis={'default': 'dzp'},
    spinpol= False,
    filter=None,
    mixer=None,
    hund=False,
    maxiter=500,
    symmetry={'point_group': False},  
    convergence={'energy': 1e-06, 'density': 1e-05, 'eigenstates': 4e-08, 'bands': 'occupied'},
    txt='gs.out')
atoms.calc = calc
energy = atoms.get_potential_energy()
calc.write('gs.gpw', mode='all')

