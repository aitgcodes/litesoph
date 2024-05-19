from dataclasses import dataclass
import pathlib
import os
import json
from matplotlib import pyplot as plt
import numpy as np
from typing import Any, Dict
from litesoph.common.data_sturcture.data_types import DataTypes as  DT
from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au, au_to_fs, fs_to_au
from litesoph.pre_processing.laser_design import laser_design, GaussianPulse, DeltaPulse, GaussianDeltaPulse
from litesoph.common.utils import get_pol_list

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
            # TODO: Polarization temporarily blocked
            # 'spinpol' :{'type':DT.string, 'values':['unpolarized', 'polarized'], 'default_value':'unpolarized'},
            'spinpol' :{'type':DT.string, 'values':['unpolarized'], 'default_value':'unpolarized'},
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
    """Laser Design Model with Gaussian Pulse"""
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
        
        sigma = autime_to_eV/self.l_design['sigma']
        time0 = self.l_design['time0']*au_to_as

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

class LaserDesignPlotModel:
    """ Laser Design Model to handle multiple lasers\n
        Currently added laser types: Gaussian, Delta
        laser_inputs: list of laser input dictionaries
        laser_profile_time: in femtosecond
    """
    
    def __init__(self, laser_inputs:list, laser_profile_time) -> None:
        self.laser_inputs  = laser_inputs
        if laser_profile_time:
            self.laser_profile_time = laser_profile_time  

    def compute_laser_design_param(self, laser_type:str, laser_param:dict):
        """ Calculates laser parameters specific to laser pulse shape
        \n and returns pulse objects
        Parameters:
            laser_type : gaussian/delta
            laser_param : 'tag','polarization','strength','tin' (common)
                            'inval','frequency','fwhm' (gaussian type)
        """

        # Collecting  common laser parameters
        tag = laser_param.get('tag', None)
        pol_var = laser_param.get('polarization', 'X')
        pol_list = get_pol_list(pol_var)   
        strength_au = laser_param.get('strength')    # in au
        t_in = laser_param.get('tin')                # in as

        if laser_type == "gaussian":
            # Collecting parameter specific to Gaussian
            inval=laser_param.get('inval')
            freq_eV=laser_param.get('frequency')     # in eV
            fwhm_eV=laser_param.get('fwhm')          # in eV  

            # Calculates fwhm/sigma(in time) and pulse centre/time0(in time)
            # creates gaussian pulse with given inval,fwhm value 
            l_design = laser_design(inval, t_in , fwhm_eV)

            l_design.update(
                {'type': 'gaussian', 
                'tag': tag,
                'frequency': freq_eV,
                'strength': strength_au,
                'polarization': pol_list
                })   
            # Unit conversion required for Pulse creation
            sigma_eV = autime_to_eV/l_design['sigma']
            time0_fs = l_design['time0']*au_to_fs

            # GaussianPulse 
            pulse = GaussianPulse(strength= strength_au,
                                time0= time0_fs*1e3,frequency= freq_eV,
                                 sigma= sigma_eV, sincos='sin')

        elif laser_type == "delta": 
            # Collecting parameter specific to Delta
            time0=t_in*au_to_as


            # DeltaPulse
            
            pulse = DeltaPulse(strength= strength_au,
            time0= time0, total_time=self.laser_profile_time)
            
            l_design = {}
            l_design.update({
            'type': 'delta',
            'tag': tag, 
            "strength": strength_au,
            "time0": time0*as_to_au,
            'polarization': pol_list
            }) 

        pulse.laser_input = laser_param                   
        pulse.laser_design = l_design
        return pulse

    def get_laser_pulse_list(self):
        """Returns list of pulse objects for list of laser inputs"""

        self.list_of_pulse = []
        for n, laser in enumerate (self.laser_inputs):
            laser_type = laser.get('type')
            pulse_info = self.compute_laser_design_param(laser_type, laser)
            self.list_of_pulse.append(pulse_info)
            
        return self.list_of_pulse

    def get_laser_param_pulse(self, laser_input:dict):
        """Returns pulse object for laser
        \n laser_input variables: 'type', 'time0'"""
        # TODO: Modify this method to decide type if not present

        laser_type = laser_input.get('type')
        if laser_type in ["gaussian", "delta"]:
            self.pulse_info = self.compute_laser_design_param(laser_type, laser_input)            
            return self.pulse_info


# ---------------------------Helper Methods for multiple laser pulses---------------------------

def get_time_strength(list_of_laser_params:list, laser_profile_time:float):
    """laser_profile_time(in fs): total time"""

    laser_sets = list_of_laser_params
    laser_profile_time_as = laser_profile_time*1e3
    time_array = np.arange(laser_profile_time_as)
    laser_strengths = []

    # TODO: Please implement it such that it always covers delta pulse spike :>
    # for i,laser in enumerate(laser_sets):
    #     if laser.get('type') == "delta":
    #         time0 = laser.get('time0')*au_to_as
    #         if time0 not in time_array:
    #             time_array = np.insert(time_array, np.searchsorted(time_array, time0), time0)

    for i,laser in enumerate(laser_sets):
        if laser.get('type') == "delta":
            time0 = laser.get('time0')*au_to_as
            pulse = DeltaPulse(strength= laser.get('strength'),
                                    time0 = time0,
                                    total_time=laser_profile_time)
            strength_value = pulse.strength(time_array*as_to_au)

        if laser.get('type') == "gaussian": 
            time0 = laser.get('time0')*au_to_as                 
            sigma_eV = autime_to_eV/laser['sigma']
            freq_eV = laser.get('frequency')
            pulse = GaussianPulse(strength= laser.get('strength'),
                                time0= time0,
                                frequency= freq_eV,
                                sigma= sigma_eV, 
                                sincos='sin')
            strength_value = pulse.strength(time_array*as_to_au)

        laser_strengths.append(strength_value) 
    return (time_array,laser_strengths)

