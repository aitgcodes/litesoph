from pathlib import Path
from tkinter import messagebox

def create_path(projpath,projname):
    path = Path(projpath)

    newpath = path / str(projname)

    try:
        newpath.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        messagebox.showinfo("Message", f"project:{newpath} already exists")
    else:
        messagebox.showinfo("Message", f"project:{newpath} is created successfully")














