from tkinter import filedialog
import subprocess
import pathlib
import json


class Status():
    def __init__(self, directory) -> None:
        self.filepath = pathlib.Path(directory) / "status.json"
        self.status_dict = {}
        if self.filepath.exists():
            self.read_status()
        else:
            self.status_dict = {
                'gs_inp': 0,
                'td_inp': 0,
                'gs_cal': 0,
                'td_cal': 0
            }
        self.update_status()

    def read_status(self):
        with open(self.filepath) as f:
            data_dict = json.load(f)
            self.status_dict.update(data_dict)
            
    def update_status(self, key=None, value=None):
        if key is None and value is None:
            dict2json(self.status_dict, self.filepath)
        else:
            self.status_dict[key] = value
            dict2json(self.status_dict, self.filepath)
            return(self.status_dict)

    def check_status(self, key, value):
        try:
            if self.status_dict[key] == value:
                return True
            else:
                return False
        except KeyError:
            return False  

    def get_value(self, key):
        self.read_status()
        value = self.status_dict[key]
        return value

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


def show_message(label_name, message):
    """
    Shows a update
    """
    label_name['text'] = message
    label_name['foreground'] = 'black'

def dict2json(dictname, filename):
    filepath = pathlib.Path(filename)
    with open(filepath, 'w') as file:
        json.dump(dictname, file)