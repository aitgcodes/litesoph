from pathlib import Path
import copy
from litesoph.common.task import InputError
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

        from scipy import signal
        # Finding peaks for FT envelope data
        peaks = signal.find_peaks(signal_transformed)
        list_peaks = list(peaks[0])
        peak_values = [signal_transformed[i] for i in list_peaks]

        freq_max_pos=np.where(signal_transformed == max(peak_values))
        freq_max=float(freq[freq_max_pos][-1])

        # freq = freq[range(int(len(freq)/2))]
        # signal_transformed = signal_transformed[range(int(len(signal_transformed)/2))]
        
        # signal_transformed_max=max(signal_transformed)
        # freq_max_pos=np.where(signal_transformed == signal_transformed_max)
        # freq_max=float(freq[freq_max_pos])

        try:
            # added conversion of frequency
            f = abs(freq_max)/(2.*numpy.pi)
            fourier_timeperiod= (1/abs(f))
            time_period_for_envelope= 2*fourier_timeperiod
            return time_period_for_envelope
        except ZeroDivisionError as e:
            raise e    


def get_direction(direction:list):
    pol_map = ('x', 'y', 'z')
    index = direction.index(1)
    return index , pol_map[index]

#----------------------Dipole Moment extraction------------------------------------------------

def read_dm(dm_file):
    """Reads single dm file"""
    data = np.loadtxt(str(dm_file),comments="#")
    return data

def read_multiple_dms(list_dm_file):
    """Reads multiple dm files and returns the list of array(dmx,dmy,dmz)"""
    arr_dm = list()
    arr_time = read_dm(list_dm_file[0])[:,0]
    for i,dm_file in enumerate(list_dm_file):        
        # dmx, dmy, dmz
        arr_dm.append(read_dm(dm_file)[:,[2,3,4]])
    return (arr_time,arr_dm)

def combine_focus_region_dm(region_dm_list):
    """List of arrays for x,y,z components of dipole moments with identical shape"""
    dm_combined = np.zeros(shape = region_dm_list[0].shape, dtype=region_dm_list[0].dtype)
    for i,dm in enumerate(region_dm_list):
        dm_combined += dm
    return dm_combined

def complement_dm(total_dm, region_dm):
    """Input arrays for x,y,z components of dipole moments with identical shape,
    Substracts region dipole momennt from the total"""
    _dm = total_dm - region_dm
    return _dm   

