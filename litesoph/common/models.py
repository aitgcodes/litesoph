from dataclasses import dataclass
import pathlib
import os
import json
from matplotlib import pyplot as plt
import numpy as np
from typing import Any, Dict
from litesoph.common.data_sturcture.data_types import DataTypes as  DT
from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au, au_to_fs, fs_to_au
from litesoph.pre_processing.laser_design import laser_design, GaussianPulse, DeltaPulse

@dataclass
class AutoModeModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['nao', 'fd', 'pw', 'gaussian'], 'default_value': '--choose mode--'},
            'shape' : {'type':DT.string, 'values':["parallelepiped","minimum", "sphere", "cylinder"], 'default_value':"--choose box--"},
            'basis' : {'type':DT.string, 'values':[], 'default_value': ''},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1},
        }


@dataclass
class GpawModel:
    
   ground_state = {
            'mode' : {'type':DT.string, 'values':['nao', 'fd', 'pw'], 'default_value': 'nao'},
            'xc' : {'type':DT.string, 'values':["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"], 'default_value': 'LDA'},
            'basis' : {'type':DT.string, 'values':["dzp","sz","dz","szp","pvalence.dz"], 'default_value': 'dzp'},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0},
            'maxiter' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
            'shape' : {'type':DT.string, 'values':['parallelepiped'], 'default_value':'parallelepiped'},
            'spinpol' : {'type':DT.string, 'values':['None', 'True'], 'default_value':'None'},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1},
            'h' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
            'nbands' :{'type':DT.string, 'min': None, 'max': None, 'default_value': ''},
            'vacuum' :{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
            'energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            'bands' : {'type':DT.string, 'values':['occupied', 'unoccupied', 'all'], 'default_value': 'occupied'},
            'lx' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'ly' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'lz' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'smear' :{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.0},    
            'smearfn' :{'type':DT.string, 'values':["","improved-tetrahedron-method","tetrahedron-method","fermi-dirac","marzari-vanderbilt",], 'default_value': ''},
            'eigenstate': {'type': DT.decimal , 'min': None, 'max': None, 'default_value': 4e-8}
        }

@dataclass
class NWchemModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['gaussian'], 'default_value': 'gaussian'},
            'xc' : {'type':DT.string, 'values':["PBE96","PBE0","B3LYP","PW91", "BP86", "BP91","BHLYP","M05","M05-2X","M06-HF","M08-SO","M011","CAM-B3LYP","LC-BLYP","LC-PBE","LC-wPBE","HSE03","HSE06"], 'default_value': "PBE0"},
            'basis' : {'type':DT.string, 'values':["6-31G","STO-2G","STO-3G","STO-6G","3-21G","3-21G*","6-31G*","6-31G**","6-311G","6-311G*","6-311G**","cc-pVDZ","aug-cc-pvtz"], 'default_value': "6-31G"},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0},
            'maxiter' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
            'multip' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 1},
            'energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            #'tolerances' : ['str','tight'],
            'gradient' :  {'type':DT.decimal, 'min': None, 'max': None, 'default_value':1.0e-4}
        }

@dataclass
class OctopusModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['fd'], 'default_value': 'fd'},
            'var_oct_xc' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 1},
            #'oct_xc' : ['str',''],
            'x' :  {'type':DT.string, 'values':{'lda_x' : ["lda_x","lda_x_rel","lda_x_erf","lda_x_rae"],
                                                    'pbe_x':["gga_x_pbe","gga_x_pbe_r","gga_x_b86","gga_x_herman","gga_x_b86_mgc","gga_x_b88","gga_x_pbe_sol"]}, 'default_value':''},
            'c' :  {'type':DT.string, 'values':{'lda_c' : ["lda_c_pz_mod","lda_c_ob_pz","lda_c_pw","lda_c_ob_pw","lda_c_2d_amgb"],
                                                    'pbe_c':["gga_c_pbe","gga_c_tca","gga_c_lyp","gga_c_p86","gga_c_pbe_sol"]}, 'default_value':''},
            'pseudo' : {'type':DT.string, 'values':{'expt_yes' :[["pseudodojo_lda","hscv_lda","pseudodojo_lda_stringent"],["pseudodojo_pbe","pseudodojo_pbe_stringent","pseudodojo_pbesol","pseudodojo_pbesol_stringent","sg15", "hscv_pbe"]],
                                                    'expt_no':["standard", "hgh_lda_sc","hgh_lda"]}, 'default_value':''},
            'expt' : {'type':DT.string, 'values':['yes','no'], 'default_value':'no'},
            'charge': {'type':DT.integer,'min': None, 'max': None, 'default_value': 0},
            'maxiter' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 300},
            'shape' :{'type':DT.string, 'values':["parallelepiped","minimum", "sphere", "cylinder"], 'default_value':'parallelepiped'},
            'spinpol' :{'type':DT.string, 'values':['unpolarized', 'polarized'], 'default_value':'unpolarized'},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1},
            'h' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},            
            'lx' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'ly' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'lz' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'r' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
            'l' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'dxc' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 3},
            'mixing' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
            'eigen' : {'type':DT.string, 'values':["rmmdiis","plan","cg","cg_new"], 'default_value':'rmmdiis'},
            'smear' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.1},
            'smearfn' : {'type':DT.string, 'values':["semiconducting","fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"], 'default_value':'semiconducting'},
            'unitconv' : {'type':DT.string, 'values':[], 'default_value':''},
            'unit_box' : {'type':DT.string, 'values':['angstrom'], 'default_value':'angstrom'},
            'conv_energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'abs_density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            'abs_eigen' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
            'rel_density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
            'rel_eigen' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
            'extra_states' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 0}
        }
    

