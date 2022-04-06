import pathlib
import os
import json
import numpy as np
from typing import Any, Dict
from litesoph.simulations.engine import EngineStrategy, EngineGpaw,EngineNwchem,EngineOctopus
from litesoph.lsio.data_types import DataTypes as  DT
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


class GroundStateModel:
    
    filename = "gs"

    _default_var = {
            'mode' : ['str', '--choose mode--'],
            'xc' : ['str', ''],
            'basis' : ['str', ''],
            'charge': ['float', 0],
            'maxiter' : ['int', 300],
            'shape' : ['str', ''],
            'spinpol' : ['str', 'None'],
            'multip' : ['int', 1],
            'h' : ['float', 0.23],
            'nbands' : ['int'],
            'vacuum' : ['float', 6],
            'energy' : ['float', 5.0e-7],
            'density' : ['float'],
            'bands' : ['str'],
            'theory' : ['str'],
            'tolerances' : ['str'],
            'lx' : ['float'],
            'ly' : ['float'],
            'lz' : ['float'],
            'r' : ['float'],
            'l' : ['float'],
            'dxc' : ['int', 3],
            'mix' : ['float', 0.3],
            'eigen' : ['str'],
            'smear' : ['float', 0.1],
            'smearfn' : ['str'],
            'unitconv' : ['str'],
            'unit_box' : ['str', 'au']
        
        }

    def __init__(self) -> None:
        pass
    

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
    figure = Figure(figsize=(5, 3), dpi=100)  
      
    ax = figure.add_subplot(1, 1, 1)
    ax.plot(x_data, y_data, 'k')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
 
    return figure    


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