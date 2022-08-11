
import sys
import math
import argparse
import numpy as np

def compute_fft(ifname: str,
                pre_process_zero:bool=False,
                damping:float = None,
                padding:int = None):
    
    ## Read in raw data t, f(t) from file (1st command line arg)
    data = np.loadtxt(ifname)
    t = data[:,0]
    f = data[:,1]

    ##
    ## Optional preprocessing of time signal
    ##
    ## (zero at t=0)
    if pre_process_zero:
        f0 = f[0]
        f = f - f0


    ## (exponential damping)
    if damping:
        damp = np.exp(-(t-t[1]) / damping)
        f = f * damp


    ## (zero padding)
    if padding:
        zeros = np.linspace(0.0, 0.0, padding)
        f = [f, zeros[:]]

    ##
    ## Do FFT, compute frequencies, and print to stdout: w, Re(fw), Im(fw),
    ## Abs(fw). Note we only print the positive frequencies (first half of
    ## the data)--this is fine since time signal is pure real so the
    ## negative frequencies are the Hermitian conjugate of the positive
    ## frequencies.
    ##

    fw = np.fft.fft(f)

    n = np.shape(f)[0]     #this includes padding

    dt = t[2] - t[1]   #assumes constant time step XXX no safety checks

    period = (n-1)*dt - t[0]

    dw = 2.0 * np.pi / period

    m = n // 2

    wmin = 0.0
    wmax = m*dw

    fw_pos = fw[0:m]              #FFT values of positive frequencies (first half of output array)
    fw_re = np.real(fw_pos)
    fw_im = np.imag(fw_pos)
    fw_abs = abs(fw_pos)

    w = np.linspace(wmin, wmax, m)  #positive frequency list

    return np.stack((w, fw_re, fw_im, fw_abs)).T

def rotate_spectrum (data):
    for v in data:
        w = v[0]
        re = v[1]
        im = v[2]
        ab = v[3]
        
        r = math.sqrt (re**2 + im**2)
        if abs (r - ab) > 1e-5:
            raise Exception ("abs not equal to sqrt(re^2 + im^2)")

        angle = abs (math.atan2 (im, re))

        if angle > math.pi:
            raise Exception ("atan2 out of range")

        re_out = ab * math.cos (angle)
        im_out = ab * math.sin (angle)

        yield [w, re_out, im_out, ab]

        
def photoabsorption_spectrum(dipole_file, spectrum_file,  process_zero=False, damping=None,padding=None):

    data = compute_fft(dipole_file, process_zero, damping,padding)
    data_rot = rotate_spectrum (data)
    with open(spectrum_file,"w+") as f:
        f.write("#Energy(eV)\tosc\tnorm\n")
        for d in data_rot:
            f.write("%20.10e\t%20.10e\t%20.10e\n" %(d[0] * 27.2114, d[0] * d[2], d[3])) 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ifile", help='time dependent dipole momment data file')
    parser.add_argument("ofile", help='output spectrum file name')
    parser.add_argument("--process_zero", help='zero time signal at t=0 ', action='store_true')
    parser.add_argument("-d",'--damping', help=' damp by exp(-t/tau) before FFT same time units as input', type=float)
    parser.add_argument("-p",'--padding', help='add this many points to time signal before FFT', type=int)
    args = parser.parse_args()

    photoabsorption_spectrum(args.ifile, args.ofile, args.process_zero, args.damping, args.padding)


if __name__ == '__main__':
    main()