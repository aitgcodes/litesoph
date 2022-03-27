import pathlib
import os

# class UserInput:

#     user_param = {
#         'directory': None,
#         'mode': None,
#         'geometry': None,
#         'xc': None,
#         'spinpol':None,
#         'tolerance':None,
#         'convergence': None,
#         'basis':None,
#         'vacuum':None,
#         'h': None,
#         'box': None,
#         'properties': None,
#         'engine':None,
#     }

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
    file_exists = os.access(filename, os.F_OK)
    parent_writeable = os.access(filename.parent, os.W_OK)
    file_writeable = os.access(filename, os.W_OK)
    
    if ((not file_exists and not parent_writeable) or
        (file_exists and not file_writeable)):
        msg = f'Permission denied acessing file: {filename}'
        raise PermissionError(msg)

    with open(filename, 'w+') as f:

        f.truncate()
        f.seek(0)
        f.write(template)

def read_file(filename) -> str:

    with open(filename, 'r') as f:
        txt = f.read()

    return txt