class MaskedDipoleAnaylsis:

    def __init__(self, task_dir: Path, focus_region_dms:list, total_dm ='dm.dat') -> None:
        self.task_dir = task_dir
        dm_list = copy.deepcopy(focus_region_dms)
        self.num_masks = len(dm_list)
        if len(dm_list) == 0:
            raise InputError('Masked Dipole File expected')
        else:
            dm_list.insert(0, total_dm)

        _data = read_multiple_dms(list_dm_file=dm_list)
        self.t = _data[0]
        self.dms = _data[1]

        self.envelope_files = []
        self.energy_coupling_file = self.task_dir / 'energy_coupling.dat'
        self.energy_coupling_data = [['Region/Mask_Index','Focus_Value', 'Direction', 'Energy_Coupling(in eV)']]


    def get_dm_complement(self, region_i:int, out_file:str= None):
        """Computes dipole moment complement to specific region and writes to file"""
        import copy
        if out_file is None:
            out_file = 'dm.dat_mask_complement_'+str(region_i)
        out_fpath = self.task_dir / out_file
        total_dm = copy.deepcopy(self.dms[0])
        if (region_i >0):
            try:
                focus_dm = self.dms[region_i]
            except:
               raise IndexError        
        else:
            print('Not a Mask')
            return
        dm_mask_complement = complement_dm(total_dm, focus_dm)
        self.dms.append(dm_mask_complement)
        time_dm_arr = np.stack([self.t, dm_mask_complement[:,0],
                                    dm_mask_complement[:,1],    
                                    dm_mask_complement[:,2]], axis=1)
        np.savetxt(out_fpath, time_dm_arr, header='Focus Complement\n time(au)\tdmx\tdmy\tdmz')

    def get_dm_filename(self, region_i:int=0, focus=None):
        """region_i: int (default gives total dm file name\n
        focus:  True (masked/with mask)
                False (mask_complement)"""
        if region_i == 0:
            focus =None
        if focus is None:
            # Total dipole moment
            suffix = 'total'
            fname = 'dm.dat'
        else:
            if focus is True:
                # suffix = '_masked_'+str(region_i)
                suffix = 'mask_complement_'+str(region_i)
                fname = 'dm.dat_'+suffix
            else:
                # suffix = '_mask_complement_'+str(region_i)
                suffix = 'masked_'+str(region_i)
                fname = 'dm.dat_'+suffix
        return fname, suffix    

    def get_dm_index(self, region_i:int=0, focus=None):
        """region_i: int (default gives total dm file name\n
        focus:  True (masked/with mask)
                False (mask_complement)"""
        if region_i == 0:
            focus = None
            id = region_i
        else:
            if focus is True:
                id = region_i
            else:
                id = region_i+self.num_masks
        return id  

    ###added region_index and focus value 
    def cal_energy_coupling_constant(self, region_i:int, axis:list,focus=None,
                                        # timeperiodmethod="Sine_method",
                                        timeperiodmethod="fourier_method", 
                                        time_window=100):        
        """Computes the envelope for dipole moment data and writes to envelope file,\n
           Computes time_period(in sec), coupling constant(in ev)from envelope data"""
        # Gets the dipole moment filename
        datafile = self.get_dm_filename(region_i, focus)[0]
        suffix = self.get_dm_filename(region_i, focus)[1]

        index, pol = get_direction(axis)
        if region_i is not None:
            envelope_file = self.task_dir / f'envelope_{suffix}_dm_{pol}.dat'
            if str(envelope_file) not in self.envelope_files:
                self.envelope_files.append(str(envelope_file))
         
        time = self.t*units.au_to_fs
        total_time_steps=len(time)
        
        dm_id = self.get_dm_index(region_i, focus) 
        signal_func = self.dms[dm_id][:,index]
        delt = time[1]-time[0]
        fourier_func=Fourier(total_time_steps,delt,time_window)
        envelope_amp  = fourier_func.envelope(signal_func[:])
        amplitude_envelope=envelope_amp[0]

        envelope_data=np.stack((time, amplitude_envelope), axis=-1) 
        envelope_data_to_write = np.stack((self.t, amplitude_envelope), axis=-1) 
        np.savetxt(str(envelope_file), envelope_data_to_write)

        if timeperiodmethod=="fourier_method":
            try:
                timeperiod = timeperiod_by_fourier_transform(envelope_data, time_window,1)
            except ZeroDivisionError:
                timeperiod = None
                error = 'Coupling constant not computed: frequency not found'
                raise Exception(error)
                
        elif timeperiodmethod=="Sine_method":
             timeperiod=timeperiod_by_fit_sin(envelope_data, 1)
        
        elif timeperiodmethod =="maxima_method":
             timeperiod=timeperiod_by_maxima(envelope_data, 1)

        sec_to_fs= 10**(-15)
        if timeperiod is not None:
            coupling_constant_in_eV= h/(timeperiod*sec_to_fs*e)
            return coupling_constant_in_eV
   
    ## -------------------------Methods used at task level----------------------

    def get_energy_coupling(self,axis:str, region_i:int, focus=None):
        """Gets energy coupling for passed dipole moment data,\n
        Writes to coupling data file"""

        try:
            energy_coupling = self.cal_energy_coupling_constant(region_i,axis,focus)  
        except Exception as e:
            energy_coupling = None
            raise e
        if energy_coupling is not None:
            _ , pol = get_direction(axis)

            region_tag = self.get_dm_filename(region_i,focus)[1]
            for item in self.energy_coupling_data:
                if region_tag in item and pol in item:
                    self.energy_coupling_data.remove(item)

            
            self.energy_coupling_data.append([str(region_tag), str(focus), pol, 
                            str(round(float(energy_coupling), 3))])
            txt = []
            for data in self.energy_coupling_data:
                txt.append('\t\t'.join(data))
            txt = '\n'.join(txt)
            with open(self.energy_coupling_file, 'w+') as f:
                    f.write(txt)
            return txt      
                   
    def plot(self,region_focus_axis_env:list):
        """region_focus_axis_env: input list is of tuples of following\n
            region_index: integer (0 : total,
                                1: focus region 1,....)\n
            focus(dipole moment focus region): bool (None/True/False)\n
            axis(pol vector): list; X: [1,0,0],
                                      Y: [0,1,0],
                                      Z : [0,0,1] \n
            env(Envelope function): bool
                                """
        time = self.t*units.au_to_fs
        dm_signal = np.ndarray(shape=(time.shape[0], len(region_focus_axis_env)))
        for i,item in enumerate(region_focus_axis_env):
            region_i = item[0]
            focus = item[1]
            axis = item[2]
            envelope = item[3]
            index, pol = get_direction(axis)

            suffix = self.get_dm_filename(region_i,focus)[1]               
            dm_id = self.get_dm_index(region_i, focus)    
            dm_signal[:,i]=self.dms[dm_id][:,index]
            title = 'Dipole Moment Plot'
            x_label = 'Time (fs)'
            y_label = 'Dipole moment'
            plt.rcParams["figure.figsize"] = (10,8)
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            l_var = f'{suffix}_{pol}'           
            plt.plot(time, dm_signal[:,i],label= l_var)           

            if envelope:
                envelope_file = self.task_dir / f'envelope_{suffix}_dm_{pol}.dat'
                if envelope_file.exists():
                    env_dat=np.loadtxt(str(envelope_file))
                    amplitude_envelope=env_dat[:,1]
                    plt.plot(time, amplitude_envelope,label=f'envelope_{suffix}')
                else:
                    # TODO: Display this in GUI
                    raise FileNotFoundError('Envelope not yet computed.')
            plt.legend(loc ="upper right")
        return plt    

    def plot_dms(self, regions:list, axis:list, envelope=False):
        """Plots extracted dipole moments: [total, region1, region2...]"""

        index, pol = get_direction(axis)
        time=self.t*units.au_to_fs  
        dm_signal = self.dms

        title = 'Dipole Moment Plot'
        x_label = 'Time (fs)'
        y_label = 'Dipole moment'
        plt.rcParams["figure.figsize"] = (10,8)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
            
        for i in regions:
            plt.plot(time, dm_signal[i][:,index],label=f'{i}_{pol}')
        plt.show()
        return plt

