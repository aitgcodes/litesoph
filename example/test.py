# export the path of the directroy containing litesoph
# export PYTHONPATH=$PYTHONPATH:path/to/directory

from litesoph.lsio.IO import UserInput as ui
from litesoph.simulations.esmd import GroundState
from litesoph.simulations import engine

#  define input parameters
input_par = {'xc':'PBE',
             'geometry':'/home/sachin/Downloads/coordinate.xyz', # Path to geometry file
             'mode':'lcao',
             'engine': 'gpaw',
             'properties':'get_potential_energy()',
             'work_dir':'/home/sachin/Downloads', # give path to your working directory
             'vacuum': 6,
             'basis':'dzp'}

ui.user_param.update(input_par) # update the user parameters
user_input = ui.user_param
print(user_input)

engine = engine.choose_engine(user_input) # decide engine from user input

# pass engine and user_input to ground_state class
# To create gpaw script for ground state calculation.
GroundState(user_input, engine)
