import sys
from math import *
from math import sqrt
import cmath
import numpy as np

####################################################################

A=np.loadtxt(sys.argv[1])
B=np.array(A)
t=B[:,0]
H_total = []
for column in range(1,A.shape[1]):
    f=B[:,column]

    ###############################################################
    def mean(x):
        return sum(x)/len(x)
    h=f-mean(f)

    ################################################################
    D=t[1]-t[0]
    ################################################################

    L=h*h
    L1=(sum(L))*D
#    print(L1,D,L,h)
    L2=sqrt(L1)
    C=1.0/len(h)*L2
    ###################################################################
    N=int(len(h))
    M=int(N/2)

    #####################################################################
    H=[]
    f=[]
    for n in range(0,M+1,1):
        fn=n/(N*D)
        S=complex(0.0,0.0)
        for k in range(0,N,1):
            S=S+h[k]*cmath.exp(-2*pi*complex(0.0,1.0)*fn*t[k])
        f.append(fn)
        H.append(S*D)
    H_total.append(np.array(H))
    ######################################################################

P=4.142
Q=0.02419
V=P/Q

outfile = open("outfile.txt","w")
for i in range(len(H_total[0])):
    outfile.write("     {:10.6f}    ".format(V*f[i]))
    for h in H_total:
        outfile.write("{: .16e}    ".format(np.absolute(h[i])**2*C))
    outfile.write("\n")
outfile.close()
#####################################################################
