from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from tkinter import scrolledtext
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
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
        view.add_command(label="Files", command=self.text_view)
        view.add_command(label="Graphs")
        view.add_command(label="Images")
        view.add_command(label="Movies")
        view.add_command(label="VMD", command=self.geom_visual)
        view.add_command(label="Vesta")
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
        for tool in ["vmd","VMD"]:
            line=subprocess.run(["which", tool], capture_output=True,text=True).stdout
            chkline = "no {} in".format(tool)
            if not chkline in line:
               visn.vistool["exists"] = True
               visn.vistool["name"] = tool
               break
        self.visn = visn



    def geom_visual(self):
        self.init_visualization()
        cmd=self.visn.vistool["name"]
        os.system(cmd)

    def text_view(self):

        top1 = Toplevel()
        top1.geometry("600x450")
        top1.title("LITESOPH Text Editor")

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        text_scroll =Scrollbar(top1)
        text_scroll.pack(side=RIGHT, fill=Y)
        
        
        my_Text = Text(top1, width = 80, height = 25, yscrollcommand= text_scroll.set)
        #my_Text = Text(top1, width = 80, height = 25)
        my_Text['font'] = myFont
        my_Text.place(x=15,y=10)
        text_scroll.config(command= my_Text.yview)

        view = tk.Button(top1, text="View Text",bg='blue',fg='white',command=lambda:[self.open_txt(my_Text)])
        view['font'] = myFont
        view.place(x=120,y=400)

        save = tk.Button(top1, text="Save", bg= 'blue',fg='white',command=lambda:[self.save_txt(my_Text)])
        save['font'] = myFont
        save.place(x=280, y=400)
        
        close = tk.Button(top1, text="Close", bg= 'blue',fg='white',command=top1.destroy)
        close['font'] = myFont
        close.place(x=420, y=400)
        

    def open_txt(self,my_Text):
        text_file_name = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=(("Text files","*"),))
        #text_file_name = open_file(user_path) 
        self.current_file = text_file_name
        text_file = open(text_file_name, 'r')
        stuff = text_file.read()
        my_Text.insert(END,stuff)
        text_file.close()
    
    def save_txt(self,my_Text):
        text_file = self.current_file
        text_file = open(text_file,'w')
        text_file.write(my_Text.get(1.0, END))
        

    
        

