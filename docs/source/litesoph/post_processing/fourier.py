import re
import numpy as np
from numpy import fft
from scipy import signal
from scipy.signal import windows, hilbert
import copy

class Fourier:

      def __init__(self, nt, delt, window):
          
          self.nt = nt
          self.wintype = window
          self.wfn = self.set_window(nt)
          self.delt = delt
          self.freqs = np.zeros(nt,dtype=float)   

      def set_window(self,nt):

          wtyp = self.wintype

          try:
             wfn = windows.get_window(wtyp,nt)  
          except:
             print('Unknown window type {} ! Default window will be used.'.format(wtyp))
             wfn = windows.get_windwos('boxcar',nt)

          return wfn

      def write_window(self):
          
          assert len(self.wfn) > 0, 'Window not defined!'

          fwin=open("window.dat","w")
          for it in range(self.nt):
              fwin.write("%10.6f %10.6f\n" %(it*self.delt, self.wfn[it]))
          fwin.close()
          	  
      def transform(self, fn, window=True):

          ### Real function expected as input

          fxn = np.zeros(self.nt, dtype=float)
          if window:
              fxn = fn*self.wfn
          else:
              fxn = fn
          
          self.freqs = np.fft.fftfreq(self.nt)/self.delt  
          fw = np.fft.fft(fxn)
          
          return self.freqs, fw
      
      def smooth(self, fn, nfr):
         
          win = self.set_window(nfr)
          fil = signal.convolve(fn,win,mode='same')/sum(win)
          
          return fil

      def envelope(self, sig):
          fs = 1/self.delt
          asg = hilbert(sig)
          ampl_envl = np.abs(asg)
          #puresig = sig/amp_envl
          phase_i = np.unwrap(np.angle(asg))
          frequency_i = (np.diff(phase_i)/(2.0*np.pi) * fs)

          return (ampl_envl, frequency_i)