from tkinter import filedialog
import subprocess
import pathlib 


class Status():
        status_dict = { 'gs_inp' : False,
                    'td_inp' : False,
                    'gs_cal' : False,
                    'td_cal' : False
                  }
        status_template = """
gs_inp = {gs_inp}
td_inp = {td_inp}
gs_cal = {gs_cal}
td_cal = {td_cal}
    """          
                 

def search_string(directory,filename, string):
    """ Checks if a string is present in the file and returns boolean"""
    inf = str(directory) + '/' + str(filename)
    if string in open(inf).read():
        return True
    else:
        return False     

def open_file(outpath):
        text_file = filedialog.askopenfilename(initialdir="./", title="Open Text File", filetypes=((" Text Files", "*.xyz"),))
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



