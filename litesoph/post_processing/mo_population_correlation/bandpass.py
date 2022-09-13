import re
import sys
import numpy as np

fname=sys.argv[1]
frame=float(sys.argv[2])

eps=1/10**6

fp=open(fname,"r")
lines=fp.readlines()
fp.close()

nt = len(lines)
#print (nt)
ncol=len(lines[0].strip().split())
#print (ncol)
fn = np.zeros((nt,ncol-1),dtype=float)
fp=open("time.dat","w")
for i in range(nt):
   t = np.zeros(nt,dtype=float)
   fp.write("%10.2f" %(t[i]))
   fp.write("\n") 
fp.close()

#print (t)


it = 0
for line in lines:
    arr=line.strip().split()
    t[it] = float(arr[0])
    for icol in range(1,ncol):
        fn[it,icol-1] = float(arr[icol])
    it += 1
    
dt = t[1]-t[0]

npad = int(frame/dt)
nex = nt+2*npad
fnex = np.zeros((nex,ncol-1),dtype=float)
fav = np.zeros((nex,ncol-1),dtype=float)
frest = np.zeros((nex,ncol-1),dtype=float)

for icol in range(ncol-1):
    fdc = 0
    for it in range(nt):
        fdc += fn[it,icol]
    fdc = fdc/nt
    fnex[:,icol] = fdc
    fav[:,icol] = fdc

i=0
for it in range(npad,nt+npad):
    fnex[it,:] = fn[i,:]
    i += 1


nwin = int(frame/dt/2)
for it in range(npad,nt+npad):
    for icol in range(ncol-1):
        fnav = 0.0
        for i in range(it-nwin,it+nwin):
            fnav += fnex[i,icol]
        fnav = fnav/2/nwin
        fav[it,icol] = fnav

fp1=open("fav.dat","w")
fp=open("frest.dat","w")
tbeg = t[0]-nwin*dt
for it in range(nex):
    frest[it,:] = fnex[it,:]-fav[it,:]
    
    fp.write("{:.16e}       ".format(tbeg+it*dt))
    fp1.write("{:.16e}      ".format(tbeg+it*dt))
    for icol in range(ncol-1):
        fp.write("{:.16e}       ".format(frest[it,icol]))
        fp1.write("{:.16e}      ".format(fav[it,icol]))
    fp.write("\n")
    fp1.write("\n")
fp.close()
fp1.close()

