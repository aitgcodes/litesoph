from litesoph.post_processing.mo_population import calc_population_diff, create_states_index, get_occ_unocc
from litesoph.simulations.esmd import InputError, Task, TaskFailed, TaskNotImplementedError, assemable_job_cmd
from .gpaw_input import gpaw_create_input
from litesoph.utilities.plot_spectrum import plot_multiple_column, plot_spectrum
from litesoph.lsio.IO import write2file
from pathlib import Path
import numpy as np
from litesoph.utilities.units import autime_to_eV, au_to_as

gpaw_data = {
'ground_state' : {'inp':'gpaw/GS/gs.py',
            'req' : ['coordinate.xyz'],
            'dir' : 'GS',
            'file_name' : 'gs',
            'out_log': 'gpaw/GS/gs.out',
            'restart': 'gpaw/GS/gs.gpw',
            'check_list':['Converged', 'Fermi level:','Total:']},

'rt_tddft_delta' : {'inp':'gpaw/TD_Delta/td.py',
        'req' : ['gpaw/GS/gs.gpw'],
        'dir' : 'TD_Delta',
        'file_name' : 'td',
        'out_log': 'gpaw/TD_Delta/td.out',
        'restart': 'gpaw/TD_Delta/td.gpw',
        'check_list':['Writing','Total:']},

'rt_tddft_laser': {'inp':'gpaw/TD_Laser/td.py',
        'req' : ['gpaw/GS/gs.gpw'],
        'dir' : 'TD_Laser',
        'file_name' : 'td',
        'out_log': 'gpaw/TD_Laser/td.out',
        'restart': 'gpaw/TD_Laser/td.gpw',
        'check_list':['Writing','Total:']},

'spectrum' : {'inp':'gpaw/Spectrum/spec.py',
        'req' : ['gpaw/TD_Delta/dm.dat'],
        'dir': 'Spectrum',
        'file_name' : 'spec',
        'out_log': 'gpaw/Spectrum/spec.dat',
        'restart': 'gpaw/TD_Delta/dm.dat',
        'check_list':['FWHM'],
        'spectra_file': ['gpaw/Spectrum/spec_x.dat','gpaw/Spectrum/spec_y.dat', 'gpaw/Spectrum/spec_z.dat' ]},

'tcm' : {'inp':'gpaw/TCM/tcm.py',
        'req' : ['gpaw/GS/gs.gpw','gpaw/TD_Delta/wf.ulm'],
        'out_log': 'gpaw/TCM/unocc.out',
        'dir': 'TCM',
        'file_name' : 'tcm',
        'restart': '',
        'check_list':['Writing','Total:']},

'mo_population':{'inp':'nwchem/mo_population/mo_population.py',
                            'out_log' : ' ',
                            'file_name':'mo_pop',
                            'req' : ['gpaw/GS/gs.gpw','gpaw/TD_Delta/wf.ulm'],
                            'dir': 'mo_population'},
'masking': {'dir' : 'masking',
            'req' : ['gpaw/TD_Laser/dm.dat']}
}

