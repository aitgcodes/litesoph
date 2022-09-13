from configparser import ConfigParser
import pathlib
import re
import os
from tabnanny import check

from ..utilities.job_submit import SubmitNetwork

GROUND_STATE = 'ground_state'
RT_TDDFT_DELTA = 'rt_tddft_delta'
RT_TDDFT_LASER = 'rt_tddft_laser'
SPECTRUM = 'spectrum'
TCM = 'tcm'
MO_POPULATION_CORRELATION = 'mo_population'
MASKING = 'masking'

class TaskError(RuntimeError):
    """Base class of error types related to any TASK."""


class TaskSetupError(TaskError):
    """Calculation cannot be performed with the given parameters.

    Typically raised before a calculation."""



class InputError(TaskSetupError):
    """Raised if inputs given to the calculator were incorrect.

    Bad input keywords or values, or missing pseudopotentials.

    This may be raised before or during calculation, depending on
    when the problem is detected."""


class TaskFailed(TaskError):
    """Calculation failed unexpectedly.

    Reasons to raise this error are:
      * Calculation did not converge
      * Calculation ran out of memory
      * Segmentation fault or other abnormal termination
      * Arithmetic trouble (singular matrices, NaN, ...)

    Typically raised during calculation."""


class ReadError(TaskError):
    """Unexpected irrecoverable error while reading calculation results."""


class TaskNotImplementedError(NotImplementedError):
    """Raised if a calculator does not implement the requested property."""


class PropertyNotPresent(TaskError):
    """Requested property is missing.

    Maybe it was never calculated, or for some reason was not extracted
    with the rest of the results, without being a fatal ReadError."""


class Task:

    """It takes in the user input dictionary as input."""

    BASH_filename = 'job_script.sh'
    job_script_first_line = "#!/bin/bash"
    remote_job_script_last_line = "touch Done"


    def __init__(self, engine_name, status, project_dir, lsconfig) -> None:
        
        self.status = status
        self.lsconfig = lsconfig
       
        self.project_dir = project_dir
        self.task = None
        self.filename = None
        self.input_data_files = []
        self.output_data_file = []
        self.task_state = None

        self.engine_name = engine_name
        self.engine_path = self.lsconfig['engine'].get(self.engine_name , self.engine_name)
        mpi_path = self.lsconfig['mpi'].get('mpirun', 'mpirun')
        self.mpi_path = self.lsconfig['mpi'].get(f'{self.engine_name}_mpi', mpi_path)
        self.python_path = self.lsconfig['programs'].get('python', 'python')
        
    def create_template(self):
        ...
    
    def reset_lsconfig(self, lsconfig):
        self.engine_path = lsconfig['engine'].get(self.engine_name , self.engine_name)
        mpi_path = lsconfig['mpi'].get('mpirun', 'mpirun')
        self.mpi_path = lsconfig['mpi'].get(f'{self.engine_name}_mpi', mpi_path)

    @staticmethod
    def create_directory(directory):
        absdir = os.path.abspath(directory)
        if absdir != pathlib.Path.cwd and not pathlib.Path.is_dir(directory):
            os.makedirs(directory)

    def write_input(self, template=None):
        ...        

    def check_prerequisite(self, network=False) -> bool:
        """ checks if the input files and required data files for the present task are present"""
        return
        inupt_file = self.project_dir.parent / self.filename
        
        if not pathlib.Path(inupt_file).exists():
            check = False
            msg = f"Input file:{inupt_file} not found."
            raise FileNotFoundError(msg)

        if network:
            if not  self.bash_file.exists():
                msg = f"job_script:{self.bash_file} not found."
                raise FileNotFoundError(msg)
            #self.bash_filename =  self.bash_file.relative_to(self.project_dir.parent)
            return
            
        for item in self.input_data_files:
            item = self.project_dir.parent / item
            if not pathlib.Path(item).exists():
                msg = f"Data file:{item} not found."
                raise FileNotFoundError(msg)
    
    def create_job_script(self) -> list:
        """Create the bash script to run the job and "touch Done" command to it, to know when the 
        command is completed."""
        job_script = []

        job_script.append(self.job_script_first_line)
        
        return job_script

    def write_job_script(self, job_script=None):
        if job_script:
            self.job_script = job_script
        self.bash_file = self.project_dir / self.BASH_filename
        with open(self.bash_file, 'w+') as f:
            f.write(self.job_script)

    def add_proper_path(self, path):
        """this adds in the proper path to the data file required for the job"""
        
        if str(self.project_dir.parent) in self.template:
            text = re.sub(str(self.project_dir.parent), str(path), self.template)
        self.write_input(text)

    def set_submit_local(self, *args):
        from litesoph.utilities.job_submit import SubmitLocal
        self.sumbit_local = SubmitLocal(self, *args)

    def run_job_local(self,cmd):
        cmd = cmd + ' ' + self.BASH_filename
        self.sumbit_local.run_job(cmd)

    def connect_to_network(self, *args, **kwargs):
        self.submit_network = SubmitNetwork(self, *args, **kwargs)
    
    def read_log(self, file):
        with open(file , 'r') as f:
            text = f.read()      
        return text
        
    def check_output(self):
        
        try:
            if hasattr(self, 'submit_network'):
                exist_status, stdout, stderr = self.net_cmd_out
            else:
                exist_status, stdout, stderr = self.local_cmd_out
        except AttributeError:
            raise TaskFailed("Job not completed.")
        else:
            return True

def assemable_job_cmd(engine_cmd:str = None, np: int =1, cd_path: str=None, 
                        mpi_path: str = None,
                        remote : bool = False,
                        scheduler_block : str = None,
                        module_load_block : str = None,
                        extra_block : str = None) -> str:
    job_script_first_line = "#!/bin/bash"
    remote_job_script_last_line = "touch Done"
    
    job_script = [job_script_first_line]
    
    if remote:
        if scheduler_block:
            job_script.append(scheduler_block)
        if module_load_block:
            job_script.append(module_load_block)

    if cd_path:
        job_script.append(f'cd {cd_path}')
    
    if engine_cmd:
        if np > 1:
            if not mpi_path:
                mpi_path = 'mpirun'
            job_script.append(f'{mpi_path} -np {np:d} {engine_cmd}')
        else:
            job_script.append(engine_cmd)

    if extra_block:
        job_script.append(extra_block)

    if remote:
        job_script.append(remote_job_script_last_line)

    job_script = '\n'.join(job_script)
    return job_script


def pbs_job_script(name):

    head_job_script = f"""
#!/bin/bash
#PBS -N {name}
#PBS -o output.txt
#PBS -e error.txt
#PBS -l select=1:ncpus=4:mpiprocs=4
#PBS -q debug
#PBS -l walltime=00:30:00
#PBS -V
cd $PBS_O_WORKDIR
   """
    return head_job_script






  

