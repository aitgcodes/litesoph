from pathlib import Path
from tkinter import messagebox
import os.path
from os import path
def create_path(projpath,projname):
    path = Path(projpath)

    newpath = path / str(projname)

    try:
        newpath.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        messagebox.showinfo("Message", f"project:{newpath} already exists, please select option 'Go'")
    else:
        messagebox.showinfo("Message", f"project:{newpath} is created successfully")

def dir_exist(projpath,projname):
    #path = Path(projpath)
    path = Path(projpath) / str(projname)
    
        #isExist = os.path.exists(path)
    if  os.path.isdir(path):
        messagebox.showinfo("Message", f"You are in Project:{path}")
    else:
        messagebox.showinfo("Message", f"project:{path} doesnot exists, please create")













