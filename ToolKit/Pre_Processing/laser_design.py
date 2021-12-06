import sys
import math

# Calculates the half-width in time of the laser pulse and centre of the pulse
# given the FWHM in frequency space, the amplitude of pulse of time origin, location of time origin
# Input arguments (in that order) are -log(E(0)), time origin of pulse and FWHM in frequency space of pulse
# Output units are the same as Input units

inval = 6.0
tin = 0.0 

if len(sys.argv) > 2:
	inval=float(sys.argv[1])
	tin=float(sys.argv[2])
	fwhm=float(sys.argv[3])
else:
	fwhm=float(sys.argv[1])

tau_0 = 2.0*math.sqrt(2*math.log(2.0))/fwhm
t0 = tin + math.sqrt(2.0)*tau_0*math.sqrt(inval)

print("sigma time : ", tau_0)
print("pulse centre :", t0)
