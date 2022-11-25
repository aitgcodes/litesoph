from signal import signal
from tkinter import W
from turtle import shape
import numpy as np
import numpy.ma as ma
import scipy as sp
from matplotlib import pyplot as plt 
import os
import argparse



####Genrate or Read Signal 

## Read Signal File
# data = np.loadtxt(ifname)
# t = data [:,0]
# s = data [:,1]

##Generate Signal Frequency Modulated 

time = np.linspace(0, 0.5, 1000)
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

# sw=s*w
# ##FFT of total Signal
fwhm=0.3   # 
sigma =fwhm/2.355
w=np.exp(-0.5 * (time - 0.25)**2 / sigma**2 )
fft = np.fft.fft(s*w)
fftabs=np.abs(fft)
T = time[1] - time[0]  # sampling interval 
N=len(s)
f = np.linspace(0, 1 / T, N)



### Window Envelop Design
fwhm=0.05   # FWHM=2.355*(standard deviation^0.5) in same unit of time 
sigma =fwhm/2.355
t_mid=[0.1,0.2,0.3,0.4]
m=len(t_mid)
# w=np.exp(-0.5 * (time - t0)**2 / sigma**2 )
file=np.array([])

print(len(f))
print(len(f[:N // 2]))
####
plt.subplot((m+1),2,1)
plt.ylabel("Amplitude")
plt.plot(time, s*w)

plt.subplot((m+1),2,2)
plt.ylabel("Amplitude")
plt.xlabel("Frequency [Hz]")
plt.plot(f[:N // 2], np.abs(fft)[:N // 2] * 1 / N)  # 1 / N is a normalization factor
plt.xlim(0,250)



for n in range(0,m):

     
     globals()['w'+str(n)]=np.exp(-0.5 * (time - (t_mid[n]))**2 / sigma**2 )  #Window Function

    #  plt.plot(globals()['w'+str(n)])
    #  plt.show()

     globals()['s'+str(n)]=s*globals()['w'+str(n)]  #Signal clipped with window shape

     globals()['fft'+str(n)]= np.abs(np.fft.fft(globals()['s'+str(n)])) #fft of clipped Signals

     globals()['t'+str(n)]=time  #Time length of each clipped signals

     globals()['N'+str(n)]= globals()['s'+str(n)].size
      
     globals()['f'+str(n)]= np.linspace(0, 1 / T, globals()['N'+str(n)])
     
    #  #  
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




#      ##Finding the all required frequency with a damping factor of d from the fft and f array 
#       ## the frequency which have the amplitude greater than Maximum Amplitude/Damping factor will appear 
#      d=90
#       ## Searching Amplitude greater than the maxamplitude/d
#      globals()['amp'+str(n)]=np.abs(globals()['fft'+str(n)])[(np.abs(globals()['fft'+str(n)])>(np.max(np.abs(globals()['fft'+str(n)]))/d)) & (globals()['f'+str(n)]<(np.max(globals()['f'+str(n)])/2) )]
      
#       ## Searching Frequency which has amplitude greater than the maxamplitude/d
#      globals()['freq'+str(n)]=globals()['f'+str(n)][(np.abs(globals()['fft'+str(n)]) > (np.max(np.abs(globals()['fft'+str(n)]))/d)) & (globals()['f'+str(n)]<(np.max(globals()['f'+str(n)])/2) )]
      
#       #Creating new array to write frequency and amplitudes
#      globals()['fft_out'+str(n)]=np.array([globals()['freq'+str(n)],globals()['amp'+str(n)]]).T
      
#       #Writing the array to an array
#      file=np.vstack([file,globals()['fft_out'+str(n)]]) if file.size else globals()['fft_out'+str(n)]


# ##Adding Header    
# file_header=np.array([["Frequency","Amplitude"]])
# file=np.vstack((file_header,file)) 

# ##Removing Existing File
# # os.remove("fft_data.txt") 

# #Writing the array to an file
# np.savetxt('fft_data_new.txt', file, delimiter="    ", fmt="%s") 




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
Z=delta_amp

plt.figure()
plt.contourf(X,Y,Z,interpolation='gaussian')
plt.ylim(0,210)
plt.xlabel('Delay Time')
plt.ylabel('Frequency')
plt.colorbar().set_label('Delta Amplitude', rotation=270)


plt.show()