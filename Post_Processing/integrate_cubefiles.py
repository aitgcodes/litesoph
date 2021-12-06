#This code integrates cube files upto a bounadary specified along the x , y, and z axes respectively

#usage python3 .py  .cube - - -  // integrates whole cube

#usage python3 .py .cube - 10 20 // integrates upto 10 angstrom in y axis and 20 angstrom in z axis

# Caution should be taken to take care of units used in cube files.



import sys
from numpy import zeros


fname=sys.argv[1]                # Getting input cube file
x_integ_length=sys.argv[2]       # Getting the input(Should be in Angstrom) for integ in x_axis
y_integ_length=sys.argv[3]       # Getting the input(Should be in Angstrom) for integ in y_axis
z_integ_length=sys.argv[4]       # Getting the input(Should be in Angstrom) for integ in z_axis


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

data=zeros(npoints,dtype=float)                    # Initializing


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



#x_plane=float(x_integ_length)/float(xvec)
#y_plane=float(y_integ_length)/float(yvec)
#z_plane=float(z_integ_length)/float(zvec)            # truncating z_axis for integration

#print(nat)
#print(xvortex)
#print(yvortex)
#print(zvortex)
#print(xvec)
#print(yvec)
#print(zvec)

#print(x_integ_length)

#print(y_integ_length)

#print(z_integ_length)

#print(x_plane)
#print(y_plane)
#print(z_plane)

ipt = 0
big_line = int(nat) + 6
#print(big_line)
for line in lines[big_line:]:

     arr=line.strip().split()
     npt=len(arr)
     for i in range(npt):
            data[ipt] = float(arr[i])
            ipt += 1
#print(ipt)
ipt=0


np=zeros((int(xvortex),int(yvortex),int(zvortex)),dtype=int)

for x in range(int(xvortex)):                        # Getting the number of points to integrate(Basically summing here)
     for y in range(int(yvortex)):
          for z in range(int(zvortex)):
                np[x,y,z] = ipt
                ipt +=1

sumdat = 0.0


#print(len(data))
#print(x)
#print(y)
#print(z)
#print(np.shape)

for x in range(int(x_plane)):                     # Performing integration(Basically summing)
   for y in range(int(y_plane)):
        for z in range(int(z_plane)):
              sumdat += data[np[x,y,z]]

sumdat = sumdat*vol
print(sumdat)


fp.close()
