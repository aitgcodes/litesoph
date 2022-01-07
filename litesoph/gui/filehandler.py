from tkinter import filedialog
import subprocess
import pathlib
import json


class Status():
    def __init__(self, directory) -> None:
        self.filepath = pathlib.Path(directory) / "status.txt"
        self.status_dict = {}
        if self.filepath.exists():
            self.status_dict = self.read_status()
        else:
            self.status_dict = {
                'gs_inp': 0,
                'td_inp': 0,
                'gs_cal': 0,
                'td_cal': 0
            }
        self.update_status()

    def read_status(self):
        with open(self.filepath, 'r') as f:
            data = f.read()
            data_dict = json.loads(data)
            self.status_dict.update(data_dict)
            return(self.status_dict)

    def update_status(self, key=None, value=None):
        if key is None and value is None:
            dict2file(self.status_dict, self.filepath)
        else:
            self.status_dict[key] = value
            dict2file(self.status_dict, self.filepath)
            return(self.status_dict)

    def check_status(self, key, value):
        if self.status_dict[key] == value:
            return True
        else:
            return False

class file_check:
    def __init__(self, check_list:list, dir) -> None:
        self.list = check_list
        self.dir = dir

    def check_list(self, fname):
        for item in self.list[0:]:
            try:
                check = search_string(self.dir, fname, item)
                if check is not True:
                    #print("{} is not found".format(item))
                    break
            except FileNotFoundError:
                print("File does not exist")
                check = False
                break    
        return(check)

    # gpaw_gs_dict={'inp':'gs.py',
    #          'out': 'gs.out',
    #          'check_list':['Converged', 'Fermi level:','Total:']}

    # gpaw_td_dict={'inp':'td.py',
    #          'out': 'tdx.out',
    #          'check_list':['Writing','Total:']}

    # gpaw_pulse_dict={'inp':'td_pulse.py',
    #          'out': 'tdpulse.out',
    #          'check_list':['Writing','Total:']}

def dict2file(dictname, filename):
    filepath = pathlib.Path(filename)
    with open(filepath, 'w') as status_file:
        status_file.write(json.dumps(dictname))


def search_string(directory, filename, string):
    """ Checks if a string is present in the file and returns boolean"""
    inf = str(directory) + '/' + str(filename)
    inf = pathlib.Path(inf)
    if string in open(inf).read():
        return True
    else:
        return False


def open_file(outpath):
    text_file = filedialog.askopenfilename(
        initialdir="./", title="Select File", filetypes=((" Text Files", "*.xyz"),))
    text_file = open(text_file, 'r')
    stuff = text_file.read()
    out_file = open(pathlib.Path(outpath) / "coordinate.xyz", 'w')
    out_file.write(stuff)
    text_file.close()
    out_file.close()


def show_message(label_name, message):
    """
    Shows a update
    """
    label_name['text'] = message
    label_name['foreground'] = 'black'
