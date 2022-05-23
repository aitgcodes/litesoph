import configparser
import pathlib
import os
from abc import ABC, abstractmethod
from typing import Any, Dict

from litesoph.lsio.IO import write2file 
from litesoph.simulations.gpaw import gpaw_data
from litesoph.simulations.nwchem import nwchem_data
from litesoph.simulations.octopus import octopus_data 
from litesoph import config

class EngineStrategy(ABC):
    """Abstract base class for the different engine."""

    @abstractmethod
    def create_script(self, template: str) -> None:
        pass

    @abstractmethod
    def create_command(self) -> list:
        pass

    def create_directory(self, directory):
        absdir = os.path.abspath(directory)
        if absdir != pathlib.Path.cwd and not pathlib.Path.is_dir(directory):
            os.makedirs(directory)
    
    def get_dir_name(self, task):
        for t_dir in self.task_dirs:
            if task in t_dir:
                dir = t_dir[1]
                break
        return dir


class EngineGpaw(EngineStrategy):

    NAME = 'gpaw'

    ground_state = gpaw_data.ground_state
    
    rt_tddft_delta = gpaw_data.rt_tddft_delta

    rt_tddft_laser = gpaw_data.rt_tddft_laser
    spectrum =  gpaw_data.spectrum
    
    tcm = gpaw_data.tcm

    task_dirs = gpaw_data.task_dirs
    
    def __init__(self, project_dir:pathlib.Path ,lsconfig, status=None) -> None:
        self.project_dir = project_dir
        self.status = status
        self.lsconfig = lsconfig
    
    def create_script(self,directory,template: str,filename) -> None:
        """creates the input scripts for gpaw"""
        if not filename:
            raise Exception('input filename not given')
        self.directory = directory
        self.filename = filename
        write2file(self.directory,self.filename,template)

    def create_dir(self, directory, task):
        task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / self.NAME / task_dir
        self.create_directory(directory)
        return directory

    def create_command(self, job_script: list , np: int ,filename, path=None, remote=False) -> list:
        
        # filename = pathlib.Path(self.directory) / self.filename
        # command = self.lsconfig.get('programs', 'python')
        # command = command + ' ' + str(filename) 
        
        # if cmd:
        #     command = cmd + ' ' + command

        if remote:
            job_script.append(self.get_engine_network_job_cmd())
            #rpath = pathlib.Path(path) / self.project_dir.name / self.path
            job_script.append(f"cd {str(path)}")
            job_script.append(f"mpirun -np {np:d}  python3 {filename}")
        else:
            job_script.append(f"cd {str(path)}")

            path_python = self.lsconfig.get('programs', 'python')
            command = path_python + ' ' + str(filename) 
            if np > 1:
                cmd_mpi = config.get_mpi_command(self.NAME, self.lsconfig)
                command = cmd_mpi + ' ' + '-np' + ' ' + str(np) + ' ' + command
            job_script.append(command)
        
        return job_script



    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of GPAW 

##eval "$(conda shell.bash hook)"
##conda activate <environment name>"""
        return job_script

class EngineOctopus(EngineStrategy):

    NAME = 'octopus'

    ground_state = octopus_data.ground_state
    
    rt_tddft_delta = octopus_data.rt_tddft_delta

    rt_tddft_laser = octopus_data.rt_tddft_laser

    spectrum =  octopus_data.spectrum

    def __init__(self,project_dir,lsconfig, status=None) -> None:
        self.project_dir = project_dir
        self.status = status
        self.lsconfig = lsconfig

    def create_dir(self, directory, *_):
        directory = pathlib.Path(directory) / self.NAME
        self.create_directory(directory)
        return directory

    def create_script(self,directory,template: str, *_) -> None:
        """creates the input scripts for gpaw"""
        self.directory = directory
        self.filename = 'inp' 
        write2file(self.directory,self.filename,template)

    def create_command(self, cmd: str):

        ofilename = "log"
        command = self.lsconfig.get('engine', 'octopus')

        if not command:
            command = 'octopus'
        command = command + ' ' + '>' + ' ' + str(ofilename)
        if cmd:
            command = cmd + ' ' + command
        return command

        
class EngineNwchem(EngineStrategy):

    NAME = 'nwchem'

    ground_state = nwchem_data.ground_state
    
    rt_tddft_delta = nwchem_data.rt_tddft_delta

    rt_tddft_laser = nwchem_data.rt_tddft_laser

    spectrum =  nwchem_data.spectrum

    restart = nwchem_data.restart

    task_dirs = nwchem_data.task_dirs


    def __init__(self, project_dir, lsconfig, status=None) -> None:
        self.project_dir = project_dir
        self.status = status
        self.lsconfig = lsconfig
        self.restart = pathlib.Path(self.project_dir.name) / self.restart

    def create_dir(self, directory, task):

        self.restart_dir = self.project_dir.parent /  self.restart
        self.create_directory(self.restart_dir)

        task_dir = self.get_dir_name(task)
        directory = pathlib.Path(directory) / self.NAME / task_dir
        self.create_directory(directory)
        return directory

    def create_script(self,directory,template: str,filename) -> None:
        """creates the input scripts for nwchem"""
        if not filename:
            raise Exception('input filename not given')
        self.directory = directory
        self.filename = filename 
        write2file(self.directory,self.filename,template)
    
    def create_command(self, job_script: list , np: int ,filename, path=None, remote=False) -> list:

        filename = pathlib.Path(self.directory) / self.filename
        ofilename = pathlib.Path(filename).stem + '.nwo'
        command = self.lsconfig.get('engine', 'nwchem')
        # if not command:
        #     command = 'nwchem'
        # command = command + ' ' + str(filename) + ' ' + '>' + ' ' + str(ofilename)
        # if cmd:
        #     command = cmd + ' ' + command

        if remote:
            job_script.append(self.get_engine_network_job_cmd())
            job_script.append(f"cd {str(path)}")
            job_script.append(f"mpirun -np {np:d}  nwchem {filename}")
        else:
            job_script.append(f"cd {str(path)}")

            path_nwchem = self.lsconfig.get('engine', 'nwchem')
            if not path_nwchem:
                path_nwchem = 'nwchem'
            command = path_nwchem + ' ' + str(filename) + ' ' + '>' + ' ' + str(ofilename)
            if np > 1:
                cmd_mpi = config.get_mpi_command(self.NAME, self.lsconfig)
                command = cmd_mpi + ' ' + '-np' + ' ' + str(np) + ' ' + command
            job_script.append(command)
        return command

    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of NWCHEM or load the module

#eval "$(conda shell.bash hook)"
#conda activate <environment name>

#module load nwchem"""
        return job_script