class GpawTask(Task):

    NAME = 'gpaw'

    simulation_tasks =  ['ground_state', 'rt_tddft_delta', 'rt_tddft_laser']
    post_processing_tasks = ['spectrum', 'tcm', 'mo_population', 'masking']
    implemented_task = simulation_tasks + post_processing_tasks

    def __init__(self, project_dir, lsconfig, status, **kwargs) -> None:
        
        self.task_name = kwargs.get('task', 'ground_state')
        self.user_input = kwargs
        self.engine_log = None
        self.output = {}
        if not self.task_name in self.implemented_task: 
            raise TaskNotImplementedError(f'{self.task_name} is not implemented.')
        self.task_data = gpaw_data.get(self.task_name)
        super().__init__('gpaw', status, project_dir, lsconfig)
        self.setup_task(self.user_input)

    def setup_task(self, param):
        infile_ext = '.py'
        self.task_dir = self.project_dir / 'gpaw' / self.task_data.get('dir')
        input_filename = self.task_data.get('file_name', None)
        self.network_done_file = self.task_dir / 'Done'

        if self.task_name in self.simulation_tasks:
            self.engine_log = self.project_dir / self.task_data.get('out_log')
            
        if input_filename:
            self.input_filename = input_filename + infile_ext
        
            param['txt_out'] = input_filename + '.out'
            param['gpw_out'] =  input_filename + '.gpw'

        if 'ground_state' in self.task_name:
            param['geometry'] = str(self.project_dir / 'coordinate.xyz')
            return
        
        if 'rt_tddft' in self.task_name:
            param['gfilename'] = str(self.project_dir /  gpaw_data['ground_state'].get('restart'))
            param['dm_file'] = 'dm.dat'
            if 'ksd' in param or 'mo_population' in param:
                param['wfile'] = 'wf.ulm'
            update_td_input(param)
            return

        if 'spectrum' == self.task_name:
            param['dm_file'] = str(self.project_dir / self.task_data.get('req')[0])
            self.pol = get_polarization_direction(self.status)
            param['spectrum_file'] = spec_file = f'spec_{self.pol[1]}.dat'
            update_spectrum_input(param)
            self.spec_file = self.task_dir / spec_file
            return

        if 'tcm' == self.task_name:
            param['gfilename'] = str(self.project_dir /  self.task_data.get('req')[0])
            param['wfile'] = str(self.project_dir / self.task_data.get('req')[1])
            return

        if 'mo_population' ==self.task_name:
            gs_log = str(self.project_dir / gpaw_data['ground_state'].get('out_log'))
            gs_file = str(self.project_dir /  self.task_data.get('req')[0])
            param['gfilename'] = gs_file
            param['wfile'] = str(self.project_dir / self.task_data.get('req')[1])
            param['mopop_file'] = mo_pop_file ='mo_population.dat'
            self.mo_populationfile = self.task_dir / mo_pop_file
            data = get_eigen_energy(gs_log)
            self.occupied_mo , self.unoccupied_mo = get_occ_unocc(data,energy_col=1,occupancy_col=2)
            return

        if 'masking' == self.task_name:
            
            self.sim_total_dm = self.project_dir / self.task_data.get('req')[0]
            self.state_mask_dm = False
            from litesoph.post_processing.masking_utls import MaskedDipoleAnaylsis
            self.masked_dm_analysis = MaskedDipoleAnaylsis(self.sim_total_dm, self.task_dir)

    def write_input(self, template=None):
        if template:
            self.template = template
        self.create_directory(self.task_dir)
        write2file(self.task_dir,self.input_filename,self.template)

    def create_template(self):
        self.template = gpaw_create_input(**self.user_input)
    
    def read_results(self):
        if self.task_name in self.simulation_tasks:
            self.engine_log = self.project_dir / self.task_data.get('out_log')

    def create_job_script(self, np=1, remote_path=None) -> list:

        python_path = self.lsconfig['programs'].get('python', 'python3')
        job_script = super().create_job_script()
        self.engine_log = self.project_dir / self.task_data.get('out_log')
        engine_cmd = ' ' + str(self.input_filename)
 
        if remote_path:
            python_path = 'python3'
            engine_cmd = python_path + engine_cmd
            rpath = Path(remote_path) / self.task_dir.relative_to(self.project_dir.parent)
            job_script = assemable_job_cmd(engine_cmd, np, cd_path= str(rpath),
                                            remote=True, module_load_block=self.get_engine_network_job_cmd())
        else:
            engine_cmd = python_path + engine_cmd
            job_script = assemable_job_cmd(engine_cmd, np, cd_path=str(self.task_dir),
                                            mpi_path=self.mpi_path)
    
        self.job_script = job_script
        return self.job_script

    def prepare_input(self):
        assert self.task_name != 'masking'
        self.create_template()
        self.write_input()
        
        self.create_job_script()
        self.write_job_script()

    def get_engine_log(self):
        self.engine_log = self.project_dir / self.task_data.get('out_log')
        if self.check_output():
            return self.read_log(self.engine_log)


    def run_job_local(self, cmd):
        assert self.task_name != 'masking'
        self.write_job_script(self.job_script)
        try:
            super().run_job_local(cmd)
        except Exception:
            raise
        else:
            if self.task_name == 'mo_population':
                self.mo_population_diff_file = self.task_dir / 'mo_population_diff.dat'
                calc_population_diff(homo_index=len(self.occupied_mo), infile=self.mo_populationfile,
                                        outfile=self.mo_population_diff_file)
    def extract_masked_dm(self):
        self.create_directory(self.task_dir)
        self.state_mask_dm = True
        self.masked_dm_analysis.extract_dipolemoment_data()


    def get_energy_coupling_constant(self, **kwargs) -> str:
        if not self.state_mask_dm:
            self.extract_masked_dm()
        region = kwargs.get('region')
        axis = kwargs.get('direction')
        return self.masked_dm_analysis.get_energy_coupling(region, axis)


    def plot(self, **kwargs):
        if self.task_name == 'spectrum':
            img = self.spec_file.with_suffix('.png')
            plot_spectrum(str(self.spec_file),str(img),0, self.pol[0]+1, "Energy (in eV)", "Strength(in /eV)",xlimit=(self.user_input['e_min'], self.user_input['e_max']))
    
        if self.task_name == 'tcm':
            from PIL import Image        
            for item in self.user_input.get('frequency_list'):
                img_file = self.task_dir / f'tcm_{item:.2f}.png'
                image = Image.open(img_file)
                image.show()

        elif self.task_name == 'mo_population':
            occ = self.occupied_mo
            unocc = self.unoccupied_mo
            below_homo = kwargs.get('num_occupied_mo_plot',1)
            above_lumo = kwargs.get('num_unoccupied_mo_plot',1)
            if (len(occ) < below_homo) or (len(unocc) < above_lumo):
                raise InputError(f'The selected MO is out of range. Number of MO: below HOMO = {len(occ)}, above_LUMO = {len(unocc)}')
            homo_index = len(occ)
            column_range = (homo_index-below_homo+1, homo_index+above_lumo)
            legend_dict = create_states_index(num_below_homo=below_homo, num_above_lumo=above_lumo, homo_index=homo_index)
            
            pop_data = np.loadtxt(self.mo_population_diff_file)
            
            plot_multiple_column(pop_data, column_list=column_range, column_dict=legend_dict, xlabel='Time (as)')

        elif self.task_name == 'masking':
            if not self.state_mask_dm:
                self.extract_masked_dm()
            region = kwargs.get('region')
            axis = kwargs.get('direction')
            envelope = kwargs.get('envelope', False)
            plt = self.masked_dm_analysis.plot(region, axis, envelope=envelope)
            plt.show()
            
    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of GPAW 

