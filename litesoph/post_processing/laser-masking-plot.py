from litesoph.utilities import units
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.constants import e,h
from math import pi
import numpy, scipy.optimize



def extract_dipolemoment_data(source_data,dm_total_file:str,dm_masked_file:str,dm_unmasked_file:str):
    
    data = np.loadtxt(source_data,comments="#")

    data[:,0] *= units.au_to_fs
    dm_total = data[:,[0,2,3,4]]
    dm_masked = data[:,[0,5,6,7]]
    dm_unmasked=dm_total-dm_masked
    
    np.savetxt(f"{str(dm_total_file)}.dat", dm_total)
    np.savetxt(f"{str(dm_masked_file)}.dat", dm_masked)
    np.savetxt(f"{str(dm_unmasked_file)}.dat", dm_unmasked)


def fit_sin(time, envelope):

    '''Fit sin to the input time sequence, and return  "period" '''
    time = numpy.array(time)
    envelope = numpy.array(envelope)
    ff = numpy.fft.fftfreq(len(time), (time[1]-time[0]))   
    Fyy = abs(numpy.fft.fft(envelope))
    guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])  
    guess_amp = numpy.std(envelope) * 2.**0.5
    guess_offset = numpy.mean(envelope)
    guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * numpy.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, time, envelope, p0=guess)
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    time_period= 1./f
    time_period_for_envelope= 2*time_period
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    
    return time_period_for_envelope


def Energy_coupling_constant(datafilename, envelope_outfile, directionaxis:int, timeperiodmethod:str,timeaxis=0):
    
    dat=np.loadtxt(datafilename)  
    t=dat[:,timeaxis]  
    signal=dat[:,directionaxis]  

    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)  
    envelope_data=np.stack((t, amplitude_envelope), axis=-1) 
    np.savetxt(f"{str(envelope_outfile)}.dat", envelope_data)


    timeperiod = timeperiodmethod(t, amplitude_envelope)
    
    sec_to_fs= 10**(-15)

    coupling_constant_in_eV= h/(timeperiod*sec_to_fs*e)

    return coupling_constant_in_eV


def envelope_plot(dm_data,env_data,imgfile:str,dm_column:int,title, x_label,y_label,env_column=1,time_column=0):
    
    dm_dat=np.loadtxt(dm_data)
    env_dat=np.loadtxt(env_data)


    t=dm_dat[:,time_column]  
    dm_signal=dm_dat[:,dm_column]
    amplitude_envelope=env_dat[:,env_column]

    
     
    plt.rcParams["figure.figsize"] = (10,8)
    plt.title(title, fontsize = 25)
    plt.xlabel(x_label, fontsize=15, weight = 'bold')
    plt.ylabel(y_label, fontsize=15, weight = 'bold')
        
    plt.xticks(fontsize=14,  weight = 'bold')
    plt.yticks(fontsize=14, weight = 'bold')
    
    plt.grid() 

    plt.plot(t, dm_signal,label='dipole moment')
    plt.plot(t, amplitude_envelope,label='envelope')
    plt.legend(loc ="upper right")

    plt.savefig(imgfile)
    plt.show()
    
