
def plot(fname,image):

    import numpy as np
    import matplotlib.pyplot as plt

    data_ej = np.loadtxt('spec.dat')

    plt.figure(figsize=(8, 6))
    ax = plt.subplot(1, 1, 1)
    ax.plot(data_ej[:, 0], data_ej[:, 1], 'k')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel('Energy (eV)')
    plt.ylabel('Photoabsorption (eV$^{-1}$)')
    plt.xlim(0, 4)
    plt.ylim(ymin=0)
    plt.tight_layout()
    plt.savefig('spec.png')

def plot_spectrum(filename,imgfile,row:int, column:int, xlabel:str, ylabel:str, xlimit=(0.0, 30.0)):  
    """ Shows the plot"""
            
    import numpy as np
    import matplotlib.pyplot as plt
    data_ej = np.loadtxt(filename) 
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(1, 1, 1) 
    ax.plot(data_ej[:, row], data_ej[:, column], 'k')                           
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.xlim(xlimit[0], xlimit[1])
    plt.savefig(imgfile)
    plt.show()      

def plot_multiple_column(data_array, column_list, row_range=(1,1), **kwargs):
    import numpy as np
    import matplotlib.pyplot as plt
    # data = np.loadtxt(filename)
    data = data_array
    time_array = data[:,0]
    row_range = row_range

    if isinstance(column_list, tuple):
        column_beg = column_list[0]
        column_end = column_list[1] 
    xlabel = kwargs.get('xlabel', 'Time (in as)')
    ylabel = kwargs.get('ylabel', 'Change in population')
    xlimit = kwargs.get('xlimit', None)
    column_dict = kwargs.get('column_dict', {1:"HOMO-2", 2:"HOMO-1", 3:"HOMO"})

    plt.figure(figsize=(8, 6))
    for i in range(column_beg, column_end+1):
        legend = column_dict.get(i)
        plt.plot(data[:,0], data[:,i], label=legend)
        plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if xlimit:
        plt.xlim(xlimit[0], xlimit[1])
    plt.show()  
