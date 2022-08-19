import os
import subprocess
import pathlib
from configparser import ConfigParser, NoOptionError, NoSectionError

import litesoph

user_data_dir = pathlib.Path.home() / ".litesoph"

config_file = user_data_dir / "lsconfig.ini"


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
    """ makes a ~/.litesoph directory to store app data.
        and writes lsconfig.ini with guess values. """

    if not user_data_dir.is_dir():
        try:
            os.mkdir(user_data_dir)
        except FileExistsError as e:
            pass

    config = ConfigParser(allow_no_value=True)
    config.add_section('path')
    config.set('path','lsproject', str(pathlib.Path.home()))
    create_default_config(config, sections)

    config.set('mpi', 'gpaw_mpi', '')
    config.set('mpi', 'octopus_mpi', '')
    config.set('mpi', 'nwchem_mpi', '')

    print(f'Creating {str(config_file)} ...')
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
            print(f"Please set lsroot in {str(config_file)}")
            exit()
        else:
            return lsroot
    if name == "vis":
        try:
           vis_tool = list(lsconfig.items("visualization_tools"))[0][1]
        except:
            print(f"Please set path to vmd or vesta in {str(config_file)} and first one will be used")
        else:
            return vis_tool

def read_config():
    """Reads the lsconfig.ini file and retrun configparser."""

    if not config_file.is_file():
        raise FileNotFoundError(f"{str(config_file)} doesn't exists")

    lsconfig = ConfigParser(allow_no_value=False)
    lsconfig.read(config_file)
    return lsconfig

def set_config(config: ConfigParser, section, key=None, value=None, list: list=None):
    """ updates lsconfig object and writes it to lsconfig.ini file"""

    try:
        a =config.items(section)
    except NoSectionError:
        config.add_section(section)
        
    if list:
        for item in dict.items():
            config.set(section, item[0],item[1])
    else:

        config.set(section, key, value)

    with open(config_file, 'w+') as configfile:
            config.write(configfile)



def get_mpi_command(engine_name: str, configs: ConfigParser):
    """returns mpi command from lsconfig."""

    name = engine_name + '_mpi'
    
    if configs.items('mpi'):
        try:
            mpi = configs.get('mpi', name)
            if not mpi:
                print("Engine specific mpi is not given, first option from mpi section will be used.")
                mpi = list(configs.items('mpi'))[0][1]
        except NoOptionError:
            print(f"Please set path to mpi in{str(config_file)}")
        else:
            return mpi
    else:
        print(f"Please set path to mpi in {str(config_file)}")

def remove_empty_value(config_items):
    dict ={}
    for key, val in config_items:
        if val:
            dict[key] = val
    return dict

def none2emptystr(input_dict:dict):
    rdict = {}
    for key, val in input_dict.items():
        if type(val) == dict:
            rdict[key] = {k : ('' if s is None else s) for k, s in val.items()}
        else:
            rdict[key] = val
    return rdict

######### convert config file to dictionary #########

def config_to_dict(infile):

    """converts configparser to dictionary object """
    config = ConfigParser()
    config.read(infile)
    my_config_parser_dict = {s:remove_empty_value(config.items(s)) for s in config.sections()}
    return dict(my_config_parser_dict)


################## convert dictionary to config file #############

def dict_to_config(input_dict, configfilename):

    """converts dictionary to configfile  object """
    parser = ConfigParser()
    parser.read_dict(none2emptystr(input_dict))

    with open(configfilename,'w') as fp:
        parser.write(fp)