##eval "$(conda shell.bash hook)"
##conda activate <environment name>"""
        return job_script

def get_polarization_direction(status):
    param = status.get('gpaw.rt_tddft_delta.param')
    pol = param['polarization']
    return get_direction(pol)

def get_direction(direction:list):
    pol_map = {'0' : 'x', '1' : 'y', '2': 'z'}
    index = direction.index(1)
    return index , pol_map[str(index)]

def update_td_input(param):
    if 'laser' in param:
        sigma = param['laser'].get('sigma')
        time0 = param['laser'].get('time0')
        param['laser']['sigma'] = round(autime_to_eV/sigma, 2)
        param['laser']['time0'] = round(time0 * au_to_as, 2)
    else:
        param['absorption_kick'] = [ p * param['strength'] for p in param['polarization']]
    
    param['propagate'] = (param['time_step'], param['number_of_steps'])
    param['analysis_tools'] = tools = []

    properties = param.get('properties', None)

    if properties:
        if 'spectrum' in properties:
            tools.append('dipole')
        if 'ksd' in properties or 'mo_population' in properties:
            tools.append('wavefunction')

def update_spectrum_input(param):

    if 'folding' not in param:
        param['folding'] = 'Gauss'
    
    if 'width' not in param:
        param['width'] = 0.2123

def get_eigen_energy(td_out_file):


        labels = ['Band','Eigenvalues', 'Occupancy']
        with open(td_out_file, 'r') as f:
            lines = f.readlines()

        data = []
        check = False
        for line in lines:

            if all([tag in line for tag in labels]):
                check = True
                continue

            if check:
                vals = line.strip().split()
                if not vals:
                    break
                data.append([float(val) for val in vals])
        return data
