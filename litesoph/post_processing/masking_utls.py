from pathlib import Path
import re
from litesoph.utilities import units
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.constants import e,h
from math import pi
import numpy, scipy.optimize
from litesoph.post_processing.fourier import Fourier 
from scipy.signal import find_peaks



def timeperiod_by_maxima(input_envelope_data,directionaxis:int,timeaxis=0):
    """ function to calculate timeperiod thorough maxima method"""

    time = input_envelope_data[:,timeaxis] 
    envelope = input_envelope_data[:,directionaxis] 

    peaks, _ = find_peaks(envelope, prominence=1) 
    time_at_peaks= np.take(time, peaks, 0)
    timeperiod= np.diff(time_at_peaks).mean() if len(time_at_peaks) !=0 else print("No timeperiod found, try some other method")
        
    return timeperiod

def timeperiod_by_fit_sin(input_envelope_data, directionaxis:int, timeaxis=0):

    '''Fit sin to the input time sequence, and return  "time period" '''
    time = input_envelope_data[:,timeaxis] 
    envelope = input_envelope_data[:,directionaxis] 

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

def timeperiod_by_fourier_transform(input_envelope_data, time_window, directionaxis:int, timeaxis=0):
        """ function to calculate timeperiod thorough fourier transformation """

        total_timestep=len(input_envelope_data) 

        time = input_envelope_data[:,timeaxis] 
        signal_func = input_envelope_data[:,directionaxis] 
        signal_func=signal_func-np.mean(signal_func)

        delt = time[1]-time[0]

        fourier_func=Fourier(total_timestep,delt,time_window)
        fourier_transformed  = fourier_func.transform(signal_func[:])
        freq =(fourier_transformed[0])
        signal_transformed   =np.abs(fourier_transformed[1])

        freq = freq[range(int(len(freq)/2))]
        signal_transformed = signal_transformed[range(int(len(signal_transformed)/2))]

        signal_transformed_max=max(signal_transformed)
        freq_max_pos=np.where(signal_transformed == signal_transformed_max)
        freq_max=float(freq[freq_max_pos]) 
        fourier_timeperiod= (1/freq_max) if freq_max !=0 else print("No freq found, try some other method")
        time_period_for_envelope= 2*fourier_timeperiod
 
        return time_period_for_envelope


def get_direction(direction:list):
    pol_map = {'0' : 'x', '1' : 'y', '2': 'z'}
    index = direction.index(1)
    return index , pol_map[str(index)]

class MaskedDipoleAnaylsis:

    def __init__(self, sim_total_dm : Path, task_dir: Path) -> None:
        self.sim_total_dm = sim_total_dm
        self.task_dir = task_dir
        self.total_dm_file = self.task_dir / 'total_dm.dat'
        self.masked_dm_file = self.task_dir / 'masked_dm.dat'
        self.unmasked_dm_file = self.task_dir / 'unmasked_dm.dat'
        self.energy_coupling_file = self.task_dir / 'energy_coupling.dat'
        self.energy_coupling_data = [['Region', 'Direction', 'Energy Coupling']]

    def extract_dipolemoment_data(self):
    
        data = np.loadtxt(str(self.sim_total_dm),comments="#")

        data[:,0] *= units.au_to_fs
        dm_total = data[:,[0,2,3,4]]
        dm_masked = data[:,[0,5,6,7]]
        dm_unmasked=dm_total-dm_masked
        
        np.savetxt(str(self.total_dm_file), dm_total)
        np.savetxt(str(self.masked_dm_file), dm_masked)
        np.savetxt(str(self.unmasked_dm_file), dm_unmasked)

    def get_region_dm_file(self, region: str):
        region = region.lower()
        if region == 'masked':
            return self.masked_dm_file
        elif region == 'unmasked':
            return self.unmasked_dm_file
        elif region == 'total':
            return self.total_dm_file


    def cal_energy_coupling_constant(self, region:str, axis:list,timeperiodmethod="fourier_method", time_window=100):
        
        datafile = self.get_region_dm_file(region)
        index, pol = get_direction(axis)
        envelope_file = self.task_dir / f'envelope_{region.lower()}_dm_{pol}.dat'
        dat=np.loadtxt(str(datafile), comments='#')  
        total_time_steps=len(dat) 
        time= dat[:,0] 
        signal_func = dat[:,index+1] 
        delt = time[1]-time[0]
        fourier_func=Fourier(total_time_steps,delt,time_window)
        envelope_amp  = fourier_func.envelope(signal_func[:])
        amplitude_envelope=envelope_amp[0]

        envelope_data=np.stack((time, amplitude_envelope), axis=-1) 
        np.savetxt(str(envelope_file), envelope_data)

        if timeperiodmethod=="fourier_method":
           timeperiod = timeperiod_by_fourier_transform(envelope_data, time_window,1)
        
        elif timeperiodmethod=="Sine_method":
             timeperiod=timeperiod_by_fit_sin(envelope_data, 1)
        
        elif timeperiodmethod =="maxima_method":
             timeperiod=timeperiod_by_maxima(envelope_data, 1)

        sec_to_fs= 10**(-15)
        coupling_constant_in_eV= h/(timeperiod*sec_to_fs*e)

        return coupling_constant_in_eV
        
    
    def get_energy_coupling(self, region:str, axis:str):
        energy_coupling = self.cal_energy_coupling_constant(region, axis)
        _ , pol = get_direction(axis)
        for item in self.energy_coupling_data:
            if region in item and pol in item:
                self.energy_coupling_data.remove(item)

        self.energy_coupling_data.append([region, pol, str(energy_coupling)])
        txt = []
        for data in self.energy_coupling_data:
            txt.append('    '.join(data))
        txt = '\n'.join(txt)
        with open(self.energy_coupling_file, 'w+') as f:
                f.write(txt)
        return txt

    def plot(self,region:str, axis:list, envelope=False):

        datafile = self.get_region_dm_file(region)
        index, pol = get_direction(axis)
        dm_dat=np.loadtxt(str(datafile))
        time=dm_dat[:,0]  
        dm_signal=dm_dat[:,index +1]
        title = 'Dipole Moment Plot'
        x_label = 'Time (fs)'
        y_label = 'Dipole moment'
        plt.rcParams["figure.figsize"] = (10,8)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
            
        plt.plot(time, dm_signal,label=f'{region}_{pol}')
        if envelope:
            envelope_file = self.task_dir / f'envelope_{region.lower()}_dm_{pol}.dat'
            if envelope_file.exists():
                env_dat=np.loadtxt(str(envelope_file))
                amplitude_envelope=env_dat[:,1]
                plt.plot(time, amplitude_envelope,label='envelope')
            else:
                raise FileNotFoundError('Envelope not yet completed.')
        plt.legend(loc ="upper right")
        img = datafile.with_suffix('.png')
        plt.savefig(img)
        return plt





    
