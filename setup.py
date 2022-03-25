#!/usr/bin/env python

"""The setup script."""

import re
from pathlib import Path
from setuptools import setup, find_packages


python_requires = '>=3.7'
requirements = [
    'click>=8.0.3',
    'ase', 'matplotlib','numpy',
    'paramiko', 'scp'
]

setup_requirements = []

txt = Path('litesoph/__init__.py').read_text()
version = re.search("__version__ = '(.*)'", txt).group(1)

setup(name = 'litesoph',
    version=version,
    description="Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena",
    maintainer='LITESOPH-group',
    python_requires=python_requires,
    entry_points={
        'console_scripts': [
            'litesoph=litesoph.cli.cli:cli',
        ]
    },
    install_requires=requirements,
    packages=find_packages(),
    package_data={'litesoph.gui.images':['*.png','*.jpg','*.xbm']},
    setup_requires=setup_requirements,
    
)
