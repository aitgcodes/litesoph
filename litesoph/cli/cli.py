import os
import pathlib
from configparser import ConfigParser

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