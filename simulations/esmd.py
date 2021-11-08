from typing import Any, Dict

from ase.calculators.calculator import InputError, Parameters
from litesoph.io.IO import write2file 
from gpaw import GPAW
from litesoph.simulations.GPAW import gpaw_template as gpaw
from abc import ABC, abstractclassmethod

class EngineStrategy(ABC):
    @abstractclassmethod
    def engine_name():
        """retruns engine name"""
        pass

    @abstractclassmethod
    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with the engine"""
        pass

    @abstractclassmethod
    def get_task_class( task: str):
        pass

    @abstractclassmethod
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    @abstractclassmethod
    def create_script(self,template: str, dict:Dict[str, Any]) -> None:
        pass

    @abstractclassmethod
    def excute():
        pass

class Enginegpaw(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'gpaw'

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""
        
        if user_param['mode'] not in ['fd', 'lcao', 'paw'] and  user_param['engine'] == 'gpaw':
            raise ValueError('This mode is not compatable with gpaw use fd, lcao or paw')
        
        if user_param['engine'] == 'gpaw':
            return  True
        else:
            return False

    def get_task_class(self, task: str):

        tasks = [gpaw.gpaw_ground_state(),
                gpaw.lr_tddft(),
                gpaw.rt_lcao_tddft(),
                gpaw.induced_density(),]

        if task == "ground state":
            return gpaw.gpaw_ground_state()
            
    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        parameters = user2gpaw(user_param, default_param)
        return parameters
    
    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for gpaw"""
        filename = filename + '.py'
        write2file(directory,filename,template, dict)

    def excute():
        pass

