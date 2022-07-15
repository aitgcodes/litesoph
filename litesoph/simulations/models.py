from dataclasses import dataclass
import pathlib
import os
import json
import numpy as np
from typing import Any, Dict
from litesoph.lsio.data_types import DataTypes as  DT
from litesoph.simulations import gpaw
from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au, au_to_fs

class WorkManagerModel:

    _default_var = {
            'proj_path' : ['str'],
            'proj_name' : ['str'],
            'task' : ['str', '--choose job task--'],
            'sub_task' : ['str']
        }
    
    def __init__(self) -> None:
        pass
        
    @staticmethod
    def check_dir_exists(project_path):
        """ check if directory exists. """
        project_path = pathlib.Path(project_path)
        dir_exists = os.access(project_path, os.F_OK)
        return dir_exists
            

    @staticmethod
    def create_dir(project_path):
        """ Creates project directory. """
        project_path = pathlib.Path(project_path)
        parent_writeable = os.access(project_path.parent, os.W_OK)

        if not parent_writeable:
            msg = f'Permission denied creating directory: {project_path}'
            raise PermissionError(msg)

        project_path = pathlib.Path(project_path)
        os.makedirs(project_path)

class SettingsModel:

    options ={
        'validate job' : {'type': 'bool', 'value': True},
        'autofill date': {'type': 'bool', 'value': True},
        'autofill sheet data': {'type': 'bool', 'value': True},
        'font size': {'type': 'int', 'value': 9},
        'font family': {'type': 'str', 'value': ''},
        'theme': {'type': 'str', 'value': 'default'},
        'db_host': {'type': 'str', 'value': 'localhost'},
        'db_name': {'type': 'str', 'value': ''},
        'weather_station': {'type': 'str', 'value': 'KBMG'},
        'host': {'type': 'str', 'value': 'localhost'},
        'port': {'type': 'int', 'value': 22},
        'path': {'type': 'str', 'value': ''}
    }
    
    config_dirs = {
    "Linux": pathlib.Path(os.environ.get('$LS_CONFIG_HOME', pathlib.Path.home() / '.lsconfig')),
    'Windows': pathlib.Path.home() / 'AppData' / 'Local'
  }

    def __init__(self) -> None:
        filename = "ls_settings.json"
        self.filepath = pathlib.Path.home() / filename
        self.load()

    def load(self):
        if not self.filepath.exists():
            return

        with open(self.filepath, 'r') as f:
            raw_values = json.load(f)

        for key in self.options:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.options[key]['value'] = raw_value
    
    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.options, f)

    def set(self, key, value):
        if (
            key in self.options and
            type(value).__name__ == self.options[key]['type']
        ):
            self.options[key]['value'] = value
        else:
            raise ValueError("Bad key or wrong variable type")

def get_engine_model(engine):

    if  engine == 'auto-mode':
        return AutoModeModel
    elif engine == 'gpaw':
        return GpawModel
    elif engine == 'nwchem':
        return NWchemModel
    elif engine == 'octopus':
        return OctopusModel

@dataclass
class AutoModeModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['nao', 'fd', 'pw', 'gaussian'], 'default_value': '--choose mode--','tooltipdoc': 'mode doc label' },
            'shape' : {'type':DT.string, 'values':["parallelepiped","minimum", "sphere", "cylinder"], 'default_value':"--choose box--"},
            'basis' : {'type':DT.string, 'values':[], 'default_value': '','tooltipdoc': 'doc label'},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0, 'tooltipdoc': 'doc label'},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1, 'tooltipdoc': 'doc label'},
        }


@dataclass
class GpawModel:
    
   ground_state = {
            'mode' : {'type':DT.string, 'values':['nao', 'fd', 'pw'], 'default_value': 'nao', 'tooltipdoc': 'doc label' },
            'xc' : {'type':DT.string, 'values':["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"], 'default_value': 'LDA'},
            'basis' : {'type':DT.string, 'values':["dzp","sz","dz","szp","pvalence.dz"], 'default_value': 'dzp','tooltipdoc': ' doc label'},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0, 'tooltipdoc': 'doc label'},
            'maxiter' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
            'shape' : {'type':DT.string, 'values':['parallelepiped'], 'default_value':'parallelepiped'},
            'spinpol' : {'type':DT.string, 'values':['None', 'True'], 'default_value':'None'},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1, 'tooltipdoc': 'doc label'},
            'h' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
            'nbands' :{'type':DT.string, 'min': None, 'max': None, 'default_value': ''},
            'vacuum' :{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
            'energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            'bands' : {'type':DT.string, 'values':['occupied', 'unoccupied'], 'default_value': 'occupied'},
            'lx' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'ly' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'lz' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'smear' :{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.0},    
            'smearfn' :{'type':DT.string, 'values':["improved-tetrahedron-method","tetrahedron-method","fermi-dirac","marzari-vanderbilt"], 'default_value': ''},
            'eigenstate': {'type': DT.decimal , 'min': None, 'max': None, 'default_value': 4e-8},
            'tooltip_label': {'type':DT.string, 'upload_geometry_doc': 'Please upload the geometry file i.e xyz coordinate file using "SELECT" button'}
        }

