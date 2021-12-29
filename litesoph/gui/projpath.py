from pathlib import Path
from tkinter import messagebox
import os


def create_folder(path, dir_name):
    path = Path(path)
    newpath = path / str(dir_name)
    try:
        newpath.mkdir(parents=True, exist_ok=False)
        return newpath
    except FileExistsError:
        #print("Folder already exists.")
        return newpath












