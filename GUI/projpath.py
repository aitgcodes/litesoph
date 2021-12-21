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
        messagebox.showinfo("Message", f"project:{newpath} already exists, please open the existing project")
    else:
        messagebox.showinfo("Message", f"project:{newpath} is created successfully")

def dir_exist(projpath,projname):
    
    path = Path(projpath) / str(projname)
    
        
    if  os.path.isdir(path):
        messagebox.showinfo("Message", f"You are in Project:{path}")
    else:
        messagebox.showinfo("Message", f"project:{path} doesnot exists, please create")

def create_folder(path, dir_name):
    path = Path(path)
    newpath = path / str(dir_name)
    try:
        newpath.mkdir(parents=True, exist_ok=False)
        return newpath
    except FileExistsError:
        print("Folder already exists.")
        return newpath












