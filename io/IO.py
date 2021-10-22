from pathlib import Path
from typing import Any, Dict


class user_input:

    user_param = {
        'work_dir': None,
        'mode': None,
        'geometry': None,
        'xc': None,
        'spinpol':None,
        'tolerance':None,
        'convergance': {},
        'basis':None,
        'vacuum':None,
        'h': None,
        'box': None,
        'properties': None,
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