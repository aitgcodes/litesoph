============================
 About LITESOPH
============================
The LITESOPH project is aimed at developing a comprehensive toolkit to launch, monitor, manage and analyse 
large-scale simulations of photo-induced phenomena in a high-performance computing (HPC) environment. 
It is designed to serve the needs of computational researchers interested in solar energy conversion 
applications (photovoltaics, water-splitting catalysts, solar fuels, etc.), opto-electronic materials, 
photochemistry and photobiology. The toolkit consists of several Python-based layers driven by popular 
and open-source TDDFT codes like OCTOPUS, GPAW and NWChem.

The project is currently funded by `MeitY <https://www.meity.gov.in/>`_ through the National Supercomputing Mission's "Applications for 
Materials and Computational Chemistry" initiative.

.. _engines:

Engines Interfaced with LITESOPH
===================================
There are three engines implimented in :ref:`LITESOPH`. The details of these engines with their Installation Instruction are given below:


.. _GPAW:

`GPAW <https://wiki.fysik.dtu.dk/gpaw/index.html>`_    (version 20.1.0 or later)
      is a density-functional theory (DFT) `Python <https://www.python.org/>`_ code based on the projector-augmented wave 
(`PAW <https://wiki.fysik.dtu.dk/gpaw/documentation/introduction_to_paw.html#introduction-to-paw>`_) method 
and the atomic simulation environment (`ASE <https://wiki.fysik.dtu.dk/ase/>`_).The wave functions can be described with:

* Plane-waves (`pw <https://wiki.fysik.dtu.dk/gpaw/documentation/basic.html#manual-mode>`_)

* Real-space uniform grids, multigrid methods and the finite-difference approximation (`fd <https://wiki.fysik.dtu.dk/gpaw/documentation/basic.html#manual-stencils>`_)

* Atom-centered basis-functions (`lcao <https://wiki.fysik.dtu.dk/gpaw/documentation/lcao/lcao.html#lcao>`_)
.. note::

Before installing this engine, go to `GPAW <https://wiki.fysik.dtu.dk/gpaw/index.html>`_  and its `Installation Instruction <https://wiki.fysik.dtu.dk/gpaw/install.html>`_  for details.


.. _Octopus:

`Octopus <https://octopus-code.org/wiki/Main_Page>`_   (version 11.4)
        is a scientific program aimed at the ab initio virtual experimentation on a hopefully 
ever-increasing range of system types. Electrons are described quantum-mechanically within density-functional theory (DFT), in its time-dependent form (TDDFT) when doing simulations in time. Nuclei are described classically as point particles. Electron-nucleus interaction is described within the pseudopotential approximation.

For optimal execution performance Octopus is parallelized using MPI and OpenMP and can scale to tens of thousands of processors. It also has support for graphical processing units (GPUs) through OpenCL and CUDA.

Octopus is free software, released under the GPL license, so you are free to download it, use it and modify it.



.. note::

Before installing this engine, go to `Octopus <https://octopus-code.org/wiki/Main_Page>`_  and its `Installation Instruction <https://octopus-code.org/wiki/Manual:Installation>`_ for details.
 
 
.. _NWChem:

`NWChem <https://nwchemgit.github.io/>`_ (version 7.0.0 or later)
  aims to provide its users with computational chemistry tools that are scalable both in their 
ability to treat large scientific computational chemistry problems efficiently, and in their use of available parallel computing resources from high-performance parallel supercomputers to conventional workstation clusters.

NWChem software can handle:

Biomolecules, nanostructures, and solid-state
From quantum to classical, and all combinations
Ground and excited-states
Gaussian basis functions or plane-waves
Scaling from one to thousands of processors
Properties and relativistic effects
.. note::

Before installing this engine, go to `NWChem <https://nwchemgit.github.io/>`_  and its `Installation Instruction <https://nwchemgit.github.io/Download.html>`_ for details.
 
  

Requirements
=============
Before installing LITESOPH, the following modules or packages are required:

  * `Python <https://www.w3schools.com/python/>`_ 3.7.6 or later
  * `Tkinter <https://docs.python.org/3/library/tkinter.html>`_
  * click_
  * NumPy_
  * SciPy_
  * Matplotlib_
  * Paramiko_
  * scp_
  * Rsync_

Getting the source code of LITESOPH
========================================
You can get the source from a zip-file or from Git:

**Zip-file:** You can get the source as a zip-file for the latest stable release (:download:`litesoph-main.zip <https://github.com/LITESOPH/litesoph/archive/refs/heads/main.zip>`)

**Git clone:** Alternatively, you can get the source for the latest stable release from github

$ git clone -b main https://github.com/LITESOPH/litesoph.git

Install it using the following command

$ pip install <path-to-litesoph>

Installation
=============================================================================================================
After installing above Requirements and Engines, you are ready to install LITESOPH using the following commands:

.. code-block:: console

  $ git clone -b main https://github.com/LITESOPH/litesoph.git
  $ pip install <path-to-litesoph> #Find the path to litesoph using "which litesoph"


Configuration
===============
To create :ref:`lsconfig file <lsconfig>`:

  .. code-block:: console

    $ litesoph config -c
  
To edit lsconfig file:
  .. code-block:: console

    $ litesoph config -e

.. _lsconfig:

Example lsconfig file
===============================
Here is an example of lsconfig file.

.. code-block:: console

  [path]
  lsproject = <litesoph project path>
  lsroot = <installation path of litesoph>

  [visualization_tools]
  vmd = <path to vmd || e.g. /usr/local/bin/vmd ||can be obtained using :command:`which vmd` >
  vesta = <path to vesta || e.g. /usr/local/bin/vesta||can be obtained using :command:`which vesta` >

  [engine]
  gpaw = <path of gpaw||can be obtained using :command:`which gpaw`> 
  nwchem =<binary path of nwchem||can be obtained using :command:`which nwchem`>
  octopus =<binary path of octopus ||can be obtained using :command:`which octopus`>

  [programs]
  python = <path to python||can be obtained using :command:`which python`>

  [mpi]
  mpirun = <path to mpirun || e.g. /usr/local/bin/mpirun ||can be obtained using :command:`which mpirun`>
  gpaw_mpi = <path to mpirun through which gpaw is compiled|| e.g. /usr/local/bin/mpirun>
  octopus_mpi =<path to mpirun through which octopus is compiled|| e.g. /usr/local/bin/mpirun>
  nwchem_mpi =<path to mpirun through which nwchem is compiled|| e.g. /usr/local/bin/mpirun>

.. _usage:

Usage
===========================================================================================================

To start gui application, run:

.. code-block:: console

  $ litesoph gui


.. _NumPy: http://docs.scipy.org/doc/numpy/reference/
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _click : https://pypi.org/project/click/
.. _Matplotlib : https://pypi.org/project/matplotlib/
.. _Paramiko : https://pypi.org/project/paramiko/
.. _scp : https://www.ssh.com/academy/ssh/scp
.. _Rsync : https://rsync.samba.org/