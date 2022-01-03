import os
import pathlib
import subprocess
from configparser import ConfigParser

sections = {
    'visualization_tools' : ['vmd', 'vesta'],
    'engine' : ['gpaw','nwchem','octopus'],
    'programs' : ['python'],
    'mpi' : ['mpirun'],
}

lsroot = pathlib.Path.cwd()
home = pathlib.Path.home()
bash_file = pathlib.Path(home) / ".bashrc"
config_file = pathlib.Path(home) / "lsconfig.ini"


def get_path(name):
    p = subprocess.run(['which', name], capture_output=True, text=True)
    if p.stdout and p.returncode == 0:
        return p.stdout.split()[0]
    else:
        return None


def create_default_config(config: ConfigParser, sections: dict):
    for key, valve in sections.items():
        config.add_section(key)
        for option in valve:
            set = get_path(option)
            if set is not None:
                config.set(key, option, set)

config = ConfigParser()
config.add_section('path')
config.set('path','home', str(home))
config.set('path','lsroot',str(lsroot))
create_default_config(config, sections)

with open(config_file, 'w+') as configfile:
    config.write(configfile)

print("##----<added by litesoph>-----##")
print(f"export PYTHONPATH=$PYTHONPATH:{lsroot}/")
print(f"export PATH=$PATH:{lsroot}/bin/")
print("##----------------##")

msg = "Above code will be appended to ~/.bashrc [y/n]:"
write_bashrc = input(msg)

if write_bashrc == 'n':
    exit()

while write_bashrc != 'y':
    print("----Incorrect input-----")
    print("enter y or n")
    write_bashrc = input(msg)
    if write_bashrc == 'n':
        break  

if write_bashrc == 'y':
    with open(bash_file, 'a') as f:
        f.write("##----<added by litesoph>-----##\n")
        f.write(f"export PYTHONPATH=$PYTHONPATH:{lsroot}/\n")
        f.write(f"export PATH=$PATH:{lsroot}/bin/\n")
        f.write("##----------------##")
