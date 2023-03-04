"""
   This script creates a contour plot depicting the KS decomposition
   of the spectrum of the system. Contour plots are created for frequency
   slices of the density matrix at frequencies between wmin and wmax (input arguments).
   The list of available frequencies as well as the list of occupied and unoccupied states
   are read from the file fname given as input. This file should contain the 
   KS decomposed strength function (or the transition contribution weight) as calculated by tddenmat.py. 

   Optionally, 
   (a) the script also plots an average of the KS decomposition over frequencies in the range
   wmin to wmax. This option is activated by the switch "-i" at the end of the argument list.
   (b) the script also allows as input the gaussian width (sigma) to be used for the energy-energy 
   plots of the strength function (or transition contribution map) and the number of energy intervals (nev) to
   be used in these plots. The switches -s and -ne activate these options and are followed by the values
   to be assigned.

   usage :
		python plotdmat.py fname wmin wmax [-i] [-s <sigma>] [-ne <nev>]
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import copy

#### Methods used by main code ###########

def get_input_params(strx):	

	tint = False
	sigma = 0.1
	nev = 51 

	fname = strx[1].strip()
	wmin = float(strx[2])
	wmax = float(strx[3]) 
	xylim = float(strx[4]) 
	if len(strx) > 5:
		if "-i" in strx[5:]:
			tint = True 
		if "-s" in strx[5:]:
			i = 4
			for item in strx[5:]:
				if item == "-s":
					break
				i += 1
			sigma = float(sys.argv[i+1]) 
		if "-ne" in strx[5:]:
			i = 4
			for item in strx[5:]:
				if item == "-ne":
					break
				i += 1
			nev = int(sys.argv[i+1]) 
	print(tint)		 
	return(fname, wmin, wmax,xylim, tint, sigma, nev)			                 
                                
def read_dmat(fp):
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
	# print(ehomo)
	for ix in range(nx):
		ediff = float(arr1[ix])-ehomo
		eocc.append(ediff)
	# print(eocc)	
	
	arr1=lines[2].strip().split()

	for ix in range(ny):
		euocc.append(float(arr1[ix])-ehomo)
	# print(euocc)

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
	# print(t)
				
	return (t, dmat, nocc, eocc, euocc)
	           
                        
def plot_slice_dmatw(eo,eu,dmatw,w0,fnm):

	(nx, ny) = dmatw.shape

	xlist=np.linspace(-nx+1,0,nx)
	ylist=np.linspace(1,ny,ny)
	X,Y = np.meshgrid(xlist,ylist)

	xmin = -nx
	xmax = 1.0
	
	ymin = 0.0
	ymax = ny+1

	fname1=fnm+".png"
	
	Z=np.zeros((ny,nx), dtype=float)

	for ix in range(nx):
		for iy in range(ny):
			Z[iy,ix] = dmatw[ix,iy]

	plt.figure()
	#levels = range(0,500,5)
	#cp = plt.contourf(X,Y,Z,levels) #,colors='k')
	#plt.clabel(cp,colors='k',fmt='%2.1f',fontsize=12)
	#cp_filled = plt.contourf(X,Y,Z,levels)
	cp_filled = plt.contourf(X,Y,Z,cmap=cm.inferno)
	plt.colorbar(cp_filled)
	plt.title('KS decomposition')
	plt.xlabel('Occupied states')
	plt.ylabel('Unoccupied states')
	plt.xlim(xmin,xmax)
	plt.ylim(ymin,ymax)
	#plt.show()
	plt.savefig(fname1)
	plt.show() 	

	return fname1

def plot_slice_dmatw_en(eo,eu,dmatw,w0,fnm,sig,ne,xylim):

	(nx, ny) = dmatw.shape  
	# print(nx)   
	# print(ny)

	ne = 51
	sig = 0.1
	fact = 1.0/(2.0*np.pi*sig**2)
	emini=-xylim
	# emini = min([min(eo), -max(eu)])
	emaxi = max(eo)+(min(eu)-max(eo))/2.0
	dei = (emaxi-emini)/float(ne-1)

	emina = max(eo)-(min(eu)-max(eo))/2.0
	emaxa=xylim
	# emaxa = max([max(eu),-min(eo)])
	dea = (emaxa-emina)/float(ne-1)

	# emini=-3
	# emaxi=0.132
	# emina=-0.132
	# emaxa=3
	
	xlist=np.linspace(emini,emaxi,ne)
	ylist=np.linspace(emina,emaxa,ne)
	X,Y = np.meshgrid(xlist,ylist)  

	xmin = emini-dei  
	xmax = emaxi+dei  
	# print(emina)
	# print(emaxa)
	# print(emini)
	# print(emaxi)
	# print((eo))
	# print((eu))
	# print(min(eu))
	# print(xlist)
	# print(ylist)
	ymin = emina-dea
	ymax = emaxa+dea
	# print(ymin)
	# print(ymax)
	fname1=fnm+".png"

	Z=np.zeros((ne,ne), dtype=float)

	file_z = open('tcm_z.dat', 'w')

	for i in range(ne):
		for j in range(ne):
			for ix in range(nx):
				xx = (xlist[i]-eo[ix])/sig
				for iy in range(ny):
					yy = (ylist[j]-eu[iy])/sig
					gx = fact*np.exp(-(xx**2+yy**2)/2.0)
					# print(gx)
					# print(dmatw[ix, iy])
					Z[j,i] += dmatw[ix,iy]*gx
		# 	file_z.write("%d" %(Z[j,i]))
		# file_z.write('\n')	
	# np.savetxt('tcm.txt', Z, delimiter="            ", fmt="%s") 	
	
	plt.figure()
	#levels = range(0,500,5)
    #cp = plt.contourf(X,Y,Z,levels) #,colors='k')
    #plt.clabel(cp,colors='k',fmt='%2.1f',fontsize=12)
    #cp_filled = plt.contourf(X,Y,Z,levels)	
	
	cp_filled = plt.contourf(X,Y,Z,cmap=cm.inferno)
	plt.colorbar(cp_filled) 
	plt.title('KS decomposition') 
	plt.xlabel('Occupied states') 
	plt.ylabel('Unoccupied states')
	plt.xlim(xmin,xmax) 
	plt.ylim(ymin,ymax) 
	lineeqn=xlist+w0
	plt.plot(xlist,lineeqn)
	#plt.show()
	plt.savefig(fname1)
	plt.show()

	return fname1              

def plot_dmatw(dmatw,w,wrange,fnm):

	(nt, nx, ny) = dmatw.shape

	ncol = nx*ny

	Z=np.zeros((nt,ncol), dtype=float)
	phlist=np.zeros((ncol,2),dtype=int)

	ik = 0
    
	for ix in range(nx):
		phlist[ik,0]=ix
		for iy in range(ny):
			phlist[ik,1]=iy
			for it in range(nt):
				Z[it,ik] = dmatw[it,ix,iy]
			ik += 1             
	          
	wmin=0.0
	wmax=2.0*max(w)

	xlist = np.linspace(0, ncol-1, ncol)
	ylist = np.linspace(wmin, wmax, nt)
	X,Y = np.meshgrid(xlist,ylist)

	plt.figure()
	#levels = range(0,500,5)
	#cp = plt.contourf(X,Y,Z,levels) #,colors='k')
	#plt.clabel(cp,colors='k',fmt='%2.1f',fontsize=12)
	#cp_filled = plt.contourf(X,Y,Z,levels)
	cp_filled = plt.contourf(X,Y,Z,cmap=cm.inferno)
	plt.colorbar(cp_filled)
	plt.title('KS decomposition')
	plt.xlabel('particle-hole states')
	plt.ylabel('Excitation energy (eV)')
	plt.ylim(wrange[0],wrange[1])
	#plt.show()
	fname1 = fnm+".png"
	plt.savefig(fname1)
	plt.close()
	return phlist       
        

####### Main code begins ##########

(fname, wmin, wmax, xylim, tint, sigma, nev) = get_input_params(sys.argv)

arr = fname.strip().split('.')
fpref = arr[0]
for i in range(1,len(arr)-1):
	fpref += "."+arr[i]

# fp=file(fname,"r")
fp=open(fname,"r")
(w, dmat, nocc, eo, eu) = read_dmat(fp)
# print(w)
# np.savetxt('tcm.txt', Z, delimiter="            ", fmt="%s") 
# np.savetxt('read_strength.txt',  dmat, delimiter="   ", fmt="%s")
# print(dmat)
fp.close()
nw = len(w)
nx = len(eo)
ny = len(eu)

wrange=[]
wrange.append(wmin)
wrange.append(wmax)

xylim=xylim
#phl = plot_dmatw(dmat, w, wrange,fpref)

if not tint:
	for it in range(nw):
		print(w[it])
		if w[it] >= wmin and w[it] <= wmax:
			f1 = fpref+"_"+str(w[it])
			fn = plot_slice_dmatw_en(eo,eu,dmat[it,:,:],w[it],f1,sigma,nev)			
			print(fn)
			
			f1 = f1+"_idx"
			fn = plot_slice_dmatw(eo,eu,dmat[it,:,:],w[it],f1)
			print(fn)
else:
	dmat_tot = np.zeros((nx,ny), dtype=float)
	ntot = 0
	for it in range(nw):
		if w[it] >= wmin and w[it] <= wmax:
			dmat_tot[:,:] += (dmat[it,:,:])
			ntot += 1
	#dmat_tot =  dmat_tot/float(ntot)
	w0 = (wmax+wmin)/2.0
	f1 = fpref+"_"+str(w0)
	fn = plot_slice_dmatw_en(eo,eu,dmat_tot,w0,f1,sigma,nev,xylim)
	print(fn)
	f1 = f1+"_idx"
	fn = plot_slice_dmatw(eo,eu,dmat_tot,w[it],f1)
	print(fn)
