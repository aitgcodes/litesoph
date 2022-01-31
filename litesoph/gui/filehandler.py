from tkinter import filedialog
import subprocess
import pathlib
import json

class Status():

    default_dict={
        'engine':'',
        'gpaw':{'ground_state':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                      },   
                'rt_tddft_delta':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                     },
                'rt_tddft_laser':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                     },             
                        },
        'octopus':{'gs':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                      },   
                'td':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                      },       
                        },
    
        'nwchem':{'gs':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                      },   
                'td':{  'state': 0,
                        'param':{},
                        'inp': 0,
                        'cal': 0
                     },       
                        }                                
    }

    def __init__(self, directory) -> None:

        self.filepath = pathlib.Path(directory) / "status.json"
        self.status_dict = {}
        if self.filepath.exists():
            self.read_status()
        else:
            self.status_dict = self.default_dict
        self.update_status()

    def read_status(self):
        """ reads the status object from json file & updates the status dictionary"""

        with open(self.filepath) as f:
            data_dict = json.load(f)
            self.status_dict.update(data_dict)
            
    def update_status(self, path:str =None, value=None):
        """ updates the status dictionary and writes to json file
         if path(string of keys separated by '.') and value are given"""

        if path is None and value is None:
            dict2json(self.status_dict, self.filepath)
        else:
            obj = self.status_dict
            list = path.split('.')
            for i in range(len(list)):
                for key in obj.keys():
                    if key == list[i]:
                        if isinstance(obj[key],dict):
                            obj =obj[key]               
                        else:
                            obj[key] = value 

            dict2json(self.status_dict, self.filepath)

    def get_status(self,path:str):
        """returns the value from the nested dictionary 
        with path(string of keys separated by '.')"""

        self.read_status()
        try:
            obj = self.status_dict
            list = path.split('.')
            for i in range(len(list)):
                key = list[i] 
                obj = obj[key]   
            return obj
        except KeyError:
            raise KeyError("Key not found")  

    def check_status(self, path, value):
        """ returns boolean value if given path(keys separated by '.') and value match"""

        try:
            if self.get_value(path) == value:
                return True
            else:
                return False
        except KeyError:
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


def search_string(directory, filename, string):
    """ Checks if a string is present in the file and returns boolean"""

    inf = str(directory) + '/' + str(filename)
    inf = pathlib.Path(inf)
    if string in open(inf).read():
        return True
    else:
        return False


def show_message(label_name, message):
    """ Shows a update """

    label_name['text'] = message
    label_name['foreground'] = 'black'

def dict2json(dictname, filename):
    filepath = pathlib.Path(filename)
    with open(filepath, 'w') as file:
        json.dump(obj=dictname, fp=file, indent= 3)