@dataclass
class NWchemModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['gaussian'], 'default_value': 'gaussian','tooltipdoc': 'mode doc label'  },
            'xc' : {'type':DT.string, 'values':["PBE96","PBE0","B3LYP","PW91", "BP86", "BP91","BHLYP","M05","M05-2X","M06-HF","M08-SO","M011","CAM-B3LYP","LC-BLYP","LC-PBE","LC-wPBE","HSE03","HSE06"], 'default_value': "PBE0"},
            'basis' : {'type':DT.string, 'values':["6-31G","STO-2G","STO-3G","STO-6G","3-21G","3-21G*","6-31G*","6-31G**","6-311G","6-311G*","6-311G**","cc-pVDZ","aug-cc-pvtz"], 'default_value': "6-31G", 'tooltipdoc': 'doc label'},
            'charge':  {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0, 'tooltipdoc': 'doc label'},
            'maxiter' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
            'multip' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 1, 'tooltipdoc': 'doc label'},
            'energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            #'tolerances' : ['str','tight'],
            'gradient' :  {'type':DT.decimal, 'min': None, 'max': None, 'default_value':1.0e-4}
        }

@dataclass
class OctopusModel:
    
    ground_state = {
            'mode' : {'type':DT.string, 'values':['fd'], 'default_value': 'fd','tooltipdoc': 'mode doc label' },
            'var_oct_xc' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 1},
            #'oct_xc' : ['str',''],
            'x' :  {'type':DT.string, 'values':{'lda_x' : ["lda_x","lda_x_rel","lda_x_erf","lda_x_rae"],
                                                    'pbe_x':["gga_x_pbe","gga_x_pbe_r","gga_x_b86","gga_x_herman","gga_x_b86_mgc","gga_x_b88","gga_x_pbe_sol"]}, 'default_value':''},
            'c' :  {'type':DT.string, 'values':{'lda_c' : ["lda_c_pz_mod","lda_c_ob_pz","lda_c_pw","lda_c_ob_pw","lda_c_2d_amgb"],
                                                    'pbe_c':["gga_c_pbe","gga_c_tca","gga_c_lyp","gga_c_p86","gga_c_pbe_sol"]}, 'default_value':''},
            'pseudo' : {'type':DT.string, 'values':{'expt_yes' :[["pseudodojo_lda","hscv_lda","pseudodojo_lda_stringent"],["pseudodojo_pbe","pseudodojo_pbe_stringent","pseudodojo_pbesol","pseudodojo_pbesol_stringent","sg15", "hscv_pbe"]],
                                                    'expt_no':["standard", "hgh_lda_sc","hgh_lda"]}, 'default_value':''},
            'expt' : {'type':DT.string, 'values':['yes','no'], 'default_value':'no'},
            'charge': {'type':DT.integer,'min': None, 'max': None, 'default_value': 0, 'tooltipdoc': 'doc label'},
            'maxiter' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 300},
            'shape' :{'type':DT.string, 'values':["parallelepiped","minimum", "sphere", "cylinder"], 'default_value':'parallelepiped'},
            'spinpol' :{'type':DT.string, 'values':['unpolarized', 'polarized'], 'default_value':'unpolarized'},
            'multip' : {'type':DT.integer, 'min': None, 'max': None, 'default_value': 1, 'tooltipdoc': 'doc label'},
            'h' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
            'energy' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7},
            'density' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6},
            'lx' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'ly' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'lz' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'r' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
            'l' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
            'dxc' : {'type':DT.integer,'min': None, 'max': None, 'default_value': 3},
            'mix' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
            'eigen' : {'type':DT.string, 'values':["rmmdiis","plan","cg","cg_new"], 'default_value':'rmmdiis'},
            'smear' : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.1},
            'smearfn' : {'type':DT.string, 'values':["semiconducting","fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"], 'default_value':'semiconducting'},
            'unitconv' : {'type':DT.string, 'values':[], 'default_value':''},
            'unit_box' : {'type':DT.string, 'values':['angstrom', 'au'], 'default_value':'angstrom'},
            'absdensity': {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
            'abseigen'  : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
            'rlteigen'   : {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0},
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
        range = int(self.user_input['number_of_steps'])* float(self.user_input['time_step'])
        self.range = range

    def create_pulse(self):
        """ creates gaussian pulse with given inval,fwhm value """
        from litesoph.pre_processing.laser_design import GaussianPulse
        from litesoph.pre_processing.laser_design import laser_design
        #from litesoph.utilities.units import autime_to_eV, au_to_as, as_to_au
        self.l_design = laser_design(self.user_input['inval'], self.user_input['tin'], self.user_input['fwhm'])      
        laser_input = {
            'frequency': self.user_input['frequency'],
            'sigma': round(autime_to_eV/self.l_design['sigma'], 2),
            'time0': round(self.l_design['time0']*au_to_as, 2) ,       
            'sincos': 'sin'
        }
        self.pulse = GaussianPulse(float(self.user_input['strength']),float(laser_input['time0']),float(laser_input['frequency']), float(laser_input['sigma']), laser_input['sincos'])        
        
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


class TextViewerModel:

    def __init__(self, filename) -> None:
        self.filename = filename

    def read_file(self):
        with open(self.filename, 'r') as f:
            self.text = f.read()
        return self.text

    def append_file(self, text):
        with open(self.filename, 'a') as f:
            f.write(text)

    def write_file(self, text):
        with open(self.filename, 'w') as f:
            f.write(text)