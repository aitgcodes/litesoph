import numpy as np
from numpy import fft
import copy

class Projections:

        def __init__(self,nt,nocc=1,nunocc=0):
                self.nt=nt
                self.nocc=nocc
                self.nunocc=nunocc
                self.nst=nocc+nunocc
                self.projn=np.zeros((nt,self.nst,self.nst,2),dtype=float)
                self.wt=np.zeros(self.nst,dtype=float)
                self.muvec=np.zeros((self.nst,self.nst,3),dtype=float)		
                self.time=np.zeros(nt, dtype=float)
                self.delt=1.0
                self.kick=1.0

        def extract(self,fp,ibeg):

                lines=fp.readlines()
                nst=self.nst
                nt=self.nt
		
                itr = 0
                iskp = 0
                for line in lines:
                        line=line.strip()
                        if "#" in line:
                                if "w(ik)" in line:
                                   arr1=line.strip().split()[2:]
                                   for i in range(nst):
                                        self.wt[i]=float(arr1[i])
		#                  self.wt = self.wt/sum(self.wt)
                                elif "<i|x_1|a>" in line:
                                   arr1=line.strip().split()[3:]
                                   ir = 0
                                   for i in range(0,nst):
                                          for j in range(nst):
                                                self.muvec[i,j,0] = float(arr1[ir])
                                                ir += 2
                                elif "<i|x_2|a>" in line:
                                   arr1=line.strip().split()[3:]
                                   ir = 0
                                   for i in range(0,nst):
                                          for j in range(nst):
                                                self.muvec[i,j,1] = float(arr1[ir])
                                                ir += 2
                                elif "<i|x_3|a>" in line:
                                   arr1=line.strip().split()[3:]
                                   ir = 0
                                   for i in range(0,nst):
                                          for j in range(nst):
                                                self.muvec[i,j,2] = float(arr1[ir])
                                                ir += 2
                                elif "kick strength" in line:
                                   arr1=line.strip().split()
                                   dk = float(arr1[3])
                                   if dk > 1.e-6:
                                        self.kick = dk
                                   else:
                                        self.kick = 0.01
                                continue
		
                        if iskp < ibeg-1:
                                iskp += 1
                                continue

                        arr=line.split()
                        t = float(arr[1])
                        ist = 2
                        for i in range(nst):
                                for j in range(nst):
                                        for k in range(2):
                                                self.projn[itr,i,j,k]=float(arr[ist])
                                                ist += 1
		
                        self.time[itr] = t
                        itr += 1

                        if itr >= nt:
                                break

                if nt > 1:
                        self.delt = self.time[1]-self.time[0]
		
                return (self.kick, self.delt)

        def populations(self,stlst):
		
                popln=np.zeros((len(stlst),self.nt),dtype=float)
                nt=self.nt
                nst=self.nst

                for itr in range(nt):
                    ipj = 0
                    for ist in stlst:
                        for i in range(nst):
                                popln[ipj,itr] += self.wt[i]*(self.projn[itr,i,ist,0]**2 + self.projn[itr,i,ist,1]**2)	
                        ipj += 1

                return popln

        def write_pop(self,a,fp):
		
                (np, nt) = a.shape

                for it in range(nt):
                        t = it*self.delt
                        fp.write("%10.6f " %(t))
                        for ip in range(np):
                                fp.write("%10.6f " %(a[ip,it]))
                        fp.write("\n")

        def denmat(self,ost,ust):
		
                occ=[]
                unocc=[]
                nt=self.nt
                nst=self.nst
		
                for i in range(ust):
                        unocc.append(self.nocc+i)

                nost=self.nocc-ost
                for i in range(nost,self.nocc):
                        occ.append(i)

