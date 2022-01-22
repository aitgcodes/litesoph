import pathlib

class UserInput:

    user_param = {
        'directory': None,
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

def write2file(directory,filename, template) -> None:
    """Write template to a file.
    
    directroy: str
        full path of the directory to write to.
    filename: str
        name of the file with extension
    template: str
        script template which needs to be written to file.
    """

    filename = pathlib.Path(directory) / filename

    with open(filename, 'w+') as f:

        f.truncate()
        f.seek(0)
        f.write(template)
