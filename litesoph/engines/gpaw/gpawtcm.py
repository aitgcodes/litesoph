class TCMGpaw:

    def __init__(self, gfilename, wfilename, frequencies:list, name:str) -> None:
        self.gfilename = gfilename
        self.wfilename = wfilename
        self.frequencies = frequencies
        self.name = name

    def create_frequency_density_matrix(self):
        #fdm_filename = fdm_filename + ".ulm"
        from gpaw.lcaotddft import LCAOTDDFT
        from gpaw.lcaotddft.densitymatrix import DensityMatrix
        from gpaw.lcaotddft.frequencydensitymatrix import FrequencyDensityMatrix
        from gpaw.tddft.folding import frequencies

        td_calc = LCAOTDDFT(self.gfilename)

        dmat = DensityMatrix(td_calc)
        freqs = frequencies(self.frequencies, 'Gauss', 0.1)
        fdm = FrequencyDensityMatrix(td_calc, dmat, frequencies=freqs)

        td_calc.replay(name=self.wfilename, update='none')

        fdm.write('fdm.ulm')
        return fdm
        
    def read_unocc(self):
        from gpaw import GPAW
        calc = GPAW(self.gfilename, txt=None)
        return calc

    def cal_unoccupied_states(self,calc):
        calc = calc.fixed_density(nbands='nao', txt='unocc.out')
        calc.write('unocc.gpw', mode='all')
        return calc
    
    def create_ks_basis(self, calc):
        from gpaw.lcaotddft.ksdecomposition import KohnShamDecomposition
        ksd = KohnShamDecomposition(calc)
        ksd.initialize(calc)
        ksd.write('ksd.ulm')
        return ksd

    def plot_tcm(self, ksd, fdm,fnum, title):
        import numpy as np
        from matplotlib import pyplot as plt
        from gpaw.tddft.units import au_to_eV
        from gpaw.lcaotddft.tcm import TCMPlotter

        rho_uMM = fdm.FReDrho_wuMM[fnum]
        freq = fdm.freq_w[fnum]
        frequency = freq.freq * au_to_eV

        rho_up = ksd.transform(rho_uMM)

        dmrho_vp = ksd.get_dipole_moment_contributions(rho_up)
        weight_p = 2 * freq.freq / np.pi * dmrho_vp[0].imag / au_to_eV * 1e5

        de = 0.01
        energy_o = np.arange(-3, 0.1 + 1e-6, de)
        energy_u = np.arange(-0.1, 3 + 1e-6, de)
        plt.clf()
        plotter = TCMPlotter(ksd, energy_o, energy_u, sigma=0.1)
        plotter.plot_TCM(weight_p)
        plotter.plot_DOS(fill={'color': '0.8'}, line={'color': 'k'})
        plotter.plot_TCM_diagonal(freq.freq * au_to_eV, color='k')
        plotter.set_title(f'Photoabsorption TCM of {title} at {frequency:.2f} eV')

        # Check that TCM integrates to correct absorption
        tcm_ou = ksd.get_TCM(weight_p, ksd.get_eig_n()[0],
                            energy_o, energy_u, sigma=0.1)
        print(f'TCM absorption: {np.sum(tcm_ou) * de ** 2:.2f} eV^-1')
        plt.savefig(f'tcm_{frequency:.2f}.png')
    
    def run(self):
        self.fdm = self.create_frequency_density_matrix()
        self.calc = self.read_unocc()
        self.calc = self.cal_unoccupied_states(self.calc)
        self.ksd = self.create_ks_basis(self.calc)    

    def plot(self):
        for fnum in range(len(self.frequencies)):
            self.plot_tcm(self.ksd, self.fdm, fnum, self.name)
