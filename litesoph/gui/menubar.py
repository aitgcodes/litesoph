from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.     
from tkinter import messagebox
from tkinter import scrolledtext
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
import os


class MainMenu(tk.Menu):
    """The Application's main menu"""

    def _event(self, sequence):
        def callback(*_):
            root = self.master.winfo_toplevel()
            root.event_generate(sequence)
        return callback

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


        file_menu = Menu(self, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save as...")
        file_menu.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="file")


        edit = Menu(self, tearoff=0)
        edit.add_command(label="Undo")
        edit.add_command(label="Cut")
        edit.add_command(label="Copy")
        edit.add_command(label="Paste")
        edit.add_command(label="Delete")
        edit.add_command(label="Select All")
        edit.add_cascade(label="Edit")

        view = Menu(self, tearoff=0)
        view.add_command(label="file")
        view.add_command(label="Graphs")
        view.add_command(label="Images")
        view.add_command(label="Movies")
        view.add_command(label="VMD")
        view.add_command(label="Vesta")
        self.add_cascade(label="View", menu=view)
        
        help = Menu(self, tearoff=0)
        help.add_command(label="About")
        help.add_command(label="Webpage")
        self.add_cascade(label="Help", menu=help)


        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self['font'] = myFont

        parent.config(menu=self)
        self.configure(bg="gainsboro")

    
    
        

