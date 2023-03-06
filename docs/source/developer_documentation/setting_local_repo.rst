Developer Guidelines
========================

Setting up your local repository
---------------------------------
1. Fork the LITESOPH/litesoph repo into your github account.

2. ‘git clone’ this newly forked repo into your local machine.

Setting up test environment
----------------------------
Conda environment
^^^^^^^^^^^^^^^^^^
Step-1: Download Anaconda_ package manager.

Step-2: Install Anaconda_ in the HOME directory.

Step-3: Create new virtual environment(say,test-lite).For this, you can use the following command : 

.. code-block:: python

   $ conda create -n test-lite python=3.7.6

Step-4: Activate the test-lite environment. For this, you can use the following command: 

.. code-block:: python

   $ conda activate test-lite

Step-5: Install litesoph using the following command: 

.. code-block:: python

   $ pip install -e <path litesoph package>

Python venv environment
^^^^^^^^^^^^^^^^^^^^^^^
Step-1: Check Python version.

.. code-block:: python
   
   $ python –version

Step-2: If it is <3.7.6 upgrade the Python version to 3.7.6 if possible else use conda environment.

Step-3: Create new virtual environment (say, test-lite). For this, use the following command:

.. code-block:: python
   $python -m venv test-lite

Step-4: Activate the test-lite environment. Use the following command:

.. code-block:: python

   $ source ~/test-lite/bin/activate

Step-5: Install litesoph. Use the following command: 

.. code-block:: python

   $ pip install -e <path to litesoph package>

Coding Standards
-----------------
The LITESOPH project adheres to PEP-8 guidelines for writing code in Python. 
Summary of the PEP-8 guidelines and advantages of using this system is explained 
in a clear and concise manner in an article published by `Real Python <https://realpython.com/python-pep8/>`_. 
For more information refer to the original  `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_ document.

.. _Anaconda : https://docs.anaconda.com/anaconda/install/linux/


