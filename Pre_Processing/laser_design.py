import sys
import math

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


def laser_design(**par):
    import math
    inval = 6.0                            # -log(E(0))
    tin = 0.0                              # location of time origin
    if 'inval' in par.keys():
        inval = float(par['inval'])
    if 'tin' in par.keys():
        tin = float(par['tin'])
    if 'fwhm' in par.keys(): 
        fwhm = float(par['fwhm'])          # FWHM in frequency space

    tau_0 = 2.0*math.sqrt(2*math.log(2.0))/fwhm       # in units of femtosecond
    t0 = tin + math.sqrt(2.0)*tau_0*math.sqrt(inval)  # in units of femtosecond
    tau_0 = tau_0*0.2418                              # converted from fms to eV
    par['sigma_time'] = tau_0    # in units of eV                     
    par['pulse centre'] = t0     # in units of fms
    return(par)

