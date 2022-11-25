# from signal import signal
from tkinter import W
from turtle import shape
import numpy as np
import numpy.ma as ma
import scipy as sp
from scipy import signal
from matplotlib import pyplot as plt 
import os
import argparse



###################################Genrate or Read Signal########################################################################## 

## Read Signal File
# data = np.loadtxt(ifname)
#data = np.loadtxt('multipoles', skiprows=17)
# time = data [:,1]
# sx = data [:,3]
# sy = data [:,4]
# sz = data [:,5]




##Generate Signal Frequency Modulated 
time = np.linspace(0, 0.5, 1000)

    ###Signal Generation
# s=[]
# for t in time:
#     if t>0.2:
#         sig = np.sin(40 * 2 * np.pi * t) + 0.5 * np.sin(90 * 2 * np.pi * (t))
#     else:
#         sig = np.sin(40 * 2 * np.pi * t) + 0.5 * np.sin(250 * 2 * np.pi * (t))
#     s.append(sig)

f0=100
v=0.5
ft =f0*(1+np.cos(v*2 * np.pi * time))
s = np.sin(ft* 2 * np.pi * time)




################################FFT of total Signal using windowing function########################################## 
    
    ###Window Design (Gaussian) for total spectra
fwhm=0.3   
sigma =fwhm/2.355
w=np.exp(-0.5 * (time - 0.25)**2 / sigma**2 )
    
    ###############################FFT of the signal 
fft = np.fft.fft(s*w)
fftabs=np.abs(fft)
T = time[1] - time[0]  # sampling interval 
N=len(s)
f = np.linspace(0, 1 / T, N)



############################################ Window Envelop Design###################################################################
fwhm=0.05   # FWHM=2.355*(standard deviation^0.5) in same unit of time 
sigma =fwhm/2.355
################################Delay Time Array##################################
t_mid=[0.05,0.15,0.25,0.35,0.45]
m=len(t_mid)

##########################Splitting Signal#######################################
s_split=np.array_split(s,m)
t_split=np.array_split(time,m)
# w=np.exp(-0.5 * (time - t0)**2 / sigma**2 )



################################################################### Plot Original Signals and its FFT###############################
plt.subplot((m+1),2,1)
plt.ylabel("Amplitude")
plt.plot(time, s*w)

plt.subplot((m+1),2,2)
plt.ylabel("Amplitude")
plt.xlabel("Frequency [Hz]")
plt.plot(f[:N // 2], np.abs(fft)[:N // 2] * 1 / N)  # 1 / N is a normalization factor
plt.xlim(0,250)


############################################### Itterating over the whole signal#################################################
file=np.array([])
delta_amp=np.array([])

for n in range(0,m):
     
     
     globals()['t'+str(n)]=t_split[n]

     ########### Custom Designed Gaussian Function################################################################## 
    #  globals()['w'+str(n)]=np.exp(-0.5 * (globals()['t'+str(n)] - t_mid[n])**2 / sigma**2 )  #Window Function
     
     ##################Scipy Library Window Functions################################################################
     width=globals()['t'+str(n)].size
    #  print(width)
    #  globals()['w'+str(n)]=signal.windows.gaussian(width, std=width//5)
    #  globals()['w'+str(n)]=signal.windows.hamming(width)
     globals()['w'+str(n)]=signal.windows.hann(width)
    #  globals()['w'+str(n)]=signal.windows.bartlett(width)
    #  globals()['w'+str(n)]=signal.windows.kaiser(width,10)
     
    #  plt.plot(globals()['t'+str(n)],globals()['w'+str(n)])
    #  plt.show()



    ######################################## Windowed Signals and FFT of the signals######################################

     globals()['s'+str(n)]=s_split[n] *globals()['w'+str(n)]  #Signal clipped with window shape

     globals()['fft'+str(n)]= np.abs(np.fft.fft(globals()['s'+str(n)])) #fft of clipped Signals

    #  globals()['t'+str(n)]=time  #Time length of each clipped signals equals to total time

     globals()['N'+str(n)]= globals()['s'+str(n)].size
      
     globals()['f'+str(n)]= np.linspace(0, 1 / T, globals()['N'+str(n)])
     



    #######Ploting Temporal Signals  and signals in frequency domain#################################################
     plt.subplot((m+1),2,2*n+3)
     plt.plot(globals()['t'+str(n)],globals()['s'+str(n)])
      
     plt.subplot((m+1),2,2*n+4)
     plt.plot(globals()['f'+str(n)][:globals()['N'+str(n)]// 2], np.abs(globals()['fft'+str(n)])[:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)])  # 1 / N is a normalization factor
     plt.xlim(0,250)


    
    ################################Creating new array to write frequency and amplitudes###########################################
    #  globals()['fft_out'+str(n)]=np.array([globals()['freq'+str(n)],globals()['amp'+str(n)]]).T
    #  globals()['fft_out'+str(n)]=np.array([globals()['f'+str(n)][:globals()['N'+str(n)]// 2], globals()['fft'+str(n)][:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)]]).T
     globals()['fft_out'+str(n)]=np.array([globals()['fft'+str(n)][:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)]]).T  ## Normalise by the length of N
    #  globals()['fft_out'+str(n)]=np.array([globals()['fft'+str(n)][:globals()['N'+str(n)] // 2] * 1 / (np.max(globals()['fft'+str(n)]))]).T    ## Normalise by the max of Amplitude
      #Writing the array to an array
     file=np.hstack([file,globals()['fft_out'+str(n)]]) if file.size else globals()['fft_out'+str(n)]







##################################Find the Amplitude Differens Delta Amplitude######################################################################
delta_amp=file
for n in range(0,m):
     delta_amp[:,0]=file[:,0]
     if n>0:
         delta_amp[:,n]=file[:,n]-file[:,0]






############################################################Contour Plot###########################################################
x=t_mid
y=globals()['f'+str(n)][:globals()['N'+str(n)]// 2]

X,Y= np.meshgrid(x,y)  #Grid
# Z=delta_amp
Z=file

plt.figure()
plt.contourf(X,Y,Z)

plt.ylim(0,210)
plt.xlabel('Delay Time')
plt.ylabel('Frequency')
plt.colorbar().set_label('Delta Amplitude', rotation=270)




##################################################Writing the array to an file######################################################
# np.savetxt('fft_data_Chop_Window.txt', file, delimiter="            ", fmt="%s") 


plt.show()