class LaserDesignModel:

    laser_input = {

        "strength": {'req' : True, 'type': DT.decimal},
        "inval" : {'req' : True, 'type': DT.decimal},
        #"pol_x": {'req' : True, 'type': DT.integer},
        #"pol_y" : {'req' : True, 'type': DT.integer},
        #"pol_z" : {'req' : True, 'type': DT.integer},
        "fwhm" : {'req' : True, 'type': DT.decimal},
        "frequency" : {'req' : True, 'type': DT.decimal},
        "time_step" : {'req' : True, 'type': DT.decimal},
        "number_of_steps": {'req' : True, 'type': DT.decimal},
        "tin" : {'req' : True, 'type': DT.decimal}
        
        }
    def __init__(self, user_input) -> None:
        self.user_input = user_input
        # range = int(self.user_input['number_of_steps'])* float(self.user_input['time_step'])
        range = self.user_input['total_time']
        self.range = range*1e3
        self.freq = self.user_input['frequency']
        self.strength = self.user_input['strength']

    def create_pulse(self):
        """ creates gaussian pulse with given inval,fwhm value """
        from litesoph.pre_processing.laser_design import GaussianPulse
        from litesoph.pre_processing.laser_design import laser_design
        #from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au
        self.l_design = laser_design(self.user_input['inval'], self.user_input['tin'], self.user_input['fwhm'])      
        self.l_design['frequency'] = self.freq
        self.l_design['strength'] = self.strength
        
        sigma = round(autime_to_eV/self.l_design['sigma'], 2)
        time0 = round(self.l_design['time0']*au_to_as, 2)       

        self.pulse = GaussianPulse(self.strength,float(time0),self.freq, float(sigma), 'sin')        
        
        self.time_t = np.arange(self.range)
        self.strength_t = self.pulse.strength(np.arange(self.range)*as_to_au)
        self.derivative_t = self.pulse.derivative(np.arange(self.range)*as_to_au)

    def write_laser(self,filename):
        """ writes laser pulse to file """
        filename = pathlib.Path(filename) 
        self.pulse.write(filename, np.arange(self.range))

    def plot_time_strength(self):
        """ returns Figure object for (time,strength) in (X,Y) """
        fig = plot(self.time_t*as_to_au*au_to_fs,self.strength_t, 'Time (in fs)', 'Pulse Strength (in au)')
        return fig

    def plot_time_derivative(self):
        """ returns Figure object for (time,derivative) in (X,Y) """
        fig = plot(self.time_t,self.derivative_t, 'Time (in attosec)', 'Time derivative of pulse strength')
        return fig    

    def plot_strength_derivative(self):
        """ returns Figure object for (strength,derivative) in (X,Y) """
        fig = plot(self.strength_t,self.derivative_t, 'Pulse Strength (in au)', 'Time derivative of pulse strength')
        return fig 

def plot(x_data, y_data, x_label, y_label):
    """ returns Figure object given x and y data """
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 6), dpi=100)  
    # figure = Figure(figsize=(5, 3), dpi=100)  
    ax = plt.subplot(1, 1, 1)  
    # ax = figure.add_subplot(1, 1, 1)
    ax.plot(x_data, y_data, 'k')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.show()
 
    # return figure    

