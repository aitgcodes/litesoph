''' A small test code to parallely read and compute  Psi_a*Psi_i which are in cube format.
This small test code reads few occupied and unoccupied states in the present directory and computes Psi_a*Psi_i. Occupied and unoccupied pairs are parallelised here. They are alloted cores in a roundrobin fasion.
'''
import sys
import numpy as np
import copy
from mpi4py import MPI
import time
import itertools
from cubehandler import cubeio 
import os
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Start_time",current_time)


a = []
b = []
o_range_down = int(sys.argv[1])
o_range_up = int(sys.argv[2])

u_range_down = int(sys.argv[3])
u_range_up = int(sys.argv[4])

wmin = float(sys.argv[5])
wmax = float(sys.argv[6])

fpref = sys.argv[7]

[a.append(i) for i in range(o_range_down,o_range_up+1)]
[b.append(j) for j in range(u_range_down,u_range_up+1)]
total_proc = size          # number of cores
print(a,b)
npx = 201           # number of vortex elements in x direction in the cube file
npy = 201             # number of vortex elements in x direction in the cube file
npz = 287             # number of vortex elements in x direction in the cube file
n_x = len(a)
n_y = len(b)
pairs = int(n_x*n_y) # number of total states
allot = int(pairs/total_proc) # number of round robin rounds required
chunk = int(pairs/size) 
if pairs > total_proc &  pairs%size != 0:
 allot += 1

mycube = cubeio(True)     # initializing class cubeio of cubehandler.py with angstrom units = true


oulist = []
oulist_loc = []
ent  = rank

def read_dmat(fp):                 # Function to read the dmat file

       lines=fp.readlines()
       arr1 = lines[0].strip().split()
       nt = int(arr1[0])
       nocc = int(arr1[1])
       nx = int(arr1[2])
       ny = int(arr1[3])

       t=[]
       dmat=np.zeros((nt,nx,ny), dtype=float)
       eocc=[]
       euocc=[]

       arr1=lines[1].strip().split()
       ehomo = float(arr1[nx-1])

       for ix in range(nx):
        ediff = float(arr1[ix])-ehomo
        eocc.append(ediff)


       arr1=lines[2].strip().split()
       for ix in range(ny):
        euocc.append(float(arr1[ix])-ehomo)

       it = 0
       for line in lines[3:]:
          arr1 = line.strip().split()
          t.append(float(arr1[0]))
          ik = 1
          for ix in range(nx):
                 for iy in range(ny):
                      dmat[it,ix,iy] = copy.copy(float(arr1[ik]))
                      ik += 1
          it += 1

       return (t, dmat, nocc, eocc, euocc)

wf_occ = []
wf_unocc = []

for i in range(500):
    wf_occ.append(i) 
    wf_unocc.append(i)  

for io in a:
    ax_o = fpref+"/"+"wf-st"+format(io,"04")+".cube"
    fp_o = open(ax_o,"r")
    wf_o = mycube.readcube(fp_o)
    print("Reading"+ax_o)
    fp_o.close()
    wf_occ.insert(io, wf_o)
for iu in b: 
    ax_u = fpref+"/"+"wf-st"+format(iu,"04")+".cube"
    fp_u = open(ax_u,"r")
    wf_u = mycube.readcube(fp_u)
    print("Reading"+ax_u)
    fp_u.close()
    wf_unocc.insert(iu, wf_u)



'''
def ks_reading(io,iu):                                #     function to read cube files of the occupied unoccupied states using cube handler file
    print('ks_reading_entered')
    ax_o = fpref+"/"+"wf-st"+format(io,"04")+".cube"
    fp_o  = open(ax_o,"r")
    wf_o  = mycube.readcube(fp_o)
    print("Reading"+ax_o)
    fp_o.close()  
    ax_u = fpref+"/"+"wf-st"+format(iu,"04")+".cube"
    fp_u  = open(ax_u,"r")
    wf_u  = mycube.readcube(fp_u)
    print("Reading"+ax_u)
    fp_u.close() 
    return (wf_o,wf_u) 
'''

def cal_chden(den,wfo,wfu,nx,ny,nz):                     # Function to compute the Psi_a*Psi_i
   
    chd = np.zeros((nx,ny,nz), dtype = float)
    ik = 0
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):

                chd[ix,iy,iz] = wfo[ik]*den*wfu[ik]
                ik += 1
    return chd

def div_chunk(oulist, chunk):
      
    # looping till length l
    for i in range(0, len(oulist), chunk): 
        yield oulist[i:i + chunk]
 


fp=open("dmat.dat","r")
(w, dmat, nocc, eo, eu) = read_dmat(fp)
fp.close()

nw = len(w)
widx = []
for it in range(nw):
    if w[it] >= wmin and w[it] <= wmax:
        widx.append(it)
sum_loc = np.zeros((npx,npy,npz), dtype=float)

oulist = list(itertools.product(a,b))         # initialising electron hole pair as list of tuples

psio = []
psiu = []

#print("oulist")
#print(oulist)
oulist_loc = list(div_chunk(oulist,chunk))
#print("oulist_loc")
#print(oulist_loc[rank])
#print(rank)

for it in widx:

  print("entered it")
  for i in range(size):
    if i == rank:
     print("Entered if rank") 
     for (io,iu) in oulist_loc[rank]:
 #      (psio,psiu) = ks_reading(io,iu)                    # parallelised reading of required electron hole pairs 
       sum_loc += cal_chden(dmat[it,io,iu-nocc],wf_occ[io],wf_unocc[iu],npx,npy,npz)        # Parallelised calculation of Psi_a*Psi_i

  v_sum = np.zeros((npx,npy,npz), dtype=float)
  total_sum = np.zeros((npx,npy,npz), dtype=float)

  for i in range(size-1):
    if rank == i:
         comm.send(sum_loc,dest = size - 1)
  if rank == size-1:
      for i in range(size-1):
         v_sum = comm.recv(source=i)
         total_sum += v_sum
      f1 = "chden_parallel"+str(w[it])
      fn = mycube.writecube(f1,total_sum)
      print(fn)

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("End_time",current_time)
