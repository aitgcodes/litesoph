import numpy as np
import cmath
import copy as cp

from ase.io import write
from gpaw import GPAW
from gpaw.tddft.units import au_to_eV
from gpaw.poisson import PoissonSolver
from gpaw.fd_operators import Gradient
from gpaw.utilities.extend_grid import extended_grid_descriptor, \
    extend_array, deextend_array #, move_atoms

class GenPlasmonicityIndex():
    '''
      Used to generate induced potential given the Fourier Transformed 
      induced density at various frequencies. Using the induced potential
      and density methods below also compute the 
      Generalized Plasmonicity Index according to
      ACS Nano 2017, 11, 7, 7321-7335
    '''

    def __init__(self, dmat, fdm, atoms, extfield=[1.0,0.0,0.0],wrange=None,extend=True,deextend=True):

        self.dtype = complex
        self.extend = extend
        self.extend_N_cd = 3 * np.ones((3, 2), int)
        self.gridrefinement = 2
        self.gradient_n = 3
        self.poisson = 'fast'
        self.deextend = deextend
        self.extfield = extfield
        #print(self.extfield)
        self.hasphi = False

        self.frequency = []

        self.get_induced_density(dmat,fdm,atoms,wrange)
        #self.wrange = wrange
        self.nw = len(self.wrange)
        #print(self.nw)

        self.nv = 3  # dimensionality of the space

    def get_induced_density(self,dmat,fdm,atoms,wrange):
    ## Computes and sets the frequency dependent induced density
    ## in the supplied range of frequencies.
    ## The values of the frequencies in eV in the range as well as
    ## the grid object is also initialized here.
    ## Cube files for the densities are also printed.

    # Set the range of frequencies for which induced quantitites will be calculated
        if wrange is None:
           wrange = range(len(fdm.freq_w))
           self.wrange = wrange
        
        self.rho_wg = []
        gd = dmat.density.finegd
        self.gd = gd
        
        for w in wrange: 
    # Select the frequency and the density matrix
            rho_MM = fdm.FReDrho_wuMM[w][0]
            freq = fdm.freq_w[w]
            frequency = freq.freq * au_to_eV
            self.frequency.append(frequency)

    # Induced density
            rho_gi = dmat.get_density([rho_MM.imag])
            rho_gr = dmat.get_density([rho_MM.real])
            rho_g = rho_gr + 1j * rho_gi
            self.rho_wg.append(rho_g)

    # Calculate dipole moment for reference
            dm_v = dmat.density.finegd.calculate_dipole_moment(rho_gi, center=True)
            absorption = 2 * freq.freq / np.pi * dm_v[0] / au_to_eV * 1e5

    # Save as a cube file and print absorption
            R_g = gd.collect(rho_gi)
            if gd.comm.rank == 0:
               print(f'Frequency: {frequency:.2f} eV')
               print(f'Folding: {freq.folding}')
               write(f'ind_{frequency:.2f}.cube', atoms, data=R_g)
               print(f'Total absorption: {absorption:.2f} eV^-1')

    def calculate_induced_potential(self,pot_only=False):


        #### These lines are heavily inspired from GPAW's inducedfield_base.py
        #### and other related routines which specialize to our application
        #### Grid extension and deextension is enforced. Grid refinement is 
        #### temporarily skipped. Poisson Solver is assumed to be 'fast' always.
        #### Induced electric field and field enhancement are also calculated
        #### optionally if pot_only=False.

        rho_wg = cp.deepcopy(self.rho_wg)
        gd = self.gd
        ## Check if nw matches with the stored one.
        nw = len(rho_wg)
        assert nw == self.nw, \
                   "Mismatch in number of frequencies at instantiation and at call to induced_potential."

        # Skip grid refinement 
        # Extend grid for accuracy
        if self.extend:
           oldgd = gd
           egd, cell_cv, move_c = \
               extended_grid_descriptor(gd, extend_N_cd=self.extend_N_cd)
           rho_we = egd.zeros((self.nw,), dtype=self.dtype)
           for w in range(self.nw):
               extend_array(gd, egd, rho_wg[w], rho_we[w])
           rho_wg = rho_we
           gd = egd

        ## Allocate arrays for the induced potential
        phi_wg = gd.zeros((self.nw,), dtype=self.dtype)
       
        if not pot_only:
           ef_wvg = gd.zeros((self.nw, self.nv,), dtype=self.dtype)
           fe_wg = gd.zeros((self.nw,), dtype=float)

        ## Prepare the poisson solver to use
        poissonsolver = PoissonSolver(name=self.poisson) #, eps=1e-20)
        poissonsolver.set_grid_descriptor(gd)

        if pot_only:
           for w in self.wrange:
               self.get_indpot(gd, rho_wg[w], phi_wg[w], poissonsolver=poissonsolver)
        else:
           for w in self.wrange:
               self.calculate_field(gd, rho_wg[w], self.extfield,
                                    phi_wg[w], ef_wvg[w], fe_wg[w],
                                    poissonsolver=poissonsolver,
                                    nv=self.nv)
                                    #gradient_n=self.gradient_n)

        # De-extend grid
        if self.extend and self.deextend:
           rho_wo = oldgd.zeros((self.nw,), dtype=self.dtype)
           phi_wo = oldgd.zeros((self.nw,), dtype=self.dtype)

           for w in self.wrange:
               deextend_array(oldgd, gd, rho_wo[w], rho_wg[w])
               deextend_array(oldgd, gd, phi_wo[w], phi_wg[w])

           phi_wg = phi_wo
           rho_wg = rho_wo

           if not pot_only:
              ef_wvo = oldgd.zeros((self.nw, self.nv,), dtype=self.dtype)
              fe_wo = oldgd.zeros((self.nw,), dtype=float)
     
              for w in self.wrange:
                  deextend_array(oldgd, gd, fe_wo[w], fe_wg[w])
                  for v in range(self.nv):
                      deextend_array(oldgd, gd, ef_wvo[w][v], ef_wvg[w][v])
              ef_wvg = ef_wvo
              fe_wg = fe_wo

           gd = oldgd

        # Store the results
        self.rho_wg = rho_wg
        self.phi_wg = phi_wg
        if not pot_only:
           self.ef_wvg = ef_wvg
           self.fe_wg = fe_wg

        if self.extend:
           self.gd = gd

        self.hasphi = True

    def get_indpot(self, gd, rho_g, phi_g, poissonsolver=None):

        dtype = rho_g.dtype
        yes_complex = dtype == complex
        phi_g[:] = 0.0
        tmp_g = gd.zeros(dtype=float)

        if poissonsolver is None:
            poissonsolver = PoissonSolver(name='fast', eps=1e-20)
            poissonsolver.set_grid_descriptor(gd)
            print("PoissonSolver Reset")

        # Potential, real part
        poissonsolver.solve(tmp_g, rho_g.real.copy())
        phi_g += tmp_g
        # Potential, imag part
        if yes_complex:
           tmp_g[:] = 0.0
           poissonsolver.solve(tmp_g, rho_g.imag.copy())
           phi_g += 1.0j * tmp_g

    def calculate_field(self, gd, rho_g, bgef_v,
                        phi_g, ef_vg, fe_g,  # preallocated numpy arrays
                        poissonsolver,
                        nv=3,
                        gradient_n=3):

        dtype = rho_g.dtype
        yes_complex = dtype == complex

        phi_g[:] = 0.0
        ef_vg[:] = 0.0
        fe_g[:] = 0.0
        tmp_g = gd.zeros(dtype=float)

        # Potential, real part
        poissonsolver.solve(tmp_g, rho_g.real.copy())
        phi_g += tmp_g
        # Potential, imag part
        if yes_complex:
            tmp_g[:] = 0.0
            poissonsolver.solve(tmp_g, rho_g.imag.copy())
            phi_g += 1.0j * tmp_g

        # Gradient
        gradient = [Gradient(gd, v, scale=1.0, n=gradient_n)
                    for v in range(nv)]
        for v in range(nv):
            # Electric field, real part
            gradient[v].apply(-phi_g.real, tmp_g)
            ef_vg[v] += tmp_g
            # Electric field, imag part
            if yes_complex:
                gradient[v].apply(-phi_g.imag, tmp_g)
                ef_vg[v] += 1.0j * tmp_g

        # Electric field enhancement
        tmp_g[:] = 0.0  # total electric field norm
        bgefnorm = 0.0  # background electric field norm
        for v in range(nv):
            tmp_g += np.absolute(bgef_v[v] + ef_vg[v])**2
            bgefnorm += np.absolute(bgef_v[v])**2

        tmp_g = np.sqrt(tmp_g)
        bgefnorm = np.sqrt(bgefnorm)

        fe_g[:] = tmp_g / bgefnorm


    def get_gpi(self,rho,pot,gd,ef):

    #### Computes the numerator and denominator in the GPI formula
    #### Numerator: gpinum = | \int rho(r,w)* phi(r,w) dr|
    #### Denominator: gpiden = | Efield . \int rho(r,w)* r dr|
        #gpi_eps = 1e-8
        gpinum = abs(gd.integrate(pot,rho))
        dmr = gd.calculate_dipole_moment(rho.real, center=True)
        dmi = gd.calculate_dipole_moment(rho.imag, center=True)

        gpiden = abs(np.dot(dmr,ef)+1j*np.dot(dmi,ef))

        #print(gpinum,gpiden)

        return (gpinum,gpiden)

    def calculate_gpi(self):

        ef = np.array(self.extfield)
        if not self.hasphi:
           self.calculate_induced_potential()
        gpi = []
        for w in range(self.nw):
            (gpinum,gpiden) = self.get_gpi(self.rho_wg[w],self.phi_wg[w],self.gd,ef)
            gpival = gpinum/gpiden
            gpi.append(gpival)
            if self.gd.comm.rank == 0:
               print(f'{self.frequency[w]:.2f} : {gpival:.6f}')

        return gpi

    def write_indpot(self,atoms,pot_only=False):

    #### Writes the induced potential to a cube file 
    #### Also, optionally writes the field enhancement
    #### to a cube file if pot_only=False.

        for w in self.wrange:
            phi_g = cp.deepcopy(self.phi_wg[w])
            V_g = self.gd.collect(phi_g)
            if self.gd.comm.rank == 0:
               write(f'indpot_{self.frequency[w]:.2f}.cube', atoms, data=V_g)
            if not pot_only:
               fe_g = cp.deepcopy(self.fe_wg[w])
               F_g = self.gd.collect(fe_g)
               if self.gd.comm.rank == 0:
                  write(f'field_{self.frequency[w]:.2f}.cube', atoms, data=F_g)
