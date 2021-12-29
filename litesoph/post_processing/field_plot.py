#This code slices  cube files in the xz plane
#usage python3 .py  .cube - - - 86 // where 86 is the distance in the y-axis to be sliced divided by the y vector as specified in the cube file
#Caution should be taken to take care of units used in cube files.

import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np


fname=sys.argv[1]                # Getting input cube file
x_integ_length=sys.argv[2]       # Getting the input(Should be in Angstrom) for integ in x_axis
y_integ_length=sys.argv[3]       # Getting the input(Should be in Angstrom) for integ in y_axis
z_integ_length=sys.argv[4]       # Getting the input(Should be in Angstrom) for integ in z_axis
y_cut = sys.argv[5]

fp=open(fname,'r')            #Opening the input cube file
lines=fp.readlines()          #Reading all the lines of the input cube file
nat = 0.000                   # Initializing number of atoms to 0.000
a = []
for line in lines[2:6]:       #Reading Headers
    for s in line.strip().split():
        a.append(s)
#        print(a)

nat=a[0]                      # Number of atoms
xvortex=a[4]                  # Number of Vortex in x direction
yvortex=a[8]                  # Number of Vortex in y direction
zvortex=a[12]                 # Number of Vortex in z direction
xvec=a[5]                     # x vector
yvec=a[10]                    # y vector
zvec=a[15]                    # z vector
###Done_Reading_Headers

vol=float(xvec)*float(yvec)*float(zvec)            # Volume of the vortex
npoints=int(xvortex)*int(yvortex)*int(zvortex)     # Total number of vortex

data=np.zeros(npoints,dtype=float)                    # Initializing


if x_integ_length=="-":
   x_plane=xvortex
else:
   x_plane=float(x_integ_length)/float(xvec)

if y_integ_length=="-":
   y_plane=yvortex
else:
   y_plane=float(y_integ_length)/float(yvec)
   

if z_integ_length=="-":
   z_plane=zvortex
else:
   z_plane=float(z_integ_length)/float(zvec)  


ipt = 0
big_line = int(nat) + 6
#print(big_line)
for line in lines[big_line:]:

     arr=line.strip().split()
     npt=len(arr)
     for i in range(npt):
            data[ipt] = float(arr[i])
            ipt += 1
ipt=0


npt=np.zeros((int(xvortex),int(yvortex),int(zvortex)),dtype=int)

for x in range(int(xvortex)):              
     for y in range(int(yvortex)):
          for z in range(int(zvortex)):
                npt[x,y,z] = ipt
                ipt +=1

sumdat = 0.0


Yl=np.zeros((int(xvortex),int(zvortex)), dtype=float)

for x in range(int(x_plane)):              
   for y in range(int(y_plane)):
        for z in range(int(z_plane)):
             if y == int(y_cut):
                print("lalalal")
                Yl[x,z]=data[npt[x,y,z]]
                

sumdat = sumdat*vol
print(sumdat)
print(xvortex)
print(yvortex)
xlist=np.linspace(0,int(xvortex),int(xvortex))
zlist=np.linspace(0,int(zvortex),int(zvortex))
Xl,Zl = np.meshgrid(zlist,xlist)

print(Xl,Zl)
print(Yl)

plt.figure()
cp_filled = plt.contourf(Xl,Zl,Yl,40)
#cp_filled = plt.contourf(Xl,Zl,Yl,cmap=cm.viridis,levels=np.linspace(2.0,5.0,5000))
plt.rcParams["contour.negative_linestyle"] = 'solid'
plt.colorbar(cp_filled)
plt.title('Field Enhancement')
plt.xlabel('z')
plt.ylabel('x')
#plt.xlim(0,zvortex)
#plt.ylim(0,xvortex)
plt.savefig("fig.png")
plt.close()
fp.close()
