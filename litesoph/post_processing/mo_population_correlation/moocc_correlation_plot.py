"""  Code to create contour plot given 3D data. The data is smoothed by a Gaussian and
  plotted using an inferno color-scale. 
  The following parameters are required as command line input
  fname  -> Name of data file. Data is expected as a 3-column data where the second parameter 
            is iterated first.
  na -> Number of values of first parameter
  nr -> Number of values of second parameter
  nev -> Number of divisions for the parameters in the plot
  sig -> The half-width of gaussian used for smoothing
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import copy

def plot2D(eo,eu,dmatw,fnm,sig,ne,eomin,eumax, title):

        (nx, ny) = dmatw.shape

#       ne = 51
#       sig = 0.1
        fact = 1.0/(2.0*np.pi*sig**2)
        
        ehomo = max(eo)
        elumo = min(eu)
        egap= elumo-ehomo
        print("%10.6f %10.6f %10.6f" %(ehomo,elumo,egap))

        #emini = min([min(eo), -max(eu)])
        #emaxi = max(eo)+(min(eu)-max(eo))/2.0
        emaxi = -eomin/4.0  #egap/2.0
        emini = eomin #min(eo) - epadi
        dei = (emaxi-emini)/float(ne-1)

        #emina = max(eo)-(min(eu)-max(eo))/2.0
        #emaxa = max([max(eu),-min(eo)])
        #epada = eu[ny-1]-eu[ny-2]
        emaxa = eumax #max(eu) + epada
        emina = eomin/4.0#-egap/2.0
        dea = (emaxa-emina)/float(ne-1)
        
        #nex = ne
        #ney = round((emaxa-emina)*nex/(emaxi-emini))


        xlist=np.linspace(emini,emaxi,ne)
        ylist=np.linspace(emina,emaxa,ne)
        X,Y = np.meshgrid(xlist,ylist)

        xmin = emini-dei
        xmax = emaxi+dei

        ymin = emina-dea
        ymax = emaxa+dea

        fname1=fnm+".png"

        Z=np.zeros((ne,ne), dtype=float)

        for i in range(ne):
                for j in range(ne):
                        for ix in range(nx):
                                xx = (xlist[i]+ehomo-eo[ix])/sig
                                for iy in range(ny):
                                        yy = (ylist[j]+elumo-eu[iy])/sig
                                        gx = fact*np.exp(-(xx**2+yy**2)/2.0)
                                        Z[j,i] += dmatw[ix,iy]*gx
        Z = Z/np.sum(Z)#/dei/dea 
        print(np.sum(Z), dei, dea )                                 

        plt.figure()
        #levels = range(0,500,5)
        #cp = plt.contourf(X,Y,Z,levels) #,colors='k')
        #plt.clabel(cp,colors='k',fmt='%2.1f',fontsize=12)
        #cp_filled = plt.contourf(X,Y,Z,levels)
        cp_filled = plt.contourf(X,Y,Z,cmap=cm.inferno)
        plt.colorbar(cp_filled)
        plt.title(title)
        plt.xlabel('Occupied states')
        plt.ylabel('Unoccupied states')
        plt.xlim(xmin,xmax)
        plt.ylim(ymin,ymax)
        plt.savefig(fname1)
        plt.show()

def plot_mo_population_correlations(pop_correlation_file, occ_states, unocc_states,
                                    divisions= 100, sigma= 0.5, title= 'Population Correlations'):
    ea = np.zeros(occ_states, dtype=float)
    er = np.zeros(unocc_states, dtype=float)
    dmat = np.zeros((occ_states,unocc_states), dtype=float)

    with open(pop_correlation_file, 'r') as f:
        lines = f.readlines()

    i = 0
    ia = 0
    for ia in range(occ_states):
        for ir in range(unocc_states):
            arr = lines[i].strip().split()
            if i%unocc_states == 0:
                ea[ia] = float(arr[0])
            if ia < 1:
                er[ir]=float(arr[1])
            dmat[ia,ir] = float(arr[3])    
            i += 1

    fplot_pref = "MO Population Correlations"            
    eamin = -16.0
    ermax = 24.0
    dmat=dmat/np.sum(dmat)
    plot2D(ea,er,dmat,fplot_pref,sigma,divisions,eamin,ermax, title)  
        
if __name__ == '__main__':
    pop_cor_file = sys.argv[1]
    occ = int(sys.argv[2])
    unocc = int(sys.argv[3])
    div = int(sys.argv[4])
    sig = float(sys.argv[5])
    plot_mo_population_correlations(pop_cor_file,occ, unocc, divisions=div, sigma=sig)