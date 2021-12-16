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

def dict2file(dictname, filename):
    filepath = pathlib.Path(filename)
    with open(filepath, 'w') as status_file:
        status_file.write(json.dumps(dictname))                 

def search_string(directory,filename, string):
    """ Checks if a string is present in the file and returns boolean"""
    inf = str(directory) + '/' + str(filename)
    if string in open(inf).read():
        return True
    else:
        return False     

def open_file(outpath):
        text_file = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=((" Text Files", "*.xyz"),))
        text_file = open(text_file,'r')
        stuff = text_file.read()
        out_file = open(pathlib.Path(outpath) / "coordinate.xyz",'w')
        out_file.write(stuff)
        text_file.close()
        out_file.close()
        
def open_existing_project():
        oldProject = filedialog.askdirectory()

def runpython(fpath:str):
        subprocess.run(["python", fpath])

def show_message(label_name,message):
        """
        Shows a update
        """
        label_name['text'] = message
        label_name['foreground'] = 'black'    