#-------------------------------------------------------------------------------------------------------
# class MaskedDipoleAnaylsis:

#     def __init__(self, sim_total_dm : Path, task_dir: Path) -> None:
#         self.sim_total_dm = sim_total_dm
#         self.task_dir = task_dir
#         self.total_dm_file = self.task_dir / 'total_dm.dat'
#         self.masked_dm_file = self.task_dir / 'masked_dm.dat'
#         self.unmasked_dm_file = self.task_dir / 'unmasked_dm.dat'
#         self.energy_coupling_file = self.task_dir / 'energy_coupling.dat'
#         self.energy_coupling_data = [['Region', 'Direction', 'Energy Coupling']]

#     def extract_dipolemoment_data(self):
#         # TODO: replace this
    
#         data = np.loadtxt(str(self.sim_total_dm),comments="#")

#         data[:,0] *= units.au_to_fs
#         dm_total = data[:,[0,2,3,4]]
#         dm_masked = data[:,[0,5,6,7]]
#         ######
#         # Issue with dm_unmasked: substracts the first column: time
#         dm_unmasked=dm_total-dm_masked
        
#         np.savetxt(str(self.total_dm_file), dm_total)
#         np.savetxt(str(self.masked_dm_file), dm_masked)
#         np.savetxt(str(self.unmasked_dm_file), dm_unmasked)

