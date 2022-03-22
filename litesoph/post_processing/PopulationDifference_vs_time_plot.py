import sys
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib import cm
import copy


xl=[]
yl=[]
f=open('populations.dat','r')
w=open('write.dat','w')
lines=f.readlines()
print(len(lines))
#for line in lines:
for i in range(len(lines)):
   arr=lines[i].strip().split()  
   xl.append(arr[0])



arr_1 = lines[0].strip().split() 
s = arr_1[0]
arr_2 = lines[len(lines)-1].strip().split()
t = arr_2[0]

d = len(lines)
for j in range(len(arr)-1):
   yl.append(j) 
s = len(arr_1) - 1
 

t = np.asarray(t, dtype='float64')
d = np.asarray(d, dtype='float64')
s = np.asarray(s, dtype='float64')

xlist = np.linspace(0, t, d)
ylist = np.linspace(1, s, s)   

print(len(arr)-1)
print(ylist)
Z=np.zeros((len(lines),len(arr)-1), dtype=float)

X,Y = np.meshgrid(ylist,xlist)

print(X.shape)

arr_first=lines[0].strip().split()[1:]


for ix in range(len(lines)):
    arr=lines[ix].strip().split()[1:]
    for iy in range(len(arr)-1):
#        if iy != 0:
#         continue
#         Z[ix,iy] = arr[iy] 
         Z[ix,iy] = round(float(arr[iy]) - float(arr_first[iy]),9)
#         if float(arr[iy]) == 2.00000:
#            Z[ix,iy] = 999.0
         w.write(str(Z[ix,iy])+" ")
    w.write("\n")
print(Z.shape)
#print(ylist)
print(xlist)
 # a.append([float(s[0]) for s in line.strip().split()])
#print(a)
plt.figure()
#levels = range(0,500,5)
#cp = plt.contourf(X,Y,Z,levels) #,colors='k')
#plt.clabel(cp,colors='k',fmt='%2.1f',fontsize=12)
#cp_filled = plt.contourf(X,Y,Z,levels)
cp_filled = plt.contourf(Y,X,Z,cmap=cm.RdBu,levels = np.linspace(-0.00001,0.00001,1001))
plt.rcParams["contour.negative_linestyle"] = 'solid'
#cp_filled.monochrome = True
plt.colorbar(cp_filled)
plt.title('Populations Difference')
plt.xlabel('Time(hbar/eV)')
plt.ylabel('states')
#plt.ylim(150,200)
#plt.xlim(0,t)
#plt.show()
#fname1 = fnm+".png"
plt.savefig("plot_population.png")
plt.close()
f.close()
w.close()
