import pathlib

class user_input:

    user_param = {
        'work_dir': None,
        'mode': None,
        'geometry': None,
        'xc': None,
        'spinpol':None,
        'tolerance':None,
        'convergence': None,
        'basis':None,
        'vacuum':None,
        'h': None,
        'box': None,
        'properties': None,
        'engine':None,
    }

def write2file(directory,filename, template, input_param) -> None:
    """Write template to a file.
    
    directroy: str
        full path of the directory to write to.
    filename: str
        name of the file with extension
    template: str
        script template which needs to be written to file.
    input_param: dict
        dictonary to format tempalte."""
    template = template.format(**input_param)
    filename = pathlib.Path(directory) / filename

    with open(filename, 'w+') as f:

        f.truncate()
        f.seek(0)
        f.write(template)