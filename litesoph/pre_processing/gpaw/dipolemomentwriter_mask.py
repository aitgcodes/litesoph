import re
import numpy as np

from gpaw.lcaotddft.observer import TDDFTObserver


def convert_repr(r):
    # Integer
    try:
        return int(r)
    except ValueError:
        pass
    # Boolean
    b = {repr(False): False, repr(True): True}.get(r, None)
    if b is not None:
        return b
    # String
    s = r[1:-1]
    if repr(s) == r:
        return s
    raise RuntimeError('Unknown value: %s' % r)


class DipoleMomentWriter(TDDFTObserver):
    version = 1

    def __init__(self, paw, filename, center=False, density='comp',
                 interval=1,mask=None):
        TDDFTObserver.__init__(self, paw, interval)
        self.master = paw.world.rank == 0
        self.mask = mask
        if paw.niter == 0:
            # Initialize
            self.do_center = center
            self.density_type = density
            if self.master:
                self.fd = open(filename, 'w')
        else:
            # Read and continue
            self.read_header(filename)
            if self.master:
                self.fd = open(filename, 'a')

    def _write(self, line):
        if self.master:
            self.fd.write(line)
            self.fd.flush()

    def _write_header(self, paw):
        if paw.niter != 0:
            return
        line = '# %s[version=%s]' % (self.__class__.__name__, self.version)
        if self.mask is not None:
            line += ('(center=%s, density=%s, Focus Region)\n' %
                     (repr(self.do_center), repr(self.density_type)))
        else:    
            line += ('(center=%s, density=%s)\n' %
                     (repr(self.do_center), repr(self.density_type)))
                     
        line += ('# %15s %15s %22s %22s %22s\n' %
                 ('time', 'norm', 'dmx', 'dmy', 'dmz'))
        self._write(line)


    def read_header(self, filename):
        with open(filename, 'r') as f:
            line = f.readline()
        m_i = re.split("[^a-zA-Z0-9_=']+", line[2:])
        assert m_i.pop(0) == self.__class__.__name__
        for m in m_i:
            if '=' not in m:
                continue
            k, v = m.split('=')
            v = convert_repr(v)
            if k == 'version':
                assert v == self.version
                continue
            # Translate key
            k = {'center': 'do_center', 'density': 'density_type'}[k]
            setattr(self, k, v)

    def _write_kick(self, paw):
        time = paw.time
        kick = paw.kick_strength
        line = '# Kick = [%22.12le, %22.12le, %22.12le]; ' % tuple(kick)
        line += 'Time = %.8lf\n' % time
        self._write(line)

    def calculate_dipole_moment(self, gd, rho_g, center=True):

        import copy

        if center:
            center_v = 0.5 * gd.cell_cv.sum(0)
        else:
            center_v = np.zeros(3, dtype=float)
        r_vg = gd.get_grid_point_coordinates()
        dm_v = np.zeros(3, dtype=float)
   
        rho_gm = copy.deepcopy(rho_g)
        if self.mask is not None:
           maskgd = self.mask.create(gd)
           rho_gm = np.multiply(maskgd,rho_gm)
        
        for v in range(3):
            dm_v[v] = - gd.integrate((r_vg[v] - center_v[v]) * rho_gm)
        return dm_v

    def _write_dm(self, paw):
        time = paw.time
        density = paw.density
        if self.density_type == 'comp':
            rho_g = density.rhot_g
            gd = density.finegd
        elif self.density_type == 'pseudo':
            rho_g = density.nt_sg.sum(axis=0)
            gd = density.finegd
        elif self.density_type == 'pseudocoarse':
            rho_g = density.nt_sG.sum(axis=0)
            gd = density.gd
        else:
            raise RuntimeError('Unknown density type: %s' % self.density_type)

        norm = gd.integrate(rho_g)

        ##### Compute the dipole moment from the unmasked (illuminated) region
        #dm1 = dm.copy()
        if self.mask is not None:
            if paw.niter == 0:
               self.maskgd = self.mask.create(gd)
            rho_gm = np.multiply(self.maskgd,rho_g) 
            dm = gd.calculate_dipole_moment(rho_gm, center=self.do_center)
        else:
            dm = gd.calculate_dipole_moment(rho_g, center=self.do_center)
            
        line = ('%20.8lf %20.8le %22.12le %22.12le %22.12le' %
                (time, norm, dm[0], dm[1], dm[2]))

        line += '\n'

        self._write(line)

    def _update(self, paw):
        if paw.action == 'init':
            self._write_header(paw)
        elif paw.action == 'kick':
            self._write_kick(paw)
        self._write_dm(paw)

 #   def __del__(self):
 #       if self.master:
 #           self.fd.close()
 #       TDDFTObserver.__del__(self)
