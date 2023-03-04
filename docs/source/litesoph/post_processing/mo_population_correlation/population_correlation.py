import numpy as np
import itertools as it
import os
import sys

n_occ = int(sys.argv[1])                                     # Number of occupied orbitals
coeff_file = np.loadtxt("outfile.txt",dtype="float64")                    # Reading coefficients from file
coeff_file_data = coeff_file[:,1:]                      # Removing the first column (frequency column)
n_unocc = coeff_file_data.shape[1]-n_occ                # Number of unoccupied orbitals
occ_indx = np.arange(n_occ)                             # list of columns containing occupied orbitals
unocc_indx = np.arange(n_occ,coeff_file_data.shape[1])  # list of columns containing occupied orbitals
combinations = list(it.product(occ_indx,unocc_indx))          # combinations of all the column indices for occupied and unoccupied orbitals

amp = []                                                # Final list containing the amplitudes
for combo in combinations:
    value = np.sum(coeff_file_data[:,combo[0]]*coeff_file_data[:,combo[1]])
    
    amp.append(np.sum(coeff_file_data[:,combo[0]]*coeff_file_data[:,combo[1]]))

amp_data = np.array(amp)
print(amp_data.shape)
print(max(amp_data))
amp_data_norm = amp_data/max(amp_data)
print(len(amp_data))


occ_en = []
unocc_en = []
ef = open(sys.argv[2],"r")                                  # energy file
for line in ef:
    l_data = np.array(line.rsplit(),dtype="float64")
    if len(l_data) == 2:
        occ_en.append(l_data[0])
        unocc_en.append(l_data[1])
    else:
        unocc_en.append(l_data[0])
ef.close()
combo2 = list(it.product(occ_en,unocc_en))
first_col = [i[0] for i in combo2]
second_col = [i[1] for i in combo2]
print(first_col)
print(second_col)

amp_file = open("amp_file.dat","w")
for i in range(len(amp_data)):
    amp_file.write("{: .16e}    {: .16e}    {: .16e}    {: .16e}\n".format(first_col[i],second_col[i],amp_data[i],amp_data_norm[i]))
amp_file.close()
