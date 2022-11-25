from dataclasses import dataclass
import pathlib
import os
import json
import numpy as np
from typing import Any, Dict
from litesoph.common.data_sturcture.data_types import DataTypes as  DT
from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au, au_to_fs


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

