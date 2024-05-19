import numpy as np
from litesoph.utilities.units import as_to_au, eV_to_au, fs_to_eV, au_to_fs
# Calculates the half-width in time of the laser pulse and centre of the pulse
# given the FWHM in frequency space, the amplitude of pulse of time origin, location of time origin
# Input arguments (in that order) are -log(E(0)), time origin of pulse and FWHM in frequency space of pulse
# Output units are the same as Input units

# inval = 6.0
# tin = 0.0 

# if len(sys.argv) > 2:
# 	inval=float(sys.argv[1])
# 	tin=float(sys.argv[2])
# 	fwhm=float(sys.argv[3])
# else:
# 	fwhm=float(sys.argv[1])

# tau_0 = 2.0*math.sqrt(2*math.log(2.0))/fwhm
# t0 = tin + math.sqrt(2.0)*tau_0*math.sqrt(inval)

# print("sigma time : ", tau_0)
# print("pulse centre :", t0)

def laser_design(inval, tin, fwhm):
    """ Calculates half-width and centre of the pulse in time space
    \n given inval: Relative strength at initial time
    \n tin(in au): Time origin
    \n fwhm(in eV): Full Width Half Maximum"""

    import math
    fwhm = fwhm*eV_to_au
    tau_0 = 2.0*math.sqrt(2*math.log(2.0))/float(fwhm)      # in units of au
    t0 = float(tin) + math.sqrt(2.0)*tau_0*math.sqrt(math.log(10)*inval)  # in units of au

    laser = {}
    
    laser['sigma'] = tau_0                   
    laser['time0'] = t0
    return (laser)

class GaussianPulse:
    r"""
    Laser pulse with Gaussian envelope:

    .. math::

        g(t) = s_0 \sin(\omega_0 (t - t_0)) \exp(-\sigma^2 (t - t_0)^2 / 2)


    Parameters
    ----------
    strength: float
        value of :math:`s_0` in atomic units
    time0: float
        value of :math:`t_0` in attoseconds
    frequency: float
        value of :math:`\omega_0` in eV
    sigma: float
        value of :math:`\sigma` in eV
    sincos: 'sin' or 'cos'
        use sin or cos function
    stoptime: float
        pulse is set to zero after this value (in attoseconds)
    """

    def __init__(self, strength, time0, frequency, sigma, sincos='sin',
                 stoptime=np.inf):
        self.dict = dict(name='GaussianPulse',
                         strength=strength,
                         time0=time0,
                         frequency=frequency,
                         sigma=sigma,
                         sincos=sincos)
        self.name = "gaussian"
        self.s0 = strength
        self.t0 = time0 * as_to_au
        self.omega0 = frequency * eV_to_au
        self.sigma = sigma * eV_to_au
        self.stoptime = stoptime * as_to_au
        assert sincos in ['sin', 'cos']
        self.sincos = sincos

    def strength(self, t):
        """
        Return the value of the pulse :math:`g(t)`.

        Parameters
        ----------
        t
            time in atomic units

        Returns
        -------
        The value of the pulse.
        """
        s = self.s0 * np.exp(-0.5 * self.sigma**2 * (t - self.t0)**2)
        if self.sincos == 'sin':
            s *= np.sin(self.omega0 * (t - self.t0))
        else:
            s *= np.cos(self.omega0 * (t - self.t0))
        flt = t < self.stoptime

        return s * flt

    def derivative(self, t):
        """
        Return the derivative of the pulse :math:`g'(t)`.

        Parameters
        ----------
        t
            time in atomic units

        Returns
        -------
        The derivative of the pulse.
        """
        dt = t - self.t0
        s = self.s0 * np.exp(-0.5 * self.sigma**2 * dt**2)
        if self.sincos == 'sin':
            s *= (-self.sigma**2 * dt * np.sin(self.omega0 * dt) +
                  self.omega0 * np.cos(self.omega0 * dt))
        else:
            s *= (-self.sigma**2 * dt * np.cos(self.omega0 * dt) +
                  -self.omega0 * np.sin(self.omega0 * dt))
        return s

    def fourier(self, omega):
        r"""
        Return Fourier transform of the pulse :math:`g(\omega)`.

        Parameters
        ----------
        omega
            frequency in atomic units

        Returns
        -------
        Fourier transform of the pulse.
        """
        s = (self.s0 * np.sqrt(np.pi / 2) / self.sigma *
             np.exp(-0.5 * (omega - self.omega0)**2 / self.sigma**2) *
             np.exp(1.0j * self.t0 * omega))
        if self.sincos == 'sin':
            s *= 1.0j
        return s

    def todict(self):
        return self.dict
    
    def write(self, fname, time_t):
        """
        Write the values of the pulse to a file.

        Parameters
        ----------
        fname
            filename
        time_t
            times in attoseconds
        """
        time_t = time_t * as_to_au
        strength_t = self.strength(time_t)
        derivative_t = self.derivative(time_t)
        fmt = '%12.6f %20.10e %20.10e'
        header = '{:^10} {:^20} {:^20}'.format('time', 'strength',
                                               'derivative')
        np.savetxt(fname, np.stack((time_t, strength_t, derivative_t)).T,
                   fmt=fmt, header=header)

