import configparser
import os
import pathlib
import subprocess
from configparser import ConfigParser

visualization_tools = ['vmd', 'vesta']

engine = ['gpaw','nwchem','octopus']

programs = ['python', 'mpi']

lsroot = pathlib.Path.cwd()
home = pathlib.Path.home()
bash_file = pathlib.Path(home) / ".bashrc"

cofigs = ConfigParser()

def get_path(name):
    try:
        p = subprocess.run(['which', name], capture_output=True, text=True)
    except:
        pass

with open(bash_file, 'a') as f:
    f.write("##----<added by litesoph>-----##\n")
    f.write(f"export PYTHONPATH=$PYTHONPATH:{lsroot}/\n")
    f.write(f"export PATH=$PATH:{lsroot}/bin/\n")
    f.write("##----------------##")