from pathlib import Path
from typing import Any, Dict


class user_input:

    user_input_param: Dict[str : Any] = {
        'work_dir': None,
        'calc_mode': None,
        'structure': None,
        'dft':{},
        'tolerance':None,
        'convergance': {},
        'basis':{},
        'box': {},
        'properties': {},
        'engine':None,
    }

def write2file(filename, template, input_param) -> None:
    """Write template to a file.
    
    filename: str or file
        full path of the file to write to.
    template: str
        script template which needs to be written to file.
    input_param: dict
        dictonary to format tempalte."""
    template = template.format(**input_param)
    filename = Path(filename)

    with open(filename, 'w+') as f:

        f.truncate()
        f.seek(0)
        f.write(template)