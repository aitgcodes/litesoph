import numpy as np

def extract_pop_window(data, popl_file, homo_index, below_homo, above_lumo):
        pop_data = []
        homo_index += 1
        for row in data:
            pop = [row[0]]
            pop.extend(row[homo_index - below_homo: homo_index+ above_lumo])
            pop_data.append(pop)
            
        pop_data = np.array(pop_data)
        np.savetxt(popl_file, pop_data)

def get_occ_unocc(data, energy_col=2, occupancy_col=1):
    occ = []
    unocc = []
    
    for row in data:
        if row[occupancy_col] == 2.0 or row[occupancy_col] == 1.0:
            occ.append(row[energy_col])
        elif row[occupancy_col] == 0.0:
            unocc.append(row[energy_col])
        
    return occ, unocc

def get_energy_window(data,energy_file, below_homo, above_lumo):
    
    occ, unocc = get_occ_unocc(data)
    r_occ = occ[-below_homo: ]
    r_unocc = unocc[: above_lumo]
    with open(energy_file, 'w+') as f:
        for item in zip(r_occ, r_unocc):
            f.write("{:.6e}  {:.6e} \n".format(item[0]-occ[-1], item[1]-occ[-1]))

def calc_population_diff(homo_index:int, infile, outfile):
    """ Calculates and writes change in population of KS states from population file"""
    
    data = np.loadtxt(infile)
    time_array = data[:,0]
    for i in range(homo_index):
        data[:,i+1] = data[:,i+1]-2
    np.savetxt(outfile, data)

def create_states_index(num_below_homo:int,num_above_lumo:int, homo_index:int):
    """ Creates the states to index dictionary"""
    
    index_dict = {}
    index_dict[homo_index] = "HOMO"
    index_dict[homo_index+1] = "LUMO"

    for i in range(num_below_homo-1):
        occ_index = homo_index-i-1
        index_dict[occ_index]="HOMO-{}".format(i+1)

    index = 1
    for unocc_index in range(homo_index+2, homo_index+num_above_lumo+1):        
        index_dict[unocc_index]= "LUMO+{}".format(index)
        index +=1
     
    return index_dict