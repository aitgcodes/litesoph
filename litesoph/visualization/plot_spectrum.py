from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

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

def plot_spectrum(filename, imgfile, row:int, y_column, xlabel:str, ylabel:str, xlimit=(0.0, 30.0), legends:list[str] = []):
    
    # Load the data
    data = np.loadtxt(filename)

    plt.figure(figsize=(8, 6))
    ax = plt.subplot(1, 1, 1)
    y_column = [y_column] if isinstance(y_column, int) else y_column
    while len(legends) < len(y_column):
        legends.append(None)

    for i in range(len(y_column)):
        ax.plot(data[:, row], data[:, y_column[i]], label=legends[i])

    # Styling and labels
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.xlim(xlimit[0], xlimit[1])
    
    # Save and show the plot
    plt.savefig(imgfile)
    plt.show()

def plot_spectrum_octo_polarized(filename, imgfile, row:int, y_column:int, xlabel:str, ylabel:str, xlimit=(0.0, 30.0)):
    """Plots the sum and difference of two columns vs another column, with the option to plot just one column if second_y_column is not provided."""
    
    # Load the data
    data = np.loadtxt(filename)
    
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(1, 1, 1)

    isPolarized = True if data.shape[1] == 9 else False
    
    if isPolarized:
        # Plot the sum and difference if we are plotting both singlet and triplet
        # The Strength Functions are stored at column 7 and 8
        sum_data = data[:, 7] + data[:, 8]
        diff_data = data[:, 7] - data[:, 8]
        ax.plot(data[:, row], sum_data, label='Singlet', color='blue')
        ax.plot(data[:, row], diff_data, label='Triplet', color='red')
    else:
        # Plot only the first column if second_y_column is not provided
        ax.plot(data[:, row], data[:, y_column], label='Singlet', color='k')

    # Styling and labels
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.xlim(xlimit[0], xlimit[1])
    
    # Save and show the plot
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

def contour_plot(x_data, y_data, z_data, x_label:str,y_label:str,title:str,x_lmt_min:float,x_lmt_max:float,y_lmt_min:float,y_lmt_max:float):
    """
    function to plot contour plot
    """    
    import matplotlib.pyplot as plt

    plt.rcParams["figure.figsize"] = (10,8)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)    
    plt.xlim(x_lmt_min,x_lmt_max)
    plt.ylim(y_lmt_min,y_lmt_max)
    plt.contourf(x_data,y_data,z_data)    
    plt.colorbar().set_label('Cross-section', rotation=90)
    return plt.show()

def get_spectrums_delays(task_info,dependent_tasks,project_dir,only_workflow_dirpath):
        """function to generate x,y,z data required by contour plot and plotting contour plot for pump_probe"""
        
        delay_list=[]
        for i in range(len(dependent_tasks)):
            delay=dependent_tasks[i].param.get('delay')   
            delay_list.append(delay) 
            
        spectrum_data_list=[]
        for delay in delay_list:
            spec_file = task_info.output.get(f'spec_delay_{delay}')    
            spec_file= Path(project_dir.parent/only_workflow_dirpath)/spec_file
            spectrum_data_list.append(spec_file)
        return delay_list,spectrum_data_list

def prepare_tas_data(spectrum_data_list,delay_list,contour_x_data_file,contour_y_data_file,contour_z_data_file):        
        
        data0=np.loadtxt(spectrum_data_list[0], comments="#")
        Omega = data0[:,0]
        data=np.zeros(((len(Omega.transpose()),len(spectrum_data_list))))

        for i, dat in enumerate(spectrum_data_list):
            dat=np.loadtxt(dat,comments="#")
            data[:,i] = (dat[:len(Omega),1])
            if i ==0:
                delta_data=data
            else:
                delta_data[:,i]=data[:,i]-data[:,0]
        
        delay_list=[i if i!='no_probe' else 0 for i in delay_list]        
        x_data,y_data= np.meshgrid(delay_list,Omega)
        z_data=(np.abs(data))
                    
        fmt = "%s"# "%20.10e %20.10e %20.10e %20.10e"
        np.savetxt(contour_x_data_file, x_data, fmt=fmt)  
        np.savetxt(contour_y_data_file, y_data, fmt=fmt)  
        np.savetxt(contour_z_data_file, z_data, fmt=fmt)  