#     def get_region_dm_file(self, region: str):
#         region = region.lower()
#         if region == 'masked':
#             return self.masked_dm_file
#         elif region == 'unmasked':
#             return self.unmasked_dm_file
#         elif region == 'total':
#             return self.total_dm_file


#     def cal_energy_coupling_constant(self, region:str, axis:list,timeperiodmethod="fourier_method", time_window=100):
        
#         datafile = self.get_region_dm_file(region)
#         index, pol = get_direction(axis)
#         envelope_file = self.task_dir / f'envelope_{region.lower()}_dm_{pol}.dat'
#         dat=np.loadtxt(str(datafile), comments='#')  
#         total_time_steps=len(dat) 
#         time= dat[:,0] 
#         signal_func = dat[:,index+1] 
#         delt = time[1]-time[0]
#         fourier_func=Fourier(total_time_steps,delt,time_window)
#         envelope_amp  = fourier_func.envelope(signal_func[:])
#         amplitude_envelope=envelope_amp[0]

#         envelope_data=np.stack((time, amplitude_envelope), axis=-1) 
#         np.savetxt(str(envelope_file), envelope_data)

#         if timeperiodmethod=="fourier_method":
#            timeperiod = timeperiod_by_fourier_transform(envelope_data, time_window,1)
        
#         elif timeperiodmethod=="Sine_method":
#              timeperiod=timeperiod_by_fit_sin(envelope_data, 1)
        
#         elif timeperiodmethod =="maxima_method":
#              timeperiod=timeperiod_by_maxima(envelope_data, 1)

#         sec_to_fs= 10**(-15)
#         coupling_constant_in_eV= h/(timeperiod*sec_to_fs*e)

#         return coupling_constant_in_eV
        
    
#     def get_energy_coupling(self, region:str, axis:str):
#         energy_coupling = self.cal_energy_coupling_constant(region, axis)
#         _ , pol = get_direction(axis)
#         for item in self.energy_coupling_data:
#             if region in item and pol in item:
#                 self.energy_coupling_data.remove(item)

#         self.energy_coupling_data.append([region, pol, str(energy_coupling)])
#         txt = []
#         for data in self.energy_coupling_data:
#             txt.append('    '.join(data))
#         txt = '\n'.join(txt)
#         with open(self.energy_coupling_file, 'w+') as f:
#                 f.write(txt)
#         return txt

#     def plot(self,region:str, axis:list, envelope=False):

#         datafile = self.get_region_dm_file(region)
#         index, pol = get_direction(axis)
#         dm_dat=np.loadtxt(str(datafile))
#         time=dm_dat[:,0]  
#         dm_signal=dm_dat[:,index +1]
#         title = 'Dipole Moment Plot'
#         x_label = 'Time (fs)'
#         y_label = 'Dipole moment'
#         plt.rcParams["figure.figsize"] = (10,8)
#         plt.title(title)
#         plt.xlabel(x_label)
#         plt.ylabel(y_label)
            
#         plt.plot(time, dm_signal,label=f'{region}_{pol}')
#         if envelope:
#             envelope_file = self.task_dir / f'envelope_{region.lower()}_dm_{pol}.dat'
#             if envelope_file.exists():
#                 env_dat=np.loadtxt(str(envelope_file))
#                 amplitude_envelope=env_dat[:,1]
#                 plt.plot(time, amplitude_envelope,label='envelope')
#             else:
#                 raise FileNotFoundError('Envelope not yet computed.')
#         plt.legend(loc ="upper right")
#         img = datafile.with_suffix('.png')
#         plt.savefig(img)
#         return plt





    