def write_lasers(fname, time_t, laser_strengths:list):
    """
    Write the time (in au)-laser strengths to a file.
    Parameters
    ----------
    fname
        filename
    time_t
        times in attoseconds
    laser_strengths
        list of laser_strength arrays
    """
    time_t = time_t * as_to_au

    fmt = '%20.10e'
    header = '{:^20}'
    fmt_str = '%12.6f'
    column_str = '{:^20}'
    header_list = ['Time(in au)']

    # Get the format strings
    for i in range(len(laser_strengths)):
        fmt_str = fmt_str + ' '+ fmt
        column_str = column_str+header
        header_list.append('pulse'+ str(i+1))
    
    # Format header_string       
    header_str = column_str.format(*header_list)         
    np.savetxt(fname, np.stack((time_t, *laser_strengths)).T,
                fmt=fmt_str, 
               header=header_str
                )

def plot_laser(time_arr, strength_arr,fname= None):
    """Plots Strengths as function of time"""

    from litesoph.visualization.plot_spectrum import plot_multiple_column
    if fname:
        data = np.loadtxt(str(fname))
    else:
        data = np.stack((time_arr, *strength_arr)).T

    num_of_lasers = len(strength_arr)
    data[:,0] = data[:,0]*as_to_au*au_to_fs
    plot_multiple_column(data_array=data,
                        column_list=(1,num_of_lasers), 
                        xlabel= 'Time (in fs)', 
                        ylabel= 'Pulse Strength (in au)', xcolumn=0,        
                        column_dict = format_laser_label(num_of_lasers)
                        )

def format_laser_label(number_of_lasers:int):
    """Formats laser labels with index"""
    laser_label_dict = {}    
    for i in range(number_of_lasers):
        laser_label_dict.update({(i+1): "laser"+ str(i+1)})
    return laser_label_dict

#--------------------------------------------------------------------------------------------

class LaserInfo:
    def __init__(self, laser_dict:dict) -> None:
        self.data = laser_dict

    def add_systems_to_laser_data(self, system_tag:str, laser_list:list=[]):
        system_key = system_tag
        system_dict = {'tag': system_tag,
                        'lasers': laser_list}

        self.data.update({system_key:system_dict})

    def add_laser(self, system_key:str, laser_param:dict, index:int = None):
        """ Appends lasers to laser database 
        or adds to list index, if index is given"""

        if system_key in self.data.keys():
            try:
                existing_lasers = self.data[system_key]['lasers']
                assert isinstance(existing_lasers, list)  
                if index is None:
                    existing_lasers.append(laser_param)
                else:
                    try:
                        existing_lasers[index] = laser_param
                    except IndexError:
                        raise IndexError('List index:{} is not found'.format(index))     

                self.data[system_key]['lasers'] = existing_lasers
            except KeyError:
                self.data[system_key]['lasers'] = [laser_param]
        else:
            self.add_systems_to_laser_data(system_tag=system_key,laser_list=[laser_param])

    def add_pulse(self, system_key:str, laser_pulse, index:int=None):
        """ Appends laser pulse object to laser database 
        or adds to list index, if index is given"""

        pulse_info = laser_pulse
        try:
            laser_pulses =self.data[system_key]['pulses']
            assert isinstance(laser_pulses, list)
            if index is None:
                laser_pulses.append(pulse_info)
            else:
                try:
                    laser_pulses[index] = pulse_info
                except IndexError:
                    raise IndexError('List index:{} is not found'.format(index))
            self.data[system_key]['pulses'] = laser_pulses

        except KeyError:
            self.data[system_key]['pulses'] = [pulse_info]

    def remove_info(self, system_key:str, laser_index:int):
        """Removes laser details on the given index from laser_database"""
        
        if system_key in self.data.keys():
            laser_system = self.data[system_key]
            lasers = laser_system.get('lasers')
            pulses = laser_system.get('pulses')

            assert isinstance(lasers, list)
            assert isinstance(pulses, list)
            try:
                lasers.pop(laser_index)
                pulses.pop(laser_index)
                self.data[system_key]['lasers'] = lasers
                self.data[system_key]['pulses'] = pulses
            except IndexError:
                raise IndexError('List index:{} is not found'.format(laser_index))

    def check_laser_exists(self, system_tag:str):
        """ Validates availability of laser/pulse and returns bool"""

        lasers_exist = False
        pulses_exist = False
        if system_tag in self.data.keys():
            laser_system = self.data[system_tag]
            lasers = laser_system.get('lasers')
            pulses = laser_system.get('pulses')
            assert isinstance(lasers, list)
            assert isinstance(pulses, list)

            if len(lasers)> 0:
                lasers_exist = True
            if len(pulses)> 0:
                pulses_exist = True
        else:
            # TODO: handle this keyerror
            return False
            # raise KeyError("{} key is missing".format(system_tag))            

        if all([lasers_exist, pulses_exist]):
            return True
        else:
            # TODO: add condition to get the false condition
            return False

    def get_number_lasers(self, system_tag):
        try:
            lasers = self.data[system_tag]['lasers']
            num_lasers = len(lasers)
        except KeyError:
            num_lasers=0
        return num_lasers
