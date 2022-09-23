import pathlib
import json
import copy


class Status():

    __default_task = {'filename': '',
                    'label': '',
                    'param':'',
                    'script': 0,
                    'done': False,
                    'sub_local':{
                        'returncode' : None,
                        'n_proc' : None,
                        'restart' : '',
                        'log' : ''
                    },
                    'sub_network':{
                        'ip': '',
                        'username': '',
                        'remote_path': '',
                        'returncode' : None,
                        'cmd_out' : '',
                        'n_proc' : None,
                        'restart' : '',
                        'log' : ''
                    },
                    
                    }
    
    def __init__(self, directory, project_data) -> None:

        self.filepath = pathlib.Path(directory) / "status.json"
        self.status_dict = project_data

        if self.filepath.exists():
            self.read()
        else:
            self.save()
    

    def read(self):
        """ reads the status object from json file & updates the status dictionary"""

        with open(self.filepath) as f:
            data_dict = json.load(f)
            for key, value in data_dict.items():
                self.status_dict[key] = value
            
    def update(self, path:str , value):
        """ updates the status dictionary and writes to json file
         if path(string of keys separated by '.') and value are given"""

        keys = path.split('.')
        recursive_update(keys, value, self.status_dict)
        self.save()

    def get(self, path:str):
        """returns the value from the nested dictionary 
        with path(string of keys separated by '.')"""

        self.read()
        try:
            obj = dict(self.status_dict)
            list = path.split('.')
            for key in list:
                obj = obj[key]   
            return obj
        except KeyError:
            raise KeyError("Key not found")  

    def check(self, path, value):
        """ returns boolean value if given path(keys separated by '.') and value match"""

        try:
            if self.get(path) == value:
                return True
            else:
                return False
        except KeyError:
            return False        

    def set_new_task(self, engine:str, task:str):
        
        engine_list = self.status_dict.keys()
        if not engine in engine_list:
            self.status_dict[engine] = {}
            self.status_dict[engine][task] = copy.deepcopy(self.__default_task)
        else:
            self.status_dict[engine][task] = copy.deepcopy(self.__default_task)
        
    def save(self):
        with open(self.filepath, 'w') as f:
            try:
                json.dump(self.status_dict, f, indent= 3)
            except TypeError:
                raise   

def recursive_update(keys :list, value, status_dict: dict):
            
    length = len(keys)
    key = keys.pop(0)
    if length == 1:
        status_dict[key] = value
    else: 
        recursive_update(keys, value, status_dict[key])

class file_check:
    def __init__(self, check_list:list, dir) -> None:
        self.list = check_list
        self.dir = dir

    def check_list(self, fname):
        for item in self.list[0:]:
            try:
                check = self.search_string(self.dir, fname, item)
                if check is not True:
                    break
            except FileNotFoundError:
                print("File does not exist")
                check = False
                break    
        return(check)


    def search_string(directory, filename, string):
        """ Checks if a string is present in the file and returns boolean"""

        filename = pathlib.Path(directory) / filename
        with open(filename, 'r') as f:
            text = f.read()
            if string in text:
                return True
            else:
                return False


def show_message(label_name, message):
    """ Shows a update """

    label_name['text'] = message
    label_name['foreground'] = 'black'


