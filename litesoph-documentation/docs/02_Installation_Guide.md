# Installation Guide

Welcome to the installation guide for Litesoph

## Requirements

* Python version  >= 3.7.6 and < 3.11.0
* Pillow  version <= 9.5.0
* tkinter
* click
* numpy
* scipy
* matplotlib
* paramiko 
* scp 
* rsync

## Installation
Some very basic information. If you never used Litesoph before, maybe it is best to start here, otherwise you can just skip and go to the next sections.

### Python 
We currently only support python versions from  3.7.6 to 3.11.0, hence we recommend to check the python version installed in your machine.



###### Windows, Linux or MacOS
``` Python
python --version 
```

If the output is not in the given range, please reinstall the python with the following command:

###### Debian/Ubuntu
``` Python
sudo apt-get install python<version_number>
```

###### Windows
You can directly download the installer for the specific version of Python you want from the official Python website [here](https://www.python.org/downloads/). Follow these steps:

* Visit the Python downloads page.
* Scroll down to the section titled "Looking for a specific release?" and select the version you want from the list.
* Download the Windows installer (usually named something like python-<version>-amd64.exe for 64-bit systems).
* Run the installer and follow the prompts to install Python.

_Note_: During the installation process, ensure that you check the box that says "Add Python <version_number> to PATH" to make the Python executable accessible from the command line.


######  Conda Envoirnment

Proceed to install Anaconda from [here](https://www.anaconda.com/download) and install the conda envorinment.

_Note_: It takes some amount of time to install anaconda on a system given, do not panic if it looks stuck

* Create a new base class
* select a valid version from the list of python versions available.
* Use this envoirnment for working on litesoph.

