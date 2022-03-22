import numpy as np

from gpaw.utilities import pack


def get_density(rho_MM, wfs, density, density_type='comp', u=0):
    if wfs.ksl.using_blacs:
        raise NotImplementedError('Scalapack is not supported')

    rho_G = density.gd.zeros()  ## Total density
    rho_Gs = density.gd.zeros() ## Density from one spin at a time
  
    #### Vardha has modified below
    for iu in range(wfs.nspins):
        kpt = wfs.kpt_u[iu]
        assert kpt.q == 0
        wfs.basis_functions.construct_density(rho_MM.astype(wfs.dtype),
                                              rho_Gs, kpt.q)

        rho_G += rho_Gs

    # Uncomment this if you want to add the static part
    # rho_G += density.nct_G

    if density_type == 'pseudocoarse':
        return rho_G

    rho_g = density.finegd.zeros()
    density.distribute_and_interpolate(rho_G, rho_g)
    rho_G = None

    if density_type == 'pseudo':
        return rho_g

    if density_type == 'comp':
        D_asp = density.atom_partition.arraydict(density.D_asp.shapes_a)
        Q_aL = {}
        for a, D_sp in D_asp.items():
            P_Mi = wfs.P_aqMi[a][kpt.q]
            assert np.max(np.absolute(P_Mi.imag)) == 0
            P_Mi = P_Mi.real
            assert P_Mi.dtype == float
            D_ii = np.dot(np.dot(P_Mi.T.conj(), rho_MM), P_Mi)
            D_sp[:] = pack(D_ii)[np.newaxis, :]
            Q_aL[a] = np.dot(D_sp.sum(axis=0), wfs.setups[a].Delta_pL)
        density.ghat.add(rho_g, Q_aL)
        return rho_g

    raise RuntimeError('Unknown density type: %s' % density_type)


class DensityMatrix(object):

    def __init__(self, paw):
        self.wfs = paw.wfs
        self.density = paw.density
        self.using_blacs = self.wfs.ksl.using_blacs
        self.tag = None

    def zeros(self, dtype):
        ksl = self.wfs.ksl
        if self.using_blacs:
            return ksl.mmdescriptor.zeros(dtype=dtype)
        else:
            return np.zeros((ksl.mynao, ksl.nao), dtype=dtype)

    def _calculate_density_matrix(self, wfs, kpt):
        if self.using_blacs:
            ksl = wfs.ksl
            rho_MM = ksl.calculate_blocked_density_matrix(kpt.f_n, kpt.C_nM)
        else:
            rho_MM = wfs.calculate_density_matrix(kpt.f_n, kpt.C_nM)
            wfs.bd.comm.sum(rho_MM, root=0)
            # TODO: should the sum over bands be moved to
            # OrbitalLayouts.calculate_density_matrix()
        return rho_MM

    def get_density_matrix(self, tag=None):
        if tag is None or self.tag != tag:
            self.rho_uMM = []
            for kpt in self.wfs.kpt_u:
                rho_MM = self._calculate_density_matrix(self.wfs, kpt)
                self.rho_uMM.append(rho_MM)
            self.tag = tag
        return self.rho_uMM

    def get_density(self, rho_uMM=None, density_type='comp'):
        #assert len(self.wfs.kpt_u) == 1, 'K-points not implemented' ## V.S. commented out
        ### V.S. modified
        vardha = len(self.wfs.kpt_u) == 1 or (len(self.wfs.kpt_u) == 2 and self.wfs.nspins == 2)
        assert vardha, 'K-points not implemented'
        ###
        u = 0
        if rho_uMM is None:
            rho_uMM = self.rho_uMM
        return get_density(rho_uMM[u], self.wfs, self.density, density_type, u)