class DeltaPulse:
    """ strength :au, time0: as, total_time:fs
        """
    def __init__(self, strength, time0,total_time:float = None,stoptime = np.inf):
        self.dict = dict(name='DeltaLaser',
                         strength=strength,
                         time0=time0)
        
        self.name = "delta"
        self.s0 = strength
        self.t0 = time0 * as_to_au
        self.stoptime = stoptime * as_to_au
        self.total_time = total_time

    def strength(self, t):
        """
        Return the value of the pulse :math:`δ(t)`.

        Parameters
        ----------
        t
            time in atomic units

        Returns
        -------
        The value of the pulse.
        """
        # time_array = np.arange(self.total_time*1e3)
        # strength_array = np.full_like(time_array, 0.0)

        # for i in range(len(time_array)):
        #     time_array[i]
        #     delta = time_array[i]- self.t0
        #     if abs(delta) == 0:
        #         strength_array[i] = self.s0
        #         break
        # return strength_array

        if hasattr(t, "__iter__"):
            return (np.abs(np.array(t) - self.t0) <= 1e-5).astype(int) * self.s0

        return self.s0 if abs(t - self.t0) <= 1e-5 else 0

    def todict(self):
        return self.dict


class Laser(object):
    def __init__(self):
        pass

    def strength(self, time):
        return 0.0

    def derivative(self, time):
        return 0.0

    def fourier(self, omega):
        return 0.0

    def write(self, fname, time_t):
        """
        Write the values of the pulse to a file.

        Parameters
        ----------
        fname
            filename
        time_t
            times in attoseconds
        """

        time_t = time_t * as_to_au
        strength_t = self.strength(time_t)
        derivative_t = self.derivative(time_t)
        fmt = '%12.6f %20.10e %20.10e'
        header = '{:^10} {:^20} {:^20}'.format('time', 'strength',
                                               'derivative')
        np.savetxt(fname, np.stack((time_t, strength_t, derivative_t)).T,
                   fmt=fmt, header=header)



class GaussianDeltaPulse(Laser):
    r"""
    Laser pulse with Gaussian envelope:

    .. math::

        g(t) = s_0  \exp(-\sigma^2 (t - t_0)^2 / 2)


    Parameters
    ----------
    strength: float
        value of :math:`s_0` in atomic units
    time0: float
        value of :math:`t_0` in attoseconds
    
    
    
    """

    def __init__(self, strength, time0,  sigma=200, 
                 stoptime=np.inf):
        self.dict = dict(name='GaussianDeltaPulse',
                         strength=strength,
                         time0=time0,
  
                         )
        self.s0 = strength
        self.t0 = time0 * as_to_au
        
        self.sigma = sigma * eV_to_au
        self.stoptime = stoptime * as_to_au
        

    def strength(self, t):
        
        s = self.s0 * np.exp(-0.5 * self.sigma**2 * (t - self.t0)**2)
        
        flt = t < self.stoptime

        return s * flt

    def derivative(self, t):
        
        dt = t - self.t0
        s = -(self.sigma)^2*dt*self.s0 * np.exp(-0.5 * self.sigma**2 * dt**2)
        
        return s

    def fourier(self, omega):
        
        s = (self.s0 * np.sqrt(np.pi / 2) / self.sigma *
             np.exp(-0.5 * (omega - self.omega0)**2 / self.sigma**2) *
             np.exp(1.0j * self.t0 * omega))
        if self.sincos == 'sin':
            s *= 1.0j
        return s

    def todict(self):
        return self.dict