class Engineoctopus(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'octopus '

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""

        return False

    def get_task_class(self, task: str):
        pass

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for octopus"""
        write2file(directory,filename,template, dict)

    def excute():
        pass

class Enginenwchem(EngineStrategy):

    def engine_name():
        """retruns engine name"""
        return 'nwchem'

    def check_compatability(self, user_param:Dict[str, Any]) -> bool:
        """checks the compatability of the input parameters with gpaw engine"""

        return False

    def get_task_class(self, task: str):
        pass

    def engine_input_para(self, user_param:Dict[str, Any], default_param:Dict[str, Any]) -> Dict[str, Any]:
        """updates the default input parameters with the user input"""
        pass

    def create_script(self,directory,filename,template: str, dict:Dict[str, Any]) -> None:
        """creates the input scripts for nwchem"""
        write2file(directory,filename,template, dict)
    
    def excute():
        pass

def choose_engine(user_input: Dict[str, Any]) -> EngineStrategy:
    
    list_engine = [Enginegpaw(),
                    Engineoctopus(),
                    Enginenwchem()]

    for engine in list_engine:
        if engine.check_compatability(user_input):
            return engine
        else:
            raise ValueError('engine not implemented')


class ground_state:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any], engine: EngineStrategy) -> None:
        self.user_input = user_input
        self.engine = engine
        
        if self.engine.check_compatability(self.user_input):
            task = self.engine.get_task_class(task='ground state')
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= task.default_param)
            engine.create_script(self.user_input['work_dir'], 'gs', task.gs_template, parameters)
        else:
            raise InputError("Input parameters not compatable with the engine")

        
            
def user_para2engine_para(self, user_input:dict, engine:str):
    """It converts user input parameter to engine specific parameters."""


def user2gpaw(user_input:Dict[str, Any], default_parameters: Dict[str, Any]) -> Dict[str, Any]:
    import os
    parameters = default_parameters
    
    for key in user_input:
        if key not in ['tolerance','convergance','box'] and user_input[key] is not None:
            parameters[key] = user_input[key]
                        
        if key == 'work_dir' and user_input[key] is None:
            print('The project directory is not specified so the current directory will be taken as working directory')
            parameters.update(key = user_input['work_dir'][os.getcwd()])

        if key == 'geometry' and user_input[key] is None:
            raise ValueError('The structure file is not found')
    return parameters


def dft_input_file(drop_mode,drop_ftype,drop_basis,spacing,bands,vacuum):
    line_1 = "from ase.io import read, write"
    line_2 = "from ase import Atoms" 
    line_3 = "from ase.parallel import paropen"
    line_4 = "from gpaw.poisson import PoissonSolver"
    line_5 = "from gpaw.eigensolvers import CG"
    line_6 = "from gpaw import GPAW, FermiDirac"
    line_7 = "from gpaw import Mixer, MixerSum, MixerDif"
    line_8 = "from gpaw.lcao.eigensolver import DirectLCAO"

    line_9 = "# Molecule or nanostructure"
    line_10 = "layer = read('coordinate.xyz')"
    vac = str(vacuum)
    line_11 = [ "layer.center(vacuum=", vac,")"]

    line_12 = "#Ground-state calculation"
    mode = str(drop_mode)
    line_13 = ["calc = GPAW(mode='",mode, "',"]
    spa = str(spacing)
    line_14 = ["            h=", spa, ","]
    line_15 = ["            basis='",str(drop_basis),"',"]
    line_16 = ["            xc='",str(drop_ftype),"',"]
    line_17 = ["            nbands=",str(bands),","]
    line_18 =  "            setups={'default': 'paw'}, "
    line_19 =  "            occupations=FermiDirac(width=0.07),"
    line_20 =  "            mixer=Mixer(0.02, 5, 1.0),"
    line_21 =  "            maxiter=2500,"
    line_22 =  "            convergence={'density': 1e-12, 'bands': -20},"
    line_23 =  "            txt='gs.out')"
    line_24 =  "layer.calc = calc"
    line_25 =  "energy = layer.get_potential_energy()"
    line_26 =  "calc.write('gs.gpw', mode='all')"


    with open("gs.py", "w") as gs_file:

        gs_file.truncate()

        gs_file.write(line_1)
        gs_file.write("\n")

        gs_file.write(line_2)
        gs_file.write("\n")
            
        gs_file.write(line_3)
        gs_file.write("\n")

        gs_file.write(line_4)
        gs_file.write("\n")

        gs_file.write(line_5)
        gs_file.write("\n")

        gs_file.write(line_6)
        gs_file.write("\n")

        gs_file.write(line_7)
        gs_file.write("\n")

        gs_file.write(line_8)
        gs_file.write("\n")
        gs_file.write("\n")

        gs_file.write(line_9)
        gs_file.write("\n")

        gs_file.write(line_10)
        gs_file.write("\n")

        gs_file.writelines(line_11)
        gs_file.write("\n")
        gs_file.write("\n")

        gs_file.writelines(line_12)
        gs_file.write("\n")

        gs_file.writelines(line_13)
        gs_file.write("\n")

        gs_file.writelines(line_14)
        gs_file.write("\n")

        gs_file.writelines(line_15)
        gs_file.write("\n")

        gs_file.writelines(line_16)
        gs_file.write("\n")
        
        gs_file.writelines(line_17)
        gs_file.write("\n")

        gs_file.write(line_18)
        gs_file.write("\n")

        gs_file.write(line_19)
        gs_file.write("\n")

        gs_file.write(line_20)
        gs_file.write("\n")

        gs_file.write(line_21)
        gs_file.write("\n")

        gs_file.write(line_22)
        gs_file.write("\n")

        gs_file.write(line_23)
        gs_file.write("\n")
        
        gs_file.write(line_24)
        gs_file.write("\n")

        gs_file.write(line_25)
        gs_file.write("\n")

        gs_file.write(line_26)


def tddft_input_file(drop_strength,drop_pol_x,drop_pol_y,drop_pol_z,dt,Nt):
    line_1 = "# Time-propagation calculation"
    line_2 = "from gpaw.lcaotddft import LCAOTDDFT"
    line_3 = "from gpaw.lcaotddft.dipolemomentwriter import DipoleMomentWriter"
    line_4 = "# Read converged ground-state file"
    line_5 = "td_calc = LCAOTDDFT('gs.gpw', txt='tdx.out')"
    line_6 = "# Attach any data recording or analysis tools"
    line_7 = "DipoleMomentWriter(td_calc, 'dm.dat')"
    line_8 = "# Kick"

    Ex = float(drop_strength)*int(drop_pol_x)
    Ey = float(drop_strength)*int(drop_pol_y)
    Ez = float(drop_strength)*int(drop_pol_z)
    #Ey = drop_strength*drop_pol_y
    #Ez = drop_strength*drop_pol_z

    line_9 = ["td_calc.absorption_kick([", str(Ex), ", ", str(Ey), ", ",  str(Ez),"])"]
    line_10 = "# Propagate"
    line_11 = ["td_calc.propagate(", str(dt), ", ", str(Nt),")"]
    line_12 = "# Save the state for restarting later"
    line_13 = "td_calc.write('td.gpw', mode='all')"


    with open("td.py", "w") as td_file:

        td_file.truncate()

        td_file.write(line_1)
        td_file.write("\n")

        td_file.write(line_2)
        td_file.write("\n")

        td_file.write(line_3)
        td_file.write("\n")
        td_file.write("\n")

        td_file.write(line_4)
        td_file.write("\n")

        td_file.write(line_5)
        td_file.write("\n")
        td_file.write("\n")

        td_file.write(line_6)
        td_file.write("\n")

        td_file.write(line_7)
        td_file.write("\n")
        td_file.write("\n")

        td_file.write(line_8)
        td_file.write("\n")

        td_file.writelines(line_9)
        td_file.write("\n")
        td_file.write("\n")

        td_file.writelines(line_10)
        td_file.write("\n")

        td_file.writelines(line_11)
        td_file.write("\n")
        td_file.write("\n")

        td_file.writelines(line_12)
        td_file.write("\n")

        td_file.writelines(line_13)
        #td_file.write("\n")

#-------------------------------------------------------------
#       Preparing the input file for the spectrum calculation
#-------------------------------------------------------------

    spec_line_1 = "# Analyze the results"
    spec_line_2 = "from gpaw.tddft.spectrum import photoabsorption_spectrum"
    spec_line_3 = "photoabsorption_spectrum('dm.dat', 'spec.dat', width=0.09, e_min=0.0, e_max=15.0, delta_e=0.05)"

    with open("spec.py", "w") as spec_file:

        spec_file.truncate()

        spec_file.write(spec_line_1)
        spec_file.write("\n")

        spec_file.write(spec_line_2)
        spec_file.write("\n")

        spec_file.write(spec_line_3)
        spec_file.write("\n")