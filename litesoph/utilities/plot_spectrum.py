
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
    xcolumn = kwargs.get('xcolumn',0)
    xlimit = kwargs.get('xlimit', None)
    column_dict = kwargs.get('column_dict', {1:"HOMO-2", 2:"HOMO-1", 3:"HOMO"})

    plt.figure(figsize=(8, 6))
    for i in reversed(range(column_beg, column_end+1)):
        legend = column_dict.get(i)
        plt.plot(data[:,xcolumn], data[:,i], label=legend)
        plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if xlimit:
        plt.xlim(xlimit[0], xlimit[1])
    plt.show()  

def plot_population_tracking(population_file, homo_index:int,**kwargs):
    """ Arguments: homo_index= column number corresopnding to homo
                   num_occupied_mo_plot,num_unoccupied_mo_plot,time_unit
    """
    import numpy as np
    from litesoph.post_processing.mo_population import create_states_index
    from litesoph.utilities.units import au_to_as,au_to_fs

    population_data = np.loadtxt(population_file)
    (total_rows, total_columns) = population_data.shape
    default_above_lumo = total_columns-homo_index-1
    default_below_homo = homo_index

    below_homo_value = kwargs.get('num_occupied_mo_plot', default_below_homo)
    above_lumo_value = kwargs.get('num_unoccupied_mo_plot', default_above_lumo)

    # Upper limit on (un/)occupied states
    below_homo = min(below_homo_value, default_below_homo)
    above_lumo = min(above_lumo_value, default_above_lumo)
    
    time_unit = kwargs.get('time_unit', 'atomic')            
    column_range = (homo_index-below_homo+1,homo_index+above_lumo)
    legend_dict = create_states_index(num_below_homo=below_homo, num_above_lumo=above_lumo, homo_index=homo_index)

    if time_unit == 'h_cut/eV':
        population_data[:,0]= population_data[:,0]*27.12*au_to_fs

    plot_multiple_column(population_data, column_list=column_range, column_dict=legend_dict, xcolumn=0, xlabel='Time (in femtosecond)', ylabel='Change in population')
