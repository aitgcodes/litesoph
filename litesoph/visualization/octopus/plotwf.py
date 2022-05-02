"""
   This script creates cube files consisting of the transition densities 
   at the input frequencies (wmin to wmax) from the KS wavefunctions in 
   cube format stored in <fpref> and the frequency dependent density matrix 
   read from "dmatw.dat" in the working directory.

   The list of available frequencies as well as the list of occupied and unoccupied states
   are read from "dmatw.dat". 

   Optionally, 
	(a) the script also computes the total transition density over frequencies in the range
   	    wmin to wmax. This option is activated by the switch "-i" at the end of the argument list.
	(b) the script computes the contribution to the transition density from the iocc --> iuocc 
            excitation. This option is activated by the switch "-s" followed by the values of iocc and iuocc.
	(c) the script instructs the cubehandler routines to convert cube file data to bohr from angstroms.
	    This option is activated by the switch "-a"

   The three switches, when used, should appear after the path of the cube files (fpref), range of frequencies
   (wmin and wmax) are specified. Their order of appearance does not matter.

   Usage :
		python plotwf.py fpref wmin wmax [-i] [-s iocc iuocc] [-a]
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import copy
from cubehandler import cubeio

fname = sys.argv[1]
wmin = float(sys.argv[2])
wmax = float(sys.argv[3])

#### Methods used by main code ###########

def get_input_params(strx):

	tint = False
	tspec = False
	tang = False
	iocc = 0
	iuocc = 0

	fname = strx[1].strip()
	wmin = float(strx[2])
	wmax = float(strx[3])

	if len(strx) > 4:
		if "-i" in strx[4:]:
			tint = True
		if "-s" in strx[4:]:
			tspec = True
			i = 4
			for item in strx[4:]:
				if item == "-s":
					break
				i += 1
			iocc = int(sys.argv[i+1])
			iuocc = int(sys.argv[i+2])
		if "-a" in strx[4:]:
			tang = True

	return (fname, wmin, wmax, tint, tspec, tang, iocc, iuocc)

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


def cal_chden(den,wo,wu,nx,ny,nz,io,iu):

	chd = np.zeros((nx,ny,nz), dtype = float)

	ik = 0
	for ix in range(nx):
		for iy in range(ny):
			for iz in range(nz):
				chd[ix,iy,iz] = wo[ik]*den*wu[ik]
				ik += 1
	return chd

#### Main code begins ########

(fpref, wmin, wmax, tint, tspec, tang, iocc, iuocc) = get_input_params(sys.argv)
print fpref, wmin, wmax, tint, tspec, tang, iocc, iuocc

fp=file("dmatw.dat","r")
(w, dmat, nocc, eo, eu) = read_dmat(fp)
fp.close()
nw = len(w)
nx = len(eo)
ny = len(eu)

wrange=[]
wrange.append(wmin)
wrange.append(wmax)

fmt = "cube"
wf_occ = []
wf_unocc = []

mycube = cubeio(tang)

for i in range(nx):
	k = nocc-nx+i 
	axr = fpref+"/"+"wf-st"+format(k+1,"04")+".cube"
	fp = file(axr,"r")
	wf = mycube.readcube(fp)
	fp.close()
	wf_occ.append(wf)

for i in range(ny):
	k = nocc+i
	axr = fpref+"/"+"wf-st"+format(k+1,"04")+".cube"
	fp = file(axr,"r")
	wf = mycube.readcube(fp)
	fp.close()
	wf_unocc.append(wf)

print "Read in wavefunction files ..."

npx = abs(mycube.nv[0])
npy = abs(mycube.nv[1])
npz = abs(mycube.nv[2])

widx = []
for it in range(nw):
	if w[it] >= wmin and w[it] <= wmax:
		widx.append(it)

chden = np.zeros((npx,npy,npz), dtype=float)
chden_tot = np.zeros((npx,npy,npz), dtype=float)

if not tint:
	if not tspec:
		print "Summing over particle-hole excitations"
		for it in widx:
			f1 = "chden_"+str(w[it])
			for i in range(nx):
				for j in range(ny):
					chden += cal_chden(dmat[it,i,j],wf_occ[i],wf_unocc[j],npx,npy,npz,i,j)
			fn = mycube.writecube(f1,chden)
			print fn
	else:
		print "Contributions for specified particle-hole excitation being computed..."
                for it in widx:
                        f1 = "chden_"+str(w[it])
			chden = cal_chden(dmat[it,iocc,iuocc],wf_occ[iocc],wf_unocc[iuocc],npx,npy,npz,iocc,iuocc)		
			fn = mycube.writecube(f1,chden)
			print fn
else:
	if not tspec:
		print "Summing over particle-hole excitations"
		for it in widx:
			for i in range(nx):
				for j in range(ny):
					chden += cal_chden(dmat[it,i,j],wf_occ[i],wf_unocc[j],npx,npy,npz,i,j)
			chden_tot[:,:,:] += chden[:,:,:]
	else:
		print "Contributions for specified particle-hole excitation being computed..."
                for it in widx:
                        chden = cal_chden(dmat[it,iocc,iuocc],wf_occ[iocc],wf_unocc[iuocc],npx,npy,npz,iocc,iuocc)		
                        chden_tot[:,:,:] += chden[:,:,:]

	w0 = (wmax+wmin)/2.0
	f1 = "chden_"+str(w0)
	fn = mycube.writecube(f1,chden_tot)
	print fn