#		return len(occ), len(unocc), ost, ust

                dmat=np.zeros((nt,ost,ust),dtype='complex')
                dmat0=np.zeros((ost,ust),dtype='complex')

                for itr in range(nt):
                    dmat[itr,:,:] = 0.0
                    for i1 in range(ost):
                        iocc = occ[i1]
                        for i2 in range(ust):
                               iunocc = unocc[i2]
                               for ist in range(nst):
                                   p1 = complex(self.projn[itr,ist,iocc,0],self.projn[itr,ist,iocc,1])  
                                   p2 = complex(self.projn[itr,ist,iunocc,0],self.projn[itr,ist,iunocc,1])  
                                   dmat[itr,i1,i2] += p2.conjugate()*p1*self.wt[ist]

                               dmat[itr,i1,i2] = dmat[itr,i1,i2] - dmat0[i1,i2]
				
                return occ, unocc, self.time, dmat

        def ft_dmat(self,dmat,occ,unocc,axis):

                (nt, nx, ny) = dmat.shape

                thresh = 1e-6 ## Minimum threshold for division
                sigma = 0.08
                axmag = 0.0
          
                for k in range(3):
                        axmag += axis[k]**2
                axmag = np.sqrt(axmag)

                dmatw = np.zeros((nt,nx,ny), dtype='complex')
                resp = np.zeros((nt,nx,ny), dtype=float)
                wia = np.zeros((nt,nx,ny), dtype=float)
                resptot = np.zeros(nt, dtype=float)
                freqs = np.fft.fftfreq(nt)/self.delt
                delw = 2*np.pi*(freqs[1]-freqs[0])
                if (nt % 2) == 0:
                   npos = nt//2
                else:
                   npos = nt//2 + 1

                gauss=np.zeros(nt, dtype=float)

                for it in range(nt):
                        t = it*self.delt
                        gauss[it] = np.exp(-sigma*t**2/2.0)

		
                for ix in range(nx):
                    x=occ[ix]
                    for iy in range(ny):
                        y=unocc[iy]
                        ft = gauss[:]*dmat[:,ix,iy]
                        fw = np.fft.fft(ft)
                        dmatw[:,ix,iy] = fw[:]/self.kick
                        mu = np.dot(self.muvec[x,y,:],axis[:])/axmag
                        for it in range(nt):
                            resp[it,ix,iy] = -8.0*freqs[it]*mu*dmatw[it,ix,iy].imag
                            resptot[it] += resp[it,ix,iy]
                            #wia[it,ix,iy] = 2.0*np.sign(mu)*dmatw[it,ix,iy].imag

#               Normalize the strength function
                
                sumresptot = max(sum(resptot[0:npos])*delw,thresh)
                nel = sum(self.wt)
                resp = resp*nel/sumresptot
                resptot = resptot*nel/sumresptot

                for it in range(nt):
                    wia[it,:,:] = resp[it,:,:]/max(resptot[it],thresh)

                return freqs, dmatw, resp, wia, resptot

        def write_dmat(self,t,dmat,aocc,auocc,fp):

                ## Writes complex dmat type matrices through their absolute values
		
                (nt, nx, ny) = dmat.shape

                fp.write("%d %d %d %d\n" %(nt, self.nocc, nx, ny))
                for en in aocc:
                         fp.write("%10.6f " %(en))
                fp.write("\n")
                for en in auocc:
                        fp.write("%10.6f " %(en))
                fp.write("\n")

                for it in range(nt):
                    fp.write("%10.6f " %(t[it]))
                    for ix in range(nx):
                        for iy in range(ny):
                            fp.write("%10.6f " %(abs(dmat[it,ix,iy])))
                    fp.write("\n")

                return

        def write_dmatr(self,t,dmat,aocc,auocc,fp):

                ## Writes real dmat type matrices through their actual values

                (nt, nx, ny) = dmat.shape

                fp.write("%d %d %d %d\n" %(nt, self.nocc, nx, ny))
                for en in aocc:
                         fp.write("%10.6f " %(en))
                fp.write("\n")
                for en in auocc:
                        fp.write("%10.6f " %(en))
                fp.write("\n")

                for it in range(nt):
                    fp.write("%10.6f " %(t[it]))
                    for ix in range(nx):
                        for iy in range(ny):
                            fp.write("%10.6f " %(dmat[it,ix,iy]))
                    fp.write("\n")

                return
