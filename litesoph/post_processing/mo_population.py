import numpy as np

def extract_pop_window(data, popl_file, homo_index, below_homo, above_lumo):
        pop_data = []
        homo_index += 1
        for row in data:
            pop = [row[0]]
            pop.extend(row[homo_index - below_homo: homo_index+ above_lumo])
            pop_data.append(pop)
            
        pop_data = np.array(pop_data)
        print(pop_data.shape)
        np.savetxt(popl_file, pop_data)

def get_occ_unocc(data):
    occ = []
    unocc = []
    
    for row in data:
        if row[1] == 2.0 or row[1] == 1.0:
            occ.append(row[2])
        elif row[1] == 0.0:
            unocc.append(row[2])
        
    return occ, unocc

def get_energy_window(data,energy_file, below_homo, above_lumo):
    
    occ, unocc = get_occ_unocc(data)
    r_occ = occ[-below_homo: ]
    r_unocc = unocc[: above_lumo]
    with open(energy_file, 'w+') as f:
        for item in zip(r_occ, r_unocc):
            f.write("{:.6e}  {:.6e} \n".format(item[0]-occ[-1], item[1]-occ[-1]))