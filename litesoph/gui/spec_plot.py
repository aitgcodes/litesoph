# web-page: spec.png
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

def plot_spectra(axis, filename, imgfile, x, y, conversion=None):
    data_ej = np.loadtxt(filename)    
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(1, 1, 1)
    if conversion is not None:
        ax.plot(data_ej[:, 0]*conversion, data_ej[:, axis], 'k')
    else:
       ax.plot(data_ej[:, 0], data_ej[:, axis], 'k')          
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel(x)
    plt.ylabel(y)
    # plt.xlabel('Energy (eV)')
    # plt.ylabel('Photoabsorption (eV$^{-1}$)')
    #plt.xlim(0, 4)
    #plt.ylim(ymin=0)
    plt.tight_layout()
    plt.savefig(imgfile)
    plt.show()


def plot_files(file1, file2, axis1, axis2):
    from litesoph.utilities.units import au_to_fs
    array1 = np.loadtxt(file1)
    array2 = np.loadtxt(file2)
    fig, ax = plt.subplots()
    ax.plot(array1[:, 0]*au_to_fs, array1[:, axis1], color = 'red', label='Laser Pulse')
    ax1= ax.twinx()
    ax1.plot(array2[:, 0]*au_to_fs, array2[:, axis2], color= 'green', label='Dipole Moment')
    ax.legend(loc = 'upper left')
    ax1.legend(loc = 'upper right')
    ax.set(xlabel='Time(in fs)', ylabel='Laser Pulse(in au)')    
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax1.set(ylabel = 'Dipole Moment in au)')
    ax1.yaxis.set_ticks_position('right')
    plt.show()