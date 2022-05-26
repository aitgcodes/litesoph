import sys
import math
import numpy as np

### Module for binning a distribution
### Used by proj2dos.py

def binit(a,xmin,xmax,mmax,xsig):

        dx = (xmax-xmin)/(mmax-1)
        alpha = 1.0/(2.0*xsig**2)
        h=np.zeros((mmax,2),dtype='float')
        pfact=math.sqrt(alpha/math.pi)
        #pfact=1.0


        sumh = 0.0

        for m in range(mmax):
                x = xmin + float(m)*dx
                h[m,0] = x

        for (xi,yi) in a:	
                   for m in range(mmax):
                          h[m,1] += pfact*math.exp(-alpha*(h[m,0]-xi)**2)*yi
#
#		print "#Total   ", sumh*dx
        return h
	
