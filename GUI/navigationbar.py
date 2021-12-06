import os
from tkinter import filedialog as fd
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import ctypes

class NavigationMenu():
    def is_hidden(filepath):
       name = os.path.basename(os.path.abspath(filepath))
       return name.startswith('.') or has_hidden_attribute(filepath)

    def has_hidden_attribute(filepath):
       try:
          attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
          assert attrs != -1
          result = bool(attrs & 2)
       except (AttributeError, AssertionError):
          result = False
       return result

root=tk.Tk()
root.geometry('320x240')
f=tk.Frame(root)
tv=ttk.Treeview(f,show='tree')
ybar=tk.Scrollbar(f,orient=tk.VERTICAL,
                  command=tv.yview)
tv.configure(yscroll=ybar.set)
directory = str(Path.home())
tv.heading('#0',text='Dir：'+directory,anchor='w')
path=os.path.abspath(directory)
node=tv.insert('','end',text=path,open=True)
def traverse_dir(parent,path):
        for d in os.listdir(path):
            full_path=os.path.join(path,d)
            isdir = os.path.isdir(full_path)
            isfile = os.path.isfile(full_path)
        if isfile and not is_hidden(full_path):
          id=tv.insert(parent,'end',text=d,open=False)
        if isdir and not is_hidden(full_path):
          id=tv.insert(parent,'end',text=d,open=False)
          traverse_dir(id,full_path)
          traverse_dir(node,path)
          ybar.pack(side=tk.RIGHT,fill=tk.Y)
          tv.pack()
          f.pack()
root.mainloop()
