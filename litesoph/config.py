import os
import subprocess
import pathlib
from configparser import ConfigParser, NoOptionError, NoSectionError

user_data_dir = pathlib.Path.home() / ".litesoph"
config_file = user_data_dir / "lsconfig.ini"

# Predefined sections and their respective commands or paths to be included in the default configuration
sections = {
    'visualization_tools': ['vmd', 'vesta'],
    'engine': ['gpaw', 'nwchem', 'octopus'],
    'programs': ['python'],
    'mpi': ['mpirun'],
}

def get_path(name):
    """
    Attempts to find the path of a given executable using the 'which' command.

    Parameters:
    - name (str): The name of the executable to find.

    Returns:
    - str: The full path to the executable if found; None otherwise.
    """
    print(f"Checking for {name}...")
    p = subprocess.run(['which', name], capture_output=True, text=True)
    if p.stdout and p.returncode == 0:
        path = p.stdout.strip()
        print(f"Found {name} in {path}")
        return path
    else:
        print(f"Did not find {name}")
        return None

def create_default_config(config: ConfigParser, sections: dict):
    """
    Populates a ConfigParser object with default settings based on available executables.

    Parameters:
    - config (ConfigParser): The ConfigParser object to populate.
    - sections (dict): A dictionary of sections and their respective options to check and set.
    """
    for section, options in sections.items():
        config.add_section(section)
        for option in options:
            path = get_path(option)
            config.set(section, option, path if path is not None else '')

def write_config():
    """
    Creates a default configuration file for litesoph in the user's home directory.
    """
    if not user_data_dir.exists():
        os.makedirs(user_data_dir, exist_ok=True)

    config = ConfigParser(allow_no_value=True)
    config.add_section('path')
    config.set('path', 'lsproject', str(pathlib.Path.home()))
    create_default_config(config, sections)

    # Additional MPI configurations
    for engine in sections['engine']:
        config.set('mpi', f'{engine}_mpi', '')

    print(f'Creating {config_file} ...')
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    print('Done.')

def read_config():
    """
    Reads the lsconfig.ini file and returns a ConfigParser object.

    Returns:
    - ConfigParser: The loaded configuration.
    
    Raises:
    - FileNotFoundError: If the lsconfig.ini file does not exist.
    """
    if not config_file.exists():
        raise FileNotFoundError(f"{config_file} doesn't exist")

    lsconfig = ConfigParser()
    lsconfig.read(config_file)
    return lsconfig

# Additional functions like check_config, set_config, get_mpi_command, etc., remain unchanged.

