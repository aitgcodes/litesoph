
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
layer = read('/home/huma/repo/litesoph/example/Na2/coordinate.xyz')
layer.center(vacuum=6)

#Ground-state calculation
calc = GPAW(mode='lcao',
    xc='LDA',
    occupations=None,
    poissonsolver= None,
    h=0.3,  # Angstrom
    gpts=None,
    kpts=[(0.0, 0.0, 0.0)],
    nbands= 10,
    charge= 0,
    setups= {},
    basis='dzp',
    spinpol= None,
    filter=None,
    mixer=None,
    eigensolver=None,
    background_charge=None,
    experimental={'reuse_wfs_method': 'paw', 'niter_fixdensity': 0, 'magmoms': None, 'soc': None, 'kpt_refine': None},
    external=None,
    random=False,
    hund=False,
    maxiter=300,
    idiotproof=True,
    symmetry={'point_group': True, 'time_reversal': True, 'symmorphic': True, 'tolerance': 1e-07, 'do_not_symmetrize_the_density': None},  # deprecated
    convergence={'energy': 5e-05, 'bands': 'occupied'},
    verbose=0,
    fixdensity=False,  # deprecated
    dtype=None,  # deprecated
    txt='/home/huma/repo/litesoph/example/Na2/GS/gs.out',
    parallel=None)
layer.calc = calc
energy = layer.get_potential_energy()
calc.write('/home/huma/repo/litesoph/example/Na2/GS/gs.gpw', mode='all')

    