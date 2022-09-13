#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 22:11:43 2019

@author: varadharajan
"""

import sys
import numpy as np
from litesoph.post_processing.mo_population_correlation.fourier import Fourier
import copy

fname=sys.argv[1]
twin = ""
nframe = 1
if len(sys.argv) > 2:
    twin=sys.argv[2]
if len(sys.argv) > 3:
    nframe=int(sys.argv[3])

fp=open(fname,"r")
lines=fp.readlines()
fp.close()

ncol = 1
arr = lines[0].strip().split()
if len(arr) > 2:
   ncol = len(arr) - 1
print("%5d items read. \n" %(ncol)) 

nt=len(lines)

time=np.zeros(nt,dtype=float)
fn=np.zeros((nt,ncol),dtype=float)
frest=np.zeros((nt,ncol),dtype=float)

i=0
for line in lines:
    arr=line.strip().split()
    time[i]=float(arr[0])
    for icol in range(ncol):
        fn[i,icol]=float(arr[icol+1])
    i += 1
  
fns=copy.deepcopy(fn)
delt = time[1]-time[0]
fou=Fourier(nt,delt,twin)

### Pre-smooth if required
presmooth=1
if presmooth:
   nfrt=nframe
   for icol in range(ncol):
       fns[:,icol] = fou.smooth(fn[:,icol],nfrt)
       frest[:,icol] = fn[:,icol]-fns[:,icol]
   fps=open("fn_smooth.dat","w")
   fprs=open("fn_rest.dat","w")
   for it in range(nt):
       fps.write("{: .16e}    ".format(time[it]))
       fprs.write("{: .16e}    ".format(time[it]))
       for icol in range(ncol):
           fps.write("{: .16e}    ".format(fns[it][icol]))
           fprs.write("{: .16e}    ".format(frest[it][icol]))
       fps.write("\n")
       fprs.write("\n")
   fps.close()
   fprs.close()
   print("Smoothed")
