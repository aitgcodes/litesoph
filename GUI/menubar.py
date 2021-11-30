from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from tkinter import scrolledtext
#from ttkthemes import ThemedTk
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
#import base64
import os


class VISUAL():

    def __init__(self, tool="None", toolpath="/usr/local/bin"):

        self.vistool={}
        if tool == "None":
           self.vistool["name"]="None"
           self.vistool["exists"]=False
           self.vistool["params"]=""
        else:
           self.vistool["name"]=tool
           self.vistool["exists"]=True

class MainMenu():
    def __init__(self, master):

        menubar = Menu(master)

        file = Menu(menubar, tearoff=0)
        file.add_command(label="New")
        file.add_command(label="Open")
        file.add_command(label="Save")
        file.add_command(label="Save as...")
        file.add_command(label="Close")
        file.add_separator()
        file.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=file)


        edit = Menu(menubar, tearoff=0)
        edit.add_command(label="Undo")
        edit.add_command(label="Cut")
        edit.add_command(label="Copy")
        edit.add_command(label="Paste")
        edit.add_command(label="Delete")
        edit.add_command(label="Select All")
        menubar.add_cascade(label="Edit", menu=edit)

        view = Menu(menubar, tearoff=0)
        view.add_command(label="Graphs")
        view.add_command(label="Images")
        view.add_command(label="Movies")
        view.add_command(label="VMD", command=self.geom_visual)
        view.add_command(label="Avogadro")
        menubar.add_cascade(label="View", menu=view)
        help = Menu(menubar, tearoff=0)
        help.add_command(label="About")
        help.add_command(label="Webpage")
        menubar.add_cascade(label="Help", menu=help)


        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        menubar['font'] = myFont

        master.config(menu=menubar)
        menubar.configure(bg="gainsboro")

    def init_visualization(self):
        visn = VISUAL()
        for tool in ["vmd","VMD","VESTA","vesta"]:
            line=subprocess.run(["which", tool], capture_output=True,text=True).stdout
            chkline = "no {} in".format(tool)
            if not chkline in line:
               visn.vistool["exists"] = True
               visn.vistool["name"] = tool
               break
        self.visn = visn

    #def create_input(self):
    #    InputJob()

    def geom_visual(self):
        self.init_visualization()
        cmd=self.visn.vistool["name"]
        os.system(cmd)




