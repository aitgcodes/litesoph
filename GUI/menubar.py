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


class MainMenu():
    def __init__(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=filemenu)
        menubar.add_cascade(label="Templates", menu=filemenu)
        menubar.add_cascade(label="Results", menu=filemenu)
        menubar.add_cascade(label="Tools", menu=filemenu)
        menubar.add_cascade(label="Help", menu=filemenu)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        menubar['font'] = myFont

        master.config(menu=menubar)
        menubar.configure(bg="gainsboro")
