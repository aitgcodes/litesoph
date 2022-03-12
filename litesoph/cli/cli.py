import os
import pathlib
from configparser import ConfigParser
import subprocess
import click

import litesoph 

config_file = pathlib.Path.home() / "lsconfig.ini"

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings = CONTEXT_SETTINGS)
@click.version_option(version=litesoph.__version__)
def cli():
    ...


@cli.command()
def gui():
    """Starts the gui."""

    lsconfig = ConfigParser()
    lsconfig.read(config_file)

    from litesoph.gui.gui import AITG
    app = AITG(lsconfig)
    app.title('LITESOPH')
    app.resizable(True, True)
    app.mainloop()


@cli.command(no_args_is_help=True)
@click.option('-c', '--create', is_flag=True,
                help = "creates config file with guess values: ~/lsconfig.ini")
@click.option('-e', '--open-file', is_flag=True,
                help = "opens lsconfig file in terminal.")
def config(create, open_file):
    """create and edit lsconfig.ini file."""
    from litesoph.config import write_config
    if create:
        write_config()
        return

    if open_file:
        subprocess.run(['vim',f'{config_file}'])
        return
