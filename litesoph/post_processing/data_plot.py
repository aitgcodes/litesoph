#import Tkinter as tk
#from tkFileDialog import askopenfilename
#from Tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import *
import pandas as pd
import numpy as np
import subprocess
import webbrowser
import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def display_graph(data):
    df = pd.read_csv(data)

    x = df["X Data"]
    y1 = df["Y1 Data"]
    y2 = df["Y2 Data"]
    z = df["Y3 Data"]
    y_pos = np.arange(len(x))

    lns1 = plt.bar(y_pos,z)
    plt.ylabel('Bar Graph')
    plt.xlabel('Date')

    plt.twinx()
    lns2 = plt.plot(y_pos,y1,'r-',linewidth=2.5)
    lns3 = plt.plot(y_pos,y2,color='orange',linewidth=2.5)
    plt.ylabel('Line Data')
    plt.xticks(y_pos, x)
    plt.xlabel('X axis')
    plt.title('Graph 1')

    plt.legend([lns1, lns2[0], lns3[0]],["Bar", "Line 1", "Line 2"], loc="upper right")

    plt.draw()
    plt.show()


def plot_dipole_moment(data):
    df = pd.read_table(data, sep="\s+")
    
    autofs = 0.02418906
    df.time *=autofs
    
    x = df["time"]
    y1 = df["dmx"]
    lns2 = plt.plot(x,y1,'r-',linewidth=2.5)
    plt.ylabel('Line Data')
    plt.xlabel('X axis')
    plt.title('Graph 1')
    plt.draw()
    plt.show()

def plot_energy_transfer_coupling():
    pass

def plot_hibert_transform():
    pass


def import_csv_data():
    global v
    csv_file_path = askopenfilename()
    print(csv_file_path)
    v.set(csv_file_path)
    df = pd.read_csv(csv_file_path)

# Define the functions before calling them
def doNothing():
    print("nothing")

def create_window():
    window = tk.Tk() 


def graph_1():
    display_graph(v.get())

def dmpulse():
    plot_dipole_moment(v.get())


root = tk.Tk()
tk.Label(root, text='File Path').grid(row=0, column=0)
v = tk.StringVar()
entry = tk.Entry(root, textvariable=v).grid(row=0, column=1)
tk.Button(root, text='Browse Data Set',command=import_csv_data).grid(row=1, column=0)
tk.Button(root, text='Close',command=root.destroy).grid(row=1, column=1)

tk.Button(root, text='Graph 1', command=graph_1).grid(row=3, column=0) # Call the graph_1 function
tk.Button(root, text='dmpulse', command=dmpulse).grid(row=3, column=1)
tk.Button(root, text='Graph 3', command=doNothing).grid(row=3, column=2)
tk.Button(root, text='Graph 4', command=doNothing).grid(row=3, column=3)


menu =  Menu(root)
root.config(menu=menu)
subMenu = Menu(menu)
menu.add_cascade(label="File",menu=subMenu)
subMenu.add_command(label="New", command=create_window)
subMenu.add_command(label="Open", command=doNothing)
subMenu.add_command(label="Restart", command=doNothing)
subMenu.add_command(label="Exit", command=doNothing)
editMenu = Menu(menu)
menu.add_cascade(label = "Help", menu=editMenu)
editMenu.add_command(label="Help", command=doNothing)

root.mainloop()