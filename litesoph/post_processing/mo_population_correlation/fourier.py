import re
import numpy as np
from numpy import fft
from scipy import signal
import copy

class Fourier:

      def __init__(self, nt, delt, window):
          
          self.nt = nt
          self.wintype = window
          self.delt = delt
          self.freqs = np.zeros(nt,dtype=float)   
      
      def window(self):
          
          wfn = np.zeros(self.nt, dtype=float)
          wtyp = self.wintype
        
          if re.search("hamming",wtyp,re.I):
             wfn = np.hamming(self.nt)  
          elif re.search("blackman",wtyp,re.I):
             wfn = np.blackman(self.nt)
          elif re.search("hanning",wtyp,re.I):
             wfn = np.hanning(self.nt)

          fwin=open("window.dat","w")
          for it in range(self.nt):
              fwin.write("%10.6f %10.6f\n" %(it*self.delt, wfn[it]))
          fwin.close()
          return wfn
          	  
      def transform(self, fn, wtyp=""):

          fxn = np.zeros(self.nt, dtype=float)
          if not wtyp == "":
              fxn[:] = fn[:]*self.window()[:]
          else:
              fxn = fn
          
          self.freqs = np.fft.fftfreq(self.nt)/self.delt  
          fw = np.fft.fft(fxn)
          
          return self.freqs, fw
      
      def smooth(self, fn, nfr):
         
          win = signal.hann(nfr)
          fil = signal.convolve(fn,win,mode='same')/sum(win)
          
          return fil
