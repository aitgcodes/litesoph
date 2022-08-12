import pathlib
from pathlib import Path

from litesoph import config
from litesoph.post_processing.mo_population import get_energy_window, get_occ_unocc
from litesoph.simulations.esmd import InputError, Task, TaskFailed, TaskNotImplementedError
from litesoph.simulations.nwchem.nwchem import NWChem
from litesoph.simulations.nwchem.spectrum import photoabsorption_spectrum
from litesoph.post_processing.mo_population_correlation.moocc_correlation_plot import plot_mo_population_correlations
from litesoph.post_processing import mo_population_correlation
from litesoph.utilities.plot_spectrum import plot_spectrum

xc = {
            'B3LYP'     :'xc b3lyp',
            'PBE0'      :'xc pbe0',
            'PBE96'     :'xc xpbe96 cpbe96',
            'BHLYP'     :'xc bhlyp',
            'PW91'      :'xc xperdew91 perdew91',
            'BP86'      :'xc becke88 perdew86',
            'BP91'      :'xc becke88 perdew91',
            'BLYP'      :'xc becke88 lyp',
            'M05'       :'xc m05',
            'M05-2X'    :'xc m05-2x',
            'M06'       :'xc m06',
            'M06-HF'    :'xc m06-hf',
            'M08-SO'    :'xc m08-so',
            'M11'       :'xc m11',
            'CAM-B3LYP' :'xc xcamb88 1.00 lyp 0.81 vwn_5 0.19 hfexch 1.00 \n cam 0.33 cam_alpha 0.19 cam_beta 0.46',
            'LC-BLYP'   :'xc xcamb88 1.00 lyp 1.0 hfexch 1.00 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
            'LC-PBE'    :'xc xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.0 cam_beta 1.0',
            'LC-wPBE'   :'xc xwpbe 1.00 cpbe96 1.0 hfexch 1.00 \n cam 0.4 cam_alpha 0.00 cam_beta 1.00',
            'CAM-PBE0'  :'xc xcampbe96 1.0 cpbe96 1.0 HFexch 1.0 \n cam 0.30 cam_alpha 0.25 cam_beta 0.75',
            'rCAM-B3LYP':'xc xcamb88 1.00 lyp 1.0 vwn_5 0. hfexch 1.00 becke88 nonlocal 0.13590 \n cam 0.33 cam_alpha 0.18352 cam_beta 0.94979',
            'HSE03'     :'xc xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.33 cam_alpha 0.0 cam_beta 1.0',
            'HSE06'     :'xc xpbe96 1.0 xcampbe96 -0.25 cpbe96 1.0 srhfexch 0.25 \n cam 0.11 cam_alpha 0.0 cam_beta 1.0',
}

nwchem_data = {
'ground_state' : {'inp':'nwchem/GS/gs.nwi',
            'out_log' : 'nwchem/GS/gs.nwo',
            'dir' : 'GS',
            'file_name':'gs',
            'req' : ['coordinate.xyz', 'nwchem/restart'],            
            'check_list':['Converged', 'Fermi level:','Total:']},

'rt_tddft_delta' : {'inp':'nwchem/TD_Delta/td.nwi',
        'out_log' : 'nwchem/TD_Delta/td.nwo',
        'dir' : 'TD_Delta',
        'file_name' : 'td',
        'req' : ['coordinate.xyz', 'nwchem/restart'],
        'check_list':['Converged', 'Fermi level:','Total:']},

'rt_tddft_laser' : {'inp':'nwchem/TD_Laser/tdlaser.nwi',
        'out_log' : 'nwchem/TD_Laser/tdlaser.nwo',
        'dir' : 'TD_Laser',
        'file_name': 'tdlaser',
        'req' : ['coordinate.xyz', 'nwchem/restart'],
        'check_list':['Converged', 'Fermi level:','Total:']},

'spectrum' : {'inp':'nwchem/TD_Delta/td.nwi',
        'out_log' : 'nwchem/TD_Delta/td.nwo',
        'dir' : 'spectrum',
        'req' : ['nwchem/TD_Delta/td.nwo'],
        'spectra_file': ['nwchem/Spectrum/spec_x.dat','nwchem/Spectrum/spec_y.dat', 'nwchem/Spectrum/spec_z.dat' ],
        'spec_dir_path' : 'nwchem/Spectrum',
        'check_list':['Converged', 'Fermi level:','Total:']},

'mo_population_correlation':{'inp':'nwchem/TD_Delta/td.nwi',
                            'out_log' : 'nwchem/TD_Delta/td.nwo',
                             'req' : ['nwchem/TD_Delta/td.nwo'],
                            'dir': 'mo_population'},
'restart': 'nwchem/restart'
}


