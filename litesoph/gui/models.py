import pathlib
import os
import json

from typing import Any, Dict
from litesoph.simulations.engine import EngineStrategy, EngineGpaw,EngineNwchem,EngineOctopus

class WorkManagerModel:
    
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
        'validate job' : {'type': 'bool', 'value': True}
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

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
        list_engine = [EngineGpaw(),
                        EngineOctopus(),
                        EngineNwchem()]
        
        
        if user_input['engine'] == 'gpaw':
            return list_engine[0]
        if user_input['engine'] == 'octopus':
            return list_engine[1]
        elif user_input['engine'] == 'nwchem':
            return list_engine[2]
        else:
            raise ValueError('engine not implemented')

class LaserDesginModel:

    def __init__(self) -> None:
        pass

    def laser_calc(self, strength,
                        inval,
                        tin,
                        fwhm):
        from litesoph.pre_processing.laser_design import laser_design
        l_dict = laser_design(strength, inval, tin , fwhm )
        return(l_dict)
    
    def write_laser(laser_input:dict, filename, directory):

        from litesoph.pre_processing.laser_design import GaussianPulse
        import numpy as np

        filename = filename + ".dat"
        filename = pathlib.Path(directory) / filename
        pulse = GaussianPulse(float(laser_input['strength']), float(laser_input['time0']),float(laser_input['frequency']), float(laser_input['sigma']), laser_input['sincos'])
        pulse.write(filename, np.arange(laser_input['range']))

class TextVewerModel:

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