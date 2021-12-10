from typing import Any, Dict
from ase.calculators.calculator import InputError
from litesoph.simulations.engine import EngineStrategy

class GroundState:
    """It takes in the user input dictionary as input. It then decides the engine and converts 
    the user input parameters to engine specific parameters then creates the script file for that
    specific engine."""

    def __init__(self, user_input: Dict[str, Any],filename, engine: EngineStrategy) -> None:
        self.user_input = user_input
        self.engine = engine
        self.task = self.engine.get_task_class('ground state',self.user_input)

        if self.engine.check_compatability(self.user_input, self.task):
            parameters = self.engine.engine_input_para(user_param=self.user_input, default_param= self.task.default_param, task=self.task)
            self.template = self.task.format_template(parameters)
            engine.create_script(self.user_input['directory'],filename, self.template)
        else:
            raise InputError("Input parameters not compatable with the engine")


class RT_LCAO_TDDFT:
    
    def __init__(self, user_input: Dict[str, Any],filename, engine: EngineStrategy, directory) -> None:
        self.user_input = user_input
        self.engine = engine
        self.task = self.engine.get_task_class('LCAO TDDFT', self.user_input)
        self.directory = directory
        self.user_input['directory']=self.directory
        self.template = self.task.format_template()

        engine.create_script(self.directory, filename, self.template)
        
class LR_TDDFT:
    pass

def user_para2engine_para(self, user_input:dict, engine:str):
    """It converts user input parameter to engine specific parameters."""


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


if __name__ == "__main__":
    pass
