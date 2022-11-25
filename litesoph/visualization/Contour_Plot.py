from copy import copy
from ctypes import sizeof
from signal import signal
from tkinter import W
from turtle import shape
import numpy as np
import numpy.ma as ma
import scipy as sp
from matplotlib import pyplot as plt 
import os
import argparse

import matplotlib.colors as mcolors


# project_path='/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/octopus/td.general_laser_td{:d}/cross_section_vector'
# data_path=[
#     '/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/octopus/td.general_laser_td0/cross_section_vector'
# ]
# data0=
data0 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td0_add/cross_section_vector', skiprows=17)
data2 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td2_add/cross_section_vector', skiprows=17)
data4 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td4_add/cross_section_vector', skiprows=17)
data6 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td6_add/cross_section_vector', skiprows=17)
data8 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td8_add/cross_section_vector', skiprows=17)
data10 = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td10_add/cross_section_vector', skiprows=17)
Omega = data0 [:,0]
delay= [0,2,4,6,8,10] 
data_list = [data0, data2, data4, data6, data8, data10]


data=np.zeros(((len(Omega.transpose()),len(data_list))))


for i, dat in enumerate(data_list):

    # data[:,i] = np.abs(dat[:len(Omega),4])
    data[:,i] = (dat[:len(Omega),4])
    # data=np.abs(data)
    if i ==0:
        delta_data=data
    else:
        delta_data[:,i]=data[:,i]-data[:,0]

# np.savetxt('Amp_data.txt', data, delimiter="            ", fmt="%s")

X,Y= np.meshgrid(delay,Omega)  #Grid

Z=(np.abs(data))
# Z=data
# Z=delta_data

# freq_lim=np.max(Omega)
freq_lim=10

# from matplotlib.cm import ScalarMappable
# from numpy import ma
# from matplotlib import ticker, cm
from matplotlib.colors import BoundaryNorm, ListedColormap
# import matplotlib
# from matplotlib.colors import LogNorm
from matplotlib import *

# Z = ma.masked_where(Z <= 0, Z)
plt.figure()
# levels = np.linspace(Z.min(), Z.max(), 10)


# cmap = ListedColormap(["Red", "darkred", "crimson", "salmon", "navy", "violet", "yellow"])
# bounds = [0,1000,2000,3000,4000,5000,6000,7000,8000]
# cmap_rb = plt.get_cmap('RdBu_r')
# colours = cmap_rb(np.linspace(0, 1, len(bounds) - 1))
# cmap, norm = mcolors.from_levels_and_colors(bounds, colours)
# norm = BoundaryNorm(bounds, cmap.N)

# plt.contourf(X,Y,Z, levels=levels, extend="both",cmap=cmap, norm=norm)

plt.contourf(X,Y,Z)



plt.ylim(0,freq_lim)
# plt.zlim(0,np.max(Z))
plt.xlabel('Delay Time (femtosecond)')
plt.ylabel('Frequency (eV)')
plt.colorbar().set_label('Cross-section', rotation=270)
# plt.colorbar(ScalarMappable(),ticks=range(0,1600 )).set_label('Amplitude', rotation=270)

plt.show()