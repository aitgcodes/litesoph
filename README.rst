============================
 LITESOPH
============================


Requirements
============

  * Python 3.7.6 or higher
  * Tkinter
  * click
  * Numpy
  * Matplotlib
  * Paramiko
  * scp
  * Rsync

Installation
=============================================================================================================

.. code-block:: console

  $ git clone -b main https://github.com/LITESOPH/litesoph.git
  $ pip install <path-to-litesoph>


Configuration
=============================================================================================================
To create lsconfig file:
  .. code-block:: console

    $ litesoph config -c
  
To edit lsconfig file:
  .. code-block:: console

    $ litesoph config -e

Example lsconfig file
=========

.. code-block:: console

  [path]
  lsproject = <litesoph project path>
  lsroot = <installation path of litesoph>

  [visualization_tools]
  vmd = <path to vmd || e.g. /usr/local/bin/vmd>
  vesta = <path to vesta || e.g. /usr/local/bin/vesta>

  [engine]
  gpaw =
  nwchem =<binary path of nwchem>
  octopus =<binary path of octopus>


  [programs]
  python = <path to python>

  [mpi]
  mpirun = <path to mpirun || e.g. /usr/local/bin/mpirun>
  gpaw_mpi = <path to mpirun through which gpaw is compiled|| e.g. /usr/local/bin/mpirun>
  octopus_mpi =<path to mpirun through which octopus is compiled|| e.g. /usr/local/bin/mpirun>
  nwchem_mpi =<path to mpirun through which nwchem is compiled|| e.g. /usr/local/bin/mpirun>


Usage
===========================================================================================================

To start gui application, run:

.. code-block:: console

  $ litesoph gui


