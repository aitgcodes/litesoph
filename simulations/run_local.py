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
            result = subprocess.run(['mpirun', '-np', processors, 'python', filename], capture_output=True, text=True)
        else:
            raise " worng number of processors"
    else:
        result = subprocess.run(['python', filename], capture_output=True, text=True)

    return result