class LaserDesignModelNew:

    laser_input = {

        "strength": {'req' : True, 'type': DT.decimal},
        "inval" : {'req' : True, 'type': DT.decimal},
        #"pol_x": {'req' : True, 'type': DT.integer},
        #"pol_y" : {'req' : True, 'type': DT.integer},
        #"pol_z" : {'req' : True, 'type': DT.integer},
        "fwhm" : {'req' : True, 'type': DT.decimal},
        "frequency" : {'req' : True, 'type': DT.decimal},
        "time_step" : {'req' : True, 'type': DT.decimal},
        "number_of_steps": {'req' : True, 'type': DT.decimal},
        "tin" : {'req' : True, 'type': DT.decimal}
        
        }
    def __init__(self,user_input) -> None:
        self.user_input = user_input
    #     # # range = int(self.user_input['number_of_steps'])* float(self.user_input['time_step'])
        # range = self.user_input['total_time']
        # self.range = range*1e3
        # self.freq = self.user_input['frequency']
        # self.strength = self.user_input['strength']
        
    def create_pulse(self):
        user_input = self.user_input
        from litesoph.pre_processing.laser_design import GaussianPulse
        from litesoph.pre_processing.laser_design import laser_design
        from litesoph.pre_processing.laser_design import G_DeltaPulse
        import matplotlib.pyplot as plt
        # print(user_input)
        laser_details =[]
        for n, laser in enumerate (user_input):

            if laser['type']== 'Gaussian':

                freq=laser['frequency']
                strength = laser['strength']
                t_total=laser['total_time']*1e3
                in_value=laser['inval']
                t_in=laser['tin']
                F_fwhm=laser['fwhm']
                
                """ creates gaussian pulse with given inval,fwhm value """
                l_design = laser_design(in_value,t_in,F_fwhm)
                l_design['frequency'] = freq
                l_design['strength'] = strength
                sigma = round(autime_to_eV/l_design['sigma'], 2)
                time0 = round(l_design['time0']*au_to_as, 2)                                 
                l_design['type']= 'Gaussian'     
                       
                
                delay_array=[x * 1e3 for x in [2,4,6,8,10]] 

                # # ##### probe pulse train Generation  ###############
                if n > 0:
                    for  delay in delay_array:

                        pulse=GaussianPulse(strength,float(time0)+delay,freq, float(sigma), 'sin')
                        strength_t = pulse.strength(np.arange(t_total)*as_to_au)
                        plt.plot(time_t*as_to_au*au_to_fs,strength_t)
                else:

                # ##### Generating Pulse by invoking GaussianPulse function
                    pulse = GaussianPulse(strength,float(time0),freq, float(sigma), 'sin')        
            
                # ##Ploting all LASERs in single file#######
                    time_t = np.arange(t_total)
                    strength_t = pulse.strength(np.arange(t_total)*as_to_au)
                    plt.plot(time_t*as_to_au*au_to_fs,strength_t) #, 'Time (in fs)', 'Pulse Strength (in au)'
            else:
                               
                strength = laser['strength']
                l_design={}
                l_design['strength'] = strength
                time0 = 0 
                l_design['time0'] =time0                                
                l_design['type']= 'Delta'         
                
                delay_array=[x * 1e3 for x in [2,4,6,8,10]] 

                # # ##### Delta probe pulse train Generation  ###############
                
                for  delay in delay_array:

                    pulse=G_DeltaPulse(strength,float(time0)+delay)
                    strength_t = pulse.strength(np.arange(t_total)*as_to_au)
                    plt.plot(time_t*as_to_au*au_to_fs,strength_t)
                
            laser_details.append(l_design)        

        plt.xlabel('Time (in fs)')
        plt.ylabel('Pulse Strength (in au)')
        plt.show()
        
        # self.derivative_t = self.pulse.derivative(np.arange(self.range)*as_to_au)

    # def write_laser(self,filename):
    #     """ writes laser pulse to file """
    #     filename = pathlib.Path(filename) 
    #     self.pulse.write(filename, np.arange(self.range))


class LaserDesignPlotModel:
    """ laser_inputs: list of laser inputs
        laser_profile_time: in femtosecond
    """
    
    def __init__(self, laser_inputs:list, laser_profile_time) -> None:
        self.laser_inputs  = laser_inputs
        if laser_profile_time:
            self.laser_profile_time = laser_profile_time       
    
    def compute_laser_design_param(self, laser_type:str, laser_param:dict):
        """ Calculates laser parameters specific to laser type"""
        assert laser_type in ["gaussian", "delta"]

        t_in=laser_param['tin'] # in au unit
        tag = laser_param.get('tag', None)

        # delay wrt the time origin of first laser 
        # delay_time_fs = laser_param['delay_time']          
        strength_au = laser_param['strength']

        if laser_type == "gaussian":
            freq_eV=laser_param['frequency']
            strength_au = laser_param['strength']
            inval=laser_param['inval']

            # fwhm in frequency space 
            fwhm_eV=laser_param['fwhm']

            # Calculates fwhm/sigma(in time) and pulse centre(in time)
            # creates gaussian pulse with given inval,fwhm value """
            t_in_plus_delay = t_in
            # t_in_plus_delay = t_in + delay_time_fs*1e3*as_to_au
            l_design = laser_design(inval,t_in_plus_delay,fwhm_eV)
            l_design.update(
                {'type': 'gaussian', 
                'tag': tag,
                # 'tin': t_in,
                'frequency': freq_eV,
                'strength': strength_au
                })
                
            sigma_eV = round(autime_to_eV/l_design['sigma'], 2)
            time0_fs = round(l_design['time0']*au_to_fs,2) 
            pulse = GaussianPulse(strength= strength_au,
                                time0= time0_fs*1e3,frequency= freq_eV,
                                 sigma= sigma_eV, sincos='sin')
            return (pulse, l_design) 

        elif laser_type == "delta":  
            # time0=t_in*au_to_as + delay_time_fs *1e3
            time0=t_in*au_to_as
            pulse = DeltaPulse(strength= strength_au,
            time0= time0, total_time=self.laser_profile_time)

            l_design={
            'type': 'delta',
            'tag': tag, 
            "strength": strength_au,
            "time0": round(time0*as_to_au,2)
            } 
            return (pulse, l_design)
       
    def get_laser_pulse_list(self):

        self.list_of_pulse = []
        self.list_of_laser_param = []

        for n, laser in enumerate (self.laser_inputs):
            laser_type = laser.get('type')
            pulse_info = self.compute_laser_design_param(laser_type, laser)
            self.list_of_pulse.append(pulse_info[0])
            self.list_of_laser_param.append(pulse_info[1])
            
        return self.list_of_pulse

    def get_time_strength(self, list_of_pulse:list):
        """Plots single/multiple lasers"""

        if list_of_pulse:
            self.laser_sets = list_of_pulse
        else:
            self.laser_sets = self.get_laser_pulse_list()
        
        laser_profile_time_fs = self.laser_profile_time
        laser_profile_time_as = laser_profile_time_fs*1e3
        time_array = np.arange(laser_profile_time_as)

        laser_strengths = []   

        for i,laser in enumerate(self.laser_sets):                     
            if laser.get('type') == "delta": 
                time0 = laser.get('time0')*au_to_as
                pulse = DeltaPulse(strength= laser.get('strength'),
                                    time0 = time0, 
                                #    time0= laser.get('time0')*au_to_as, 
                                   total_time=self.laser_profile_time)
                strength_value = pulse.strength()

            if laser.get('type') == "gaussian": 
                time0 = laser.get('time0')*au_to_as                 
                sigma_eV = round(autime_to_eV/laser['sigma'], 2)
                # time0_fs = round(laser['time0']*au_to_fs,2) 
                freq_eV = laser.get('frequency')
                pulse = GaussianPulse(strength= laser.get('strength'),
                                    # time0= time0_fs*1e3,
                                    time0= time0,
                                    frequency= freq_eV,
                                    sigma= sigma_eV, 
                                    sincos='sin')              
                strength_value = pulse.strength(time_array*as_to_au)
            laser_strengths.append(strength_value)  

        # for pulse in self.pulse_sets:
        #     if pulse.name == "delta":
        #         strength_value = pulse.strength()
        #     if pulse.name == "gaussian":                
        #         strength_value = pulse.strength(time_array*as_to_au)
        #     laser_strengths.append(strength_value)
        self.time = time_array
        self.strengths = laser_strengths

        return (time_array,laser_strengths)     
                
    def write(self, fname, time_t, laser_strengths:list):
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
        fmt = '%20.10e'
        # fmt = '%12.6f'
        header = '{:^10}'

        # fmt_str = '%12.6f %20.10e %20.10e'
        fmt_str = '%12.6f'
        header_str = ''

        for i in range(len(laser_strengths)):
            fmt_str = fmt_str + ' '+ fmt
            header_str = header_str+header
        
        # Format header_string            
        np.savetxt(fname, np.stack((time_t, *laser_strengths)).T,
                   fmt=fmt_str, 
                #    header=header
                   )

    def plot_laser(self, fname= None):
        from litesoph.visualization.plot_spectrum import plot_multiple_column
        if fname:
            data = np.loadtxt(str(fname))
        else:
            data = np.stack((self.time, *self.strengths)).T
        num_of_lasers = len(self.strengths)
        data[:,0] = data[:,0]*as_to_au*au_to_fs

        plot_multiple_column(data_array=data,
        column_list=(1,num_of_lasers), xlabel= 'Time (in fs)', ylabel= 'Pulse Strength (in au)', xcolumn=0,        
        column_dict = format_laser_label(num_of_lasers)
        )

def format_laser_label(number_of_lasers:int):
    laser_label_dict = {}
    
    for i in range(number_of_lasers):
        laser_label_dict.update({(i+1): "laser"+ str(i+1)})

    return laser_label_dict