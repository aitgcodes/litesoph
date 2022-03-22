import subprocess
import pathlib
import os


def run_local(filename, directory, processors=None):
    """Runs the script file locally and captures the output."""
    filename = pathlib.Path(directory) / filename
    total_processors = os.cpu_count()
    if processors is not None:
        if processors <= total_processors and processors >= 0:
            processors= str(processors)
            result = subprocess.Popen(['mpirun', '-np', processors, 'python', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result.wait()
        else:
            raise "wrong number of processors"
    else:
        result = subprocess.Popen(['python', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.wait()
    return result