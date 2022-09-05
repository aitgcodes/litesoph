import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import *
import pandas as pd
import numpy as np
import subprocess
import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
from scipy.signal import hilbert


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


def read_dmpulse_dat_file(data):

    df = pd.read_table(data, sep="\s+")
    
    autofs = 0.02418906
    df.time *=autofs
    
    df['dm_umx'] = df['dmx'] - df['dmx1']
    df['dm_umy'] = df['dmy'] - df['dmy1']
    df['dm_umz'] = df['dmz'] - df['dmz1']

    return df

# def plot_dipole_moment(data):

#     df=read_dmpulse_dat_file(data)
    
#     autofs = 0.02418906
#     df.time *=autofs
    
#     x = df["time"]
#     y1 = df["dmx"]
#     lns2 = plt.plot(x,y1,'r-',linewidth=2.5)
#     plt.ylabel('y axis label')
#     plt.xlabel('x axis label')
#     plt.title('Graph 1')
#     plt.draw()
#     plt.show()

def plot_dipole_moment(data):
    
    df=read_dmpulse_dat_file(data)
    
    
    t=df['time'] 

    plt.subplot(3, 3, 1)
    plt.plot(t,df['dmx'])
    plt.title("dmx vs t")

    plt.subplot(3, 3, 2)
    plt.plot(t,df['dmy'])
    plt.title("dmy vs t")

    plt.subplot(3, 3, 3)
    plt.plot(t,df['dmz'])
    plt.title("dmz vs t")
    
    plt.subplot(3, 3, 4)
    plt.plot(t,df['dmx1'])
    plt.title("dmx1 vs t")
    
    plt.subplot(3, 3, 5)
    plt.plot(t,df['dmy1'])
    plt.title("dmy1 vs t")
    
    plt.subplot(3, 3, 6)
    plt.plot(t,df['dmz1'])
    plt.title("dmz1 vs t")

    plt.subplot(3, 3, 7)
    plt.plot(t,df['dm_umx'])
    plt.title("dm_umx vs t")
    
    plt.subplot(3, 3, 8)
    plt.plot(t,df['dm_umy'])
    plt.title("dm_umy vs t")
    
    plt.subplot(3, 3, 9)
    plt.plot(t,df['dm_umz'])
    plt.title("dm_umz vs t")

    # plt.subplot_tool()
    plt.suptitle("Dipole Moment Pulse")

    plt.show()


def energy_transfer_coupling():


    def show_entry_fields():
        length = float(e1.get())
        area=  (6.023*10**(-34))/((length*(10**(-15)))*(1.6*10**(-19)))                                      
        result_label['text'] = str(area)+'eV'

    master = Toplevel(root)
    master.geometry("350x150")

    Label(master, text="time period in fs").grid(row=0)
    e1 = Entry(master)
    e1.grid(row=0, column=1)

    area_label = Label(master, text="Energy coupling constant :")
    area_label.grid(row=2)

    result_label = Label(master, text="")
    result_label.grid(row=2,column=1)

    Button(master, text='Quit', command=master.quit).grid(row=3, column=0, sticky=W, pady=4)
    Button(master, text='Show', command=show_entry_fields).grid(row=3, column=1, sticky=W, pady=4)

    master.mainloop()

   
def plot_hilbert_transform(data):
    
    df_hil=pd.read_table(data, sep="\s+")
    signal= df_hil['dmx']
    t=df_hil['time']
    
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)
    
    plt.plot(t,signal,linewidth=0.5,label='signal')
    plt.plot(t,amplitude_envelope,linewidth=1.5,label='envelope')    
    plt.ylabel('Dipole Moment')
    plt.xlabel('Time ')
    plt.title('Dipole moment oscillations')
    plt.legend()
    plt.draw()
    plt.show()

    
    
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

def hilbert_button():
    plot_hilbert_transform(v.get())






root = tk.Tk()
root.geometry("600x300")

tk.Label(root, text='File Path').grid(row=0, column=0)
v = tk.StringVar()
entry = tk.Entry(root, textvariable=v).grid(row=0, column=1)
tk.Button(root, text='Browse Data Set',command=import_csv_data).grid(row=1, column=0)
tk.Button(root, text='Close',command=root.destroy).grid(row=1, column=1)

tk.Button(root, text='sample plot', command=graph_1).grid(row=3, column=0) # Call the graph_1 function
tk.Button(root, text='dmpulse', command=dmpulse).grid(row=3, column=1)
tk.Button(root, text='hilbert', command=hilbert_button).grid(row=3, column=2)
tk.Button(root, text='energy_transfer_coupling', command=energy_transfer_coupling).grid(row=3, column=3)


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