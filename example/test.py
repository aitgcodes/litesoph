# export the path of the directroy containing litesoph
# export PYTHONPATH=$PYTHONPATH:path/to/directory

from litesoph.io.IO import user_input as ui
from litesoph.simulations.esmd import ground_state 
from litesoph.simulations import esmd

#  define input parameters
input_par = {'xc':'PBE',
             'geometry':'/home/sachin/Downloads/coordinate.xyz', # Path to geometry file
             'mode':'lcao',
             'engine': 'gpaw',
             'properties':'get_potential_energy()',
             'work_dir':'/home/sachin/Downloads', # give path to your working directory
             'vacuum': 6,
             'basis':'pw' }

ui.user_param.update(input_par) # update the user parameters
user_input = ui.user_param
print(user_input)

engine = esmd.choose_engine(user_input) # decide engine from user input

# pass engine and user_input to ground_state class
# To create gpaw script for ground state calculation.
ground_state(user_input, engine)
