from copy import copy
from ctypes import sizeof
from signal import signal
from tkinter import W
from turtle import shape
import numpy as np
import numpy.ma as ma
import scipy as sp
from matplotlib import pyplot as plt 
import os
import argparse


################################### Read Signal ########################################################################## 

## Read Signal File
# data = np.loadtxt(ifname)


data = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/Reproduce_C2H4/C2H4_Test/24_09_oct/td.general_laser_td10_add/multipoles', skiprows=17)
# data = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/octopus/LASER_0.5EV_FWHM_td.general/multipoles')
# laser=np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/octopus/LASER_0.5EV_FWHM_td.general/laser')
# data = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/octopus/td.general_9.3eV_2.5eV_Same_E0_LASER/multipoles', skiprows=17)
# laser=np.genfromtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/octopus/td.general_9.3eV_2.5eV_Same_E0_LASER/laser',delimiter='\n',dtype=None,skip_header=6)
# laser=np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/octopus/td.general_9.3eV_2.5eV_LASER/laser')
laser00=np.loadtxt('/home/niel/sachin/h2o_pulse/h2o/test/C2H4/pulse0.dat')
laser01=np.loadtxt('/home/niel/sachin/h2o_pulse/h2o/test/C2H4/pulse1.dat')
# data = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Pump_Probe/C2H4/gpaw/TD_Laser_Delta1/dm.dat', skiprows=2)

# laser1=laser[:,2]
# laser2=laser[:,5]

# laser0=laser00[:,1] ## For GPAW
# laser1=laser01[:,1] ## For GPAW
# time = data [:,0] ## For GPAW
# sx = data [:,2]     ## For GPAW

time = data [:,1] 
sx = data [:,3]
# sy = data [:,4]
# sz = data [:,5]

# data = np.loadtxt('/home/niel/Documents/C901/test/Lite_Test/Long_Run_CH4/nwchem/Spectrum/dipole.dat', skiprows=27)  ## For NWChem
# time = data [:,0]  ## For NWChem
# sx = data [:,1]     ## For NWChem



# ##Signal Selection########## 
s = sx 
# s = sy 
# s = sz 

