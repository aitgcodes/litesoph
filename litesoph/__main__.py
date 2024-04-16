from sys import path
path.insert(0, path[0] + '/..')

from litesoph.cli.cli import cli 

cli()