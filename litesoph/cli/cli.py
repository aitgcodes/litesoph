import os
import pathlib
import subprocess
import click
from litesoph.config import config_file, read_config, write_config
import litesoph 



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings = CONTEXT_SETTINGS)
@click.version_option(version=litesoph.__version__)
def cli():
    ...


@cli.command()
def gui():
    """Starts the gui."""

    try:
        lsconfig = read_config()
    except FileNotFoundError as e:
        print(f"{str(config_file)} doesn't exists.\n")
        print("creating  lsconfig with default value.\n")
        write_config()
        lsconfig = read_config()
        print(" ")
        print("     litesoph config")
        print(" ")
        print("Use above command for further help in configuration")
    

    from litesoph.gui.gui import GUIAPP
    app = GUIAPP(lsconfig)
    app.run()


@cli.command(no_args_is_help=True)
@click.option('-c', '--create', is_flag=True,
                help = f"creates {str(config_file)} file with guess values")
@click.option('-e', '--open-file', is_flag=True,
                help = "opens lsconfig file in terminal.")
def config(create, open_file):
    """create and edit lsconfig.ini file."""
   
    if create:
        write_config()
        return

    if open_file:
        if config_file.exists():
            subprocess.run(['vim',f'{config_file}'])
        else:
            print("lsconfig file doesn't exists.")
            print("create lsconfig file using command.")
            print(" ")
            print("     litesoph config -c")
        return