class NwchemTask(Task):

    NAME = 'nwchem'
    simulation_task =  ['ground_state', 'rt_tddft_delta', 'rt_tddft_laser']
    post_processing_task = ['spectrum', 'mo_population_correlation']
    implemented_task = simulation_task + post_processing_task

    def __init__(self, project_dir, lsconfig, status=None, **kwargs) -> None:
        
        
        self.task_name = kwargs.pop('task', 'ground_state')
        
        
        if not self.task_name in nwchem_data.keys(): 
            raise TaskNotImplementedError(f'{self.task_name} is not implemented.')

        self.task_data = nwchem_data.get(self.task_name)
        super().__init__('nwchem',status, project_dir, lsconfig)
        self.user_input = kwargs
        self.create_engine(self.user_input)
    
    def create_engine(self, param):

        infile_ext = '.nwi'
        outfile_ext = '.nwo'
        self.task_dir = self.project_dir / 'nwchem' / self.task_data.get('dir')
        label = str(self.project_dir.name)
        file_name = self.task_data.get('file_name')
        
        if self.task_name in self.post_processing_task:
            completed_task = self.status.get_status('nwchem').keys()
            if 'rt_tddft_laser' in completed_task:
                td_out = nwchem_data['rt_tddft_laser'].get('out_log')
            else:
                td_out = nwchem_data['rt_tddft_delta'].get('out_log')

            self.outfile = self.project_dir / td_out 
            

            self.nwchem = NWChem(outfile=str(self.outfile), 
                            label=label, directory=self.task_dir)
            return

        param['perm'] = str(self.task_dir.parent / 'restart')
        param['geometry'] = str(self.project_dir / 'coordinate.xyz')
        
        if 'rt_tddft' in self.task_name:
            param['restart_kw'] = 'restart'
            param['basis'] = self.status.get_status('nwchem.ground_state.param').get('basis')
        
        file_name = self.task_data.get('file_name')
        self.infile = file_name + infile_ext
        self.outfile = file_name + outfile_ext
        self.nwchem = NWChem(infile= self.infile, outfile=self.outfile, 
                            label=label, directory=self.task_dir, **param)

    def write_input(self, template=None):
        self.create_directory(self.task_dir)
        self.nwchem.write_input(template)

    def create_template(self):
        self.template = self.nwchem.create_input()

    def _create_spectrum_cmd(self, remote=False ):

        td_out = self.outfile

        self.pol, tag = get_pol_and_tag(self.status)

        if  not td_out.exists():
            raise FileNotFoundError(f' Required file {td_out} doesnot exists!')
            
        path = pathlib.Path(__file__)

        if remote:
            path_python = 'python3'
        else:
            path_python = self.lsconfig.get('programs', 'python')

        nw_rtparse = str(path.parent /'nwchem_read_rt.py')
        spectrum_file = str(path.parent / 'spectrum.py')
        
        dm_cmd = f'{path_python} {nw_rtparse} -x dipole -p {self.pol} -t {tag} {td_out} > {self.pol}.dat'

        spec_cmd = f'{path_python} {spectrum_file} dipole.dat spec_{self.pol}.dat'
        
        return [spec_cmd]

    def compute_spectrum(self):
        self.create_directory(self.task_dir)
        
        td_out = self.outfile

        self.pol, tag = get_pol_and_tag(self.status)
        self.dipole_file = self.task_dir / 'dipole.dat'
        self.spectra_file = self.task_dir / f'spec_{self.pol}.dat'
        try:
            self.nwchem.get_td_dipole(self.dipole_file, td_out, tag, polarization=self.pol)
        except Exception:
            raise
        #else:
        #    photoabsorption_spectrum(self.dipole_file, self.spectra_file,)

    def compute_mo_population_correlation(self):
        
        self.below_homo = below_homo = self.user_input['num_occupied_mo']
        self.above_lumo = above_lumo = self.user_input['num_unoccpied_mo']
        bandpass_window = self.user_input['bandpass_window']
        hanning_window = self.user_input['hanning_window']

        self.create_directory(self.task_dir)
        td_out = self.outfile

        energy_file = self.task_dir / 'energy_format.dat'
        eigen_data = self.nwchem.get_eigen_energy(td_out)
        occ, unocc = get_occ_unocc(eigen_data)
        if (len(occ) < below_homo) or (len(unocc) < above_lumo):
            raise InputError(f'The selected MO is out of range. Number of MO: below HOMO = {len(occ)}, above_LUMO = {len(unocc)}')
        mo_population_file = self.task_dir / 'mo_population.dat'
        self.nwchem.get_td_moocc(str(mo_population_file), td_out, homo_index=len(occ),
                                     below_homo=below_homo, above_lumo=above_lumo)
        get_energy_window(eigen_data, energy_file, below_homo, above_lumo)
    
        path = pathlib.Path(mo_population_correlation.__file__)
        
        pop_py = str(path.parent /'population_correlation.py')
        pop_cmd = f'python {pop_py} {below_homo} {energy_file}'    
        
        band_py = str(path.parent / 'bandpass.py')
        band_cmd = f'python {band_py} {mo_population_file} {bandpass_window}'       
        
        hann_py = str(path.parent / 'test.py')
        hann_cmd = f'python {hann_py} frest.dat hanning {hanning_window}'
        
        dft_mod_py = str(path.parent /'dft-mod.py')
        dft_mod_cmd = f'python {dft_mod_py} fn_rest.dat'

        return [band_cmd, hann_cmd, dft_mod_cmd, pop_cmd]

    def create_job_script(self, np=1, remote_path=None, remote=None) -> list:

        job_script = super().create_job_script()

        if 'spectrum' in self.task_name:
            
           # self.create_directory(self.task_dir)
            path = self.task_dir
            #if remote_path:
            #    path = Path(remote_path) / self.task_dir.relative_to(self.project_dir.parent)
            self.compute_spectrum()
            job_script.append(f"cd {str(path)}")
            job_script.extend(self._create_spectrum_cmd(bool(remote_path)))
            self.job_script = "\n".join(job_script)
            self.write_job_script()
            return 

        if self.task_name == 'mo_population_correlation':
            print('here')
            job_script.append(f"cd {str(self.task_dir)}")
            job_script.extend(self.compute_mo_population_correlation())
            self.job_script = "\n".join(job_script)
            self.write_job_script()
            return 

        ifilename =  self.infile
        ofilename = self.outfile
        command = self.lsconfig.get('engine', 'nwchem')

        if remote_path:
            path = Path(remote_path) / self.task_dir.relative_to(self.project_dir.parent)
            job_script.append(self.get_engine_network_job_cmd())
            job_script.append(f"cd {str(path)}")
            job_script.append(f"mpirun -np {np:d}  nwchem {str(ifilename)} > {str(ofilename)}")
            job_script.append(self.remote_job_script_last_line)       
        else:
            job_script.append(f"cd {str(self.task_dir)}")

            path_nwchem = self.lsconfig.get('engine', 'nwchem')
            if not path_nwchem:
                path_nwchem = 'nwchem'
            command = path_nwchem + ' ' + str(ifilename) + ' ' + '>' + ' ' + str(ofilename)
            if np > 1:
                cmd_mpi = config.get_mpi_command(self.NAME, self.lsconfig)
                command = cmd_mpi + ' ' + '-np' + ' ' + str(np) + ' ' + command
            job_script.append(command)

        self.job_script = "\n".join(job_script)
        return self.job_script
    
    def prepare_input(self):

        if self.task_name in self.simulation_task:
            self.create_template()
            self.write_input()
        
        self.create_job_script()
            

    def run_job_local(self, cmd):
        super().run_job_local(cmd)

    def get_engine_log(self):

        if self.read_output():
            with open(self.task_dir / self.outfile, 'r') as f:
                text = f.read()      
            return text

    def read_output(self):
        try:
            exist_status, stdout, stderr = self.local_cmd_out
        except AttributeError:
            TaskFailed("Job not completed.")
            return
        else:
            return True

    def plot(self,**kwargs):

        if self.task_name == 'spectrum':
            img = self.spectra_file.parent / f"spec_{self.pol}.png"
            plot_spectrum(self.spectra_file,img,0, 1, "Energy(eV)","Strength",xlimit=(self.user_input['e_min'], self.user_input['e_max']))

        elif self.task_name == 'mo_population_correlation':
            pop_corr_file = self.task_dir / 'amp_file.dat'
            plot_mo_population_correlations(pop_corr_file,self.below_homo, self.above_lumo,
                                            divisions=kwargs['ngrid'], sigma=kwargs['broadening'])
    
    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of NWCHEM or load the module

#eval "$(conda shell.bash hook)"
#conda activate <environment name>

#module load nwchem"""
        return job_script


def get_pol_and_tag(status):

    param =  status.get_status('nwchem.rt_tddft_delta.param')
    pol = param['rt_tddft']['field'].get('polarization', 'x')
    tag = param['rt_tddft'].get('tag', 'rt_tddft')
    return pol, tag
