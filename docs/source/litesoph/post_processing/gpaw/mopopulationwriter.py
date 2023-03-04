import os
import numpy as np
from gpaw.lcaotddft.observer import TDDFTObserver
from ase.utils import IOContext
from gpaw.tddft.units import au_to_as


class MoPopulationWriter(TDDFTObserver):

    def __init__(self, paw, dmat, ksd, filename,
                force_new_file= False, interval=1):
        TDDFTObserver.__init__(self, paw, interval)
        self.ioctx = IOContext()
        self.dmat = dmat
        self.ksd = ksd
        if paw.niter == 0 or force_new_file:
            self.fd = self.ioctx.openfile(filename, comm=paw.world, mode='w')
            #self._write_header(paw)
        else:
            #self.read_header(filename)
            self.fd = self.ioctx.openfile(filename, comm=paw.world, mode='a')

    def _write(self, line):
        self.fd.write(line)
        self.fd.flush()

    def calculate_mo_population(self, paw):
        rho_uMM = self.dmat.get_density_matrix((paw.niter, paw.action))
        u = 0
        rho_MM = rho_uMM[u]
        C0S_nM = self.ksd.C0S_unM[u].astype(rho_MM.dtype, copy=True)
        rho_nn = np.dot(np.dot(C0S_nM, rho_MM), C0S_nM.T.conj())
        mo_pop = np.real(rho_nn.diagonal())
        return mo_pop

    def _write_mo_pop(self, paw):
        time = paw.time
        mo_pop = self.calculate_mo_population(paw)
        line = ["{:.16e}".format(pop) for pop in mo_pop]
        line.insert( 0, f"{time * au_to_as: 9.2f}")
        line = '        '.join(line) + '\n'
        self._write(line)


    def _update(self, paw):
        self._write_mo_pop(paw)

    def __del__(self):
        self.ioctx.close()