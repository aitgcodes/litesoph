import subprocess
import pathlib
from configparser import ConfigParser, NoOptionError, NoSectionError

import litesoph


config_file = pathlib.Path.home() / "lsconfig.ini"

lsroot = pathlib.Path(litesoph.__file__).parent.parent


sections = {
    'visualization_tools' : ['vmd', 'vesta'],
    'engine' : ['gpaw','nwchem','octopus'],
    'programs' : ['python'],
    'mpi' : ['mpirun'],
}


def get_path(name):
    print("Checking for {}....".format(name))
    p = subprocess.run(['which', name], capture_output=True, text=True)
    if p.stdout and p.returncode == 0:
        print("Found {} in {}".format(name, p.stdout.split()[0]))
        return p.stdout.split()[0]
    else:
        print("Did not find {}".format(name))
        return None
    

def create_default_config(config: ConfigParser, sections: dict):
    for key, valve in sections.items():
        config.add_section(key)
        for option in valve:
            set = get_path(option)
            if set is not None:
                config.set(key, option, set)
            else:
                config.set(key, option , '')

def write_config():
    config = ConfigParser(allow_no_value=True)
    config.add_section('path')
    config.set('path','lsproject', str(pathlib.Path.home()))
    print(f"setting lsroot:{str(lsroot)}")
    config.set('path','lsroot',str(lsroot))
    create_default_config(config, sections)

    config.set('mpi', 'gpaw_mpi', '')
    config.set('mpi', 'octopus_mpi', '')
    config.set('mpi', 'nwchem_mpi', '')

    print('Creating ~/lsconfig.ini ...')
    try:
        with open(config_file, 'w+') as configfile:
            config.write(configfile)
    except Exception as e:
        raise e
    else:
        print('Done.')


def check_config(lsconfig: ConfigParser, name):
    if name == "lsroot":
        try:
            lsroot = pathlib.Path(lsconfig.get("path", "lsroot" ))
        except:
            print("Please set lsroot in ~/lsconfig.ini")
            exit()
        else:
            return lsroot
    if name == "vis":
        try:
           vis_tool = list(lsconfig.items("visualization_tools"))[0][1]
        except:
            print("Please set path to vmd or vesta in ~/lsconfig.ini and first one will be used")
        else:
            return vis_tool
        # try:
        #     vmd = lsconfig.get("visualization_tools", "vmd" )
        # try:
        #     vmd = lsconfig.get("visualization_tools", "vesta" )
        # except:
        #     print("Please set path to vmd in ~/lsconfig.ini")
        # else:
        #     return vmd

def read_config():

    if config_file.is_file is False:
        raise FileNotFoundError("lsconfig.ini doesn't exists")

    lsconfig = ConfigParser(allow_no_value=False)
    lsconfig.read(config_file)
    return lsconfig

def set_config(config: ConfigParser, section, key, value):
    try:
        a =config.get(section)
    except NoSectionError:
        config.add_section(section)
    
    config.set(section,key, value)

    with open(config_file, 'w+') as configfile:
            config.write(configfile)



def get_mpi_command(engine_name: str, configs: ConfigParser):

    name = engine_name + '_mpi'
    
    if configs.items('mpi'):
        try:
            mpi = configs.get('mpi', name)
            if not mpi:
                print("Engine specific mpi is not given, first option from mpi section will be used.")
                mpi = list(configs.items('mpi'))[0][1]
        except NoOptionError:
            print("Please set path to mpi in lsconfig.ini")
        else:
            return mpi
    else:
        print("Please set path to mpi in lsconfig.ini")