###########Total Window design for whole signal###########
tmid=time[len(time)//2]
fwhm_total=0.8*tmid   # # FWHM=2.355*(standard deviation^0.5) in same unit of time 
sigma_total =fwhm_total/2.355
w=np.exp(-0.5 * (time - tmid)**2 / sigma_total**2 ) #Gaussian Window with fwhm same as the mid point of time length


m=2 #Number of snap of whole time signal


##############FFT of total Signal
sw=s*w  #Windowed Signal for fft
sfft = np.fft.fft(sw) ##fft of the whole signal
REsfft=sfft.real         ## Real part of fft
IMsfft=sfft.imag         ## Imaginary part of fft
ABSsfft=np.abs(sfft)     ## Absolute of fft

T = time[1] - time[0]  # sampling interval 
N=len(s)
f = np.linspace(0, 1 / T, N)
omega=2*np.pi*f

#####################Plot Time signal and total fft of the signal##########
freq_lim=20
plt.subplot((m+1),2,1)
plt.ylabel("Amplitude")
plt.plot(time, s)
# plt.twinx().plot(laser00[:,0],laser0,color="red")
# plt.twinx().plot(laser01[:,0],laser1,color="red")

plt.subplot((m+1),2,2)
plt.ylabel("Amplitude")
plt.xlabel("Frequency [eV]")
# plt.plot(omega[:N // 2], REsfft[:N // 2] * 1 / N)  # 1 / N is a normalization factor
# plt.plot(omega[:N // 2], omega[:N // 2]* IMsfft[:N // 2] * 1 / N)  # 1 / N is a normalization factor
plt.plot(omega[:N // 2], ABSsfft[:N // 2] * 1 / N)  # 1 / N is a normalization factor
plt.xlim(0,freq_lim)
# plt.show ()

####################### Window Envelop Design###############
# m=5 #Number of snap of whole time signal
t_mid0=time[len(time)//m]
T_mid=np.arange(t_mid0//2,m*(t_mid0),t_mid0)
# print(T_mid)
fwhm=0.9*(t_mid0//2)  
sigma =fwhm/2.355



file=np.array([])

for n in range(0,m):

     
     globals()['w'+str(n)]=np.exp(-0.5 * (time - (T_mid[n]))**2 / sigma**2 )  #Window Function

    #  plt.plot(globals()['w'+str(n)])
    #  plt.show()

     globals()['s'+str(n)]=s*globals()['w'+str(n)]  #Signal clipped with window shape

     globals()['ffts'+str(n)]= (np.fft.fft(globals()['s'+str(n)])) #fft of clipped Signals
     globals()['REffts'+str(n)]= (np.fft.fft(globals()['s'+str(n)])).real #Real part of fft of clipped Signals
     globals()['IMffts'+str(n)]= (np.fft.fft(globals()['s'+str(n)])).imag #Imaginary part offft of clipped Signals
     globals()['ABSffts'+str(n)]= np.abs(np.fft.fft(globals()['s'+str(n)])) #Absolute value fft of clipped Signals

     globals()['t'+str(n)]=time  #Time length of each clipped signals

     globals()['N'+str(n)]= globals()['s'+str(n)].size
      
     globals()['f'+str(n)]= np.linspace(0, 1 / T, globals()['N'+str(n)]) ## Frequency
     
     globals()['omega'+str(n)]= globals()['f'+str(n)]*2*np.pi ##Omega
    #  #  
     plt.subplot((m+1),2,2*n+3)

     plt.plot(globals()['t'+str(n)],globals()['s'+str(n)])
      
     plt.subplot((m+1),2,2*n+4)
     # plt.plot(globals()['omega'+str(n)][:globals()['N'+str(n)]// 2], globals()['REffts'+str(n)][:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)])  # 1 / N is a normalization factor
     # plt.plot(globals()['omega'+str(n)][:globals()['N'+str(n)]// 2], globals()['omega'+str(n)][:globals()['N'+str(n)]// 2]* globals()['IMffts'+str(n)][:globals()['N'+str(n)] // 2] )  # 1 / N is a normalization factor
     plt.plot(globals()['omega'+str(n)][:globals()['N'+str(n)]// 2], globals()['ABSffts'+str(n)][:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)])  # 1 / N is a normalization factor
     plt.xlim(0,freq_lim)


     # ##Finding the all required frequency with a damping factor of d from the fft and f array 
     #  ## the frequency which have the amplitude greater than Maximum Amplitude/Damping factor will appear 
     # d=90
     #  ## Searching Amplitude greater than the maxamplitude/d
     # globals()['amp'+str(n)]=np.abs(globals()['ffts'+str(n)])[(np.abs(globals()['ffts'+str(n)])>(np.max(np.abs(globals()['ffts'+str(n)]))/d)) & (globals()['f'+str(n)]<(np.max(globals()['f'+str(n)])/2) )]
      
     #  ## Searching Frequency which has amplitude greater than the maxamplitude/d
     # globals()['freq'+str(n)]=globals()['f'+str(n)][(np.abs(globals()['ffts'+str(n)]) > (np.max(np.abs(globals()['ffts'+str(n)]))/d)) & (globals()['f'+str(n)]<(np.max(globals()['f'+str(n)])/2) )]
      
     #  #Creating new array to write frequency and amplitudes
     # globals()['fft_out'+str(n)]=np.array([globals()['freq'+str(n)],globals()['amp'+str(n)]]).T
      
     #  #Writing the array to an array
     # file=np.vstack([file,globals()['fft_out'+str(n)]]) if file.size else globals()['fft_out'+str(n)]

     ################################Creating new array to write frequency and amplitudes###########################################
    #  globals()['fft_out'+str(n)]=np.array([globals()['freq'+str(n)],globals()['amp'+str(n)]]).T
    #  globals()['fft_out'+str(n)]=np.array([globals()['f'+str(n)][:globals()['N'+str(n)]// 2], globals()['fft'+str(n)][:globals()['N'+str(n)] // 2] * 1 / globals()['N'+str(n)]]).T
     
     # globals()['fft_out'+str(n)]=np.array([globals()['REffts'+str(n)][:globals()['N'+str(n)] // 2] ]).T  ## Normalise by the length of N
   
     # globals()['fft_out'+str(n)]=np.array([globals()['IMffts'+str(n)][:globals()['N'+str(n)] // 2] ]).T  ## Normalise by the length of N
    
     globals()['fft_out'+str(n)]=np.array([globals()['ABSffts'+str(n)][:globals()['N'+str(n)] // 2] ]).T  ## Normalise by the length of N
    
    #  globals()['fft_out'+str(n)]=np.array([globals()['fft'+str(n)][:globals()['N'+str(n)] // 2] * 1 / (np.max(globals()['fft'+str(n)]))]).T    ## Normalise by the max of Amplitude
      
      #Writing the array to an array
     file=np.hstack([file,globals()['fft_out'+str(n)]]) if file.size else globals()['fft_out'+str(n)]
     # file=np.hstack([file,(globals()['fft_out'+str(n)]-globals()['fft_out'+str(n-1)])]) if file.size else globals()['fft_out'+str(n)]

     # print(globals()['fft_out'+str(0)])





# test_file=globals()['fft_out'+str(1)]
##################################Find the Amplitude Differens Delta Amplitude######################################################################
# delta_amp=np.zeros((2000,3))
# delta_amp=file

delta_amp=np.zeros(np.shape(file))
amp=np.zeros(np.shape(file))
for n in range(0,m):
     # delta_amp[:,0]=file[:,0]
     # print(n)
     amp[:,n]=globals()['fft_out'+str(n)].transpose()
     if n == 0:
          # delta_amp[:,0]=globals()['fft_out'+str(0)].transpose()
          delta_amp[:,n]=amp[:,n]
     else:
          # delta_amp[:,n]=file[:,n]-file[:,0]
          delta_amp[:,n]=amp[:,n]-amp[:,0]
          # delta_amp[:,n]=globals()['fft_out'+str(n)].transpose()-globals()['fft_out'+str(0)].transpose()
############################################################Contour Plot###########################################################
x=T_mid
y=globals()['omega'+str(n)][:globals()['N'+str(n)]// 2]

X,Y= np.meshgrid(x,y)  #Grid
# Z=delta_amp
Z=amp
# Z=file

plt.figure()
# plt.contourf(X,Y,Z,interpolation='gaussian')
plt.contourf(X,Y,Z)
plt.ylim(0,freq_lim)
plt.xlabel('Delay Time (femtosecond)')
labels, locations = plt.xticks()
plt.xticks(labels, labels*24.2e-3)   #time conversion from a.u. to fs
plt.ylabel('Frequency (eV)')
labels, locations = plt.yticks()
plt.yticks(labels, labels*27.211324570273)   #time conversion from a.u. to fs

plt.colorbar().set_label('Delta Amplitude', rotation=270)






##Adding Header    
# file_header=np.array([["Frequency","Amplitude"]])
# file=np.vstack((file_header,file)) 

# file=np.hstack([file,globals()['omega'+str(n)]])


##Removing Existing File
# os.remove("test_fft_data_new.txt") 
# os.remove("test_fft_frequency.txt") 

#Writing the array to an file
# np.savetxt('test_fft_Amp_data.txt', test_file, delimiter="            ", fmt="%s") 
# np.savetxt('fft_Amp_data.txt', amp, delimiter="            ", fmt="%s") 
# np.savetxt('fft_Delta_Amp_data.txt', delta_amp, delimiter="            ", fmt="%s") 
# np.savetxt('fft_frequency.txt', globals()['omega'+str(n)], delimiter="            ", fmt="%s") 



plt.show()