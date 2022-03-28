import numpy as np
import argparse

def compute_spec(ifname: str,
                ofname: str,
                pre_process_zero:bool=False,
                damping:float = None,
                padding:int = None):
    
    ## Read in raw data t, f(t) from file (1st command line arg)
    data = np.loadtxt(ifname)
    t = data [:,0]
    f = data [:,1]

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

    w = np.linspace (wmin, wmax, m)  #positive frequency list


    fmt = '%12.6f %20.10e %20.10e %20.10e'
    header = '{:^10} {:^20} {:^20} {:^20}'.format('frequency', 'real part',
                                            'imaginary part', 'absolute value')
    np.savetxt(ofname, np.stack((w,  fw_re, fw_im, fw_abs)).T,
                fmt=fmt, header=header)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ifile", help='time dependent dipole momment data file')
    parser.add_argument("ofile", help='output file name')
    parser.add_argument("--process_zero", help='zero time signal at t=0 ', action='store_true')
    parser.add_argument("-d",'--damping', help=' damp by exp(-t/tau) before FFT same time units as input', type=float)
    parser.add_argument("-p",'--padding', help='add this many points to time signal before FFT', type=int)
    args = parser.parse_args()

    compute_spec(args.ifile, args.ofile, args.process_zero, args.damping, args.padding)

if __name__ == '__main__':
    main()