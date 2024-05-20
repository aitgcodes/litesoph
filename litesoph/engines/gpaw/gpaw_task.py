import copy
from typing import Any, List, Dict, Union
from litesoph.common.utils import get_new_directory
from litesoph.post_processing.mo_population import calc_population_diff, create_states_index, get_occ_unocc
from litesoph.common.task import (InputError, Task, TaskFailed ,
                                     TaskNotImplementedError, assemable_job_cmd, write2file)
from litesoph.common.task_data import TaskTypes as tt 
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.engines.gpaw.gpaw_input import gpaw_create_input, default_param
from litesoph.visualization.plot_spectrum import plot_multiple_column, plot_spectrum
from litesoph.engines.gpaw.task_data import gpaw_gs_param_data
from pathlib import Path
import numpy as np
from litesoph.utilities.units import autime_to_eV, au_to_as

gpaw_data = {
tt.GROUND_STATE : {'inp':'gpaw/GS/gs.py',
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

tt.RT_TDDFT : {'file_name' : 'td',
        'output': {'out_log': 'td.out',
                    'gpw_out': 'td.gpw'}},

'rt_tddft_laser': {'inp':'gpaw/TD_Laser/td.py',
        'req' : ['gpaw/GS/gs.gpw'],
        'dir' : 'TD_Laser',
        'file_name' : 'td',
        'out_log': 'gpaw/TD_Laser/td.out',
        'restart': 'gpaw/TD_Laser/td.gpw',
        'check_list':['Writing','Total:']},

tt.COMPUTE_SPECTRUM : {'inp':'gpaw/Spectrum/spec.py',
        'req' : ['gpaw/TD_Delta/dm.dat'],
        'dir': 'Spectrum',
        'file_name' : 'spec',
        'out_log': 'gpaw/Spectrum/spec.dat',
        'restart': 'gpaw/TD_Delta/dm.dat',
        'check_list':['FWHM'],
        'spectra_file': ['gpaw/Spectrum/spec_x.dat','gpaw/Spectrum/spec_y.dat', 'gpaw/Spectrum/spec_z.dat' ]},

tt.TCM : {'inp':'gpaw/TCM/tcm.py',
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

    simulation_tasks =  [tt.GROUND_STATE, tt.RT_TDDFT]
    post_processing_tasks = [tt.COMPUTE_SPECTRUM, tt.TCM, tt.MO_POPULATION, tt.MASKING]
    implemented_task = simulation_tasks + post_processing_tasks

    def __init__(self, lsconfig, 
                task_info: TaskInfo, 
                dependent_tasks: Union[List[TaskInfo],None]= None
                ) -> None:
        
        super().__init__(lsconfig, task_info, dependent_tasks)

        self.task_data = gpaw_data.get(self.task_name)
        self.params = copy.deepcopy(self.task_info.param)
        
        self.relative_path = Path('../../')
        self.user_input = {}
        self.user_input['task'] = self.task_name
        if tt.GROUND_STATE == self.task_name:
            self.user_input.update(format_gs_input(self.params))
        else:
            self.user_input.update(self.params)

        if self.task_info.job_info.directory is None:
            task_dir = self.directory / 'gpaw' / self.task_name
            task_dir = get_new_directory(task_dir)
            self.task_info.job_info.directory = task_dir.relative_to(self.directory)

        self.task_dir = self.directory / self.task_info.job_info.directory
        self.task_info.local_copy_files.append(str(self.task_dir.relative_to(self.directory)))
        self.setup_task(self.user_input)
        
        

    def setup_task(self, param):
        infile_ext = '.py'
        input_filename = self.task_data.get('file_name', None)
        
        self.network_done_file = self.task_dir / 'Done'
        self.task_info.input['engine_input']={}
        
        
        if input_filename:
            self.input_filename = input_filename + infile_ext
        
            param['txt_out'] = input_filename + '.out'
            param['gpw_out'] =  input_filename + '.gpw'

            self.task_info.input['engine_input']['path'] = str(self.task_dir.relative_to(self.directory) / self.input_filename)
            self.task_info.output['txt_out'] = str(self.task_dir.relative_to(self.directory) / param['txt_out'])
            self.task_info.output['gpw_out'] = str(self.task_dir.relative_to(self.directory) / param['gpw_out'])

        if param.get('restart', False) and self.task_name in (tt.GROUND_STATE, tt.RT_TDDFT):
            nrestart = self.task_info.task_data.get('nrestart', 0)
            nrestart += 1
            param['txt_out'] = input_filename + '.out' + str(nrestart)
            self.task_info.output['txt_out'] = str(self.task_dir.relative_to(self.directory) / param['txt_out'])

        if tt.GROUND_STATE in self.task_name:
            geom_path = '../../coordinate.xyz'
            self.task_info.local_copy_files.append('coordinate.xyz')
            param['geometry'] = geom_path
            return
        
        if  tt.RT_TDDFT in self.task_name:
            
            if param.get('restart', False):
                param['gfilename'] = param['gpw_out']
                previous_steps = self.task_info.task_data.get('td_number_of_steps', 0)
                param['number_of_steps'] = param['number_of_steps'] - previous_steps 

            else:
                param['gfilename'] = str(Path.joinpath(self.relative_path, self.dependent_tasks[0].output.get('gpw_out')))
            
            self.task_info.task_data['td_number_of_steps'] = param.get('number_of_steps')
            # TODO: add dm files
            dm_list = ['dm.dat']
            num_masks = 0
            self.masked_dm_files = []
            lasers = param.get('laser', None)
            if lasers is not None:
                for i, laser in enumerate(lasers):
                    mask = laser.get('mask', None)
                    if mask is not None:
                        if isinstance(mask, dict):
                            num_masks += 1
                for i in range(num_masks):
                    dm_filename = 'dm_masked_'+ str(i+1)+'.dat' 
                    dm_list.append(dm_filename)     

            param['dm_files'] = dm_list
            # TODO: add dm files
            dm_files = []
            for i,dm in enumerate(dm_list):
                dm_rel_path = str(self.task_dir.relative_to(self.directory) / dm)
                dm_files.append(dm_rel_path)
            self.task_info.output['dm_files'] = dm_files
            # self.task_info.output['dm_file'] = str(self.task_dir.relative_to(self.directory) / param['dm_file'])
            
            if 'ksd' in param['properties'] or 'mo_population' in param['properties']:
                param['wfile'] = 'wf.ulm'
                self.task_info.output['wfile'] = str(self.task_dir.relative_to(self.directory) / param['wfile'])
            update_td_input(param)
            return

        if tt.TCM == self.task_name:

            param['gfilename'] = str(Path.joinpath(self.relative_path, self.dependent_tasks[0].output.get('gpw_out')))
            param['wfile'] = str(Path.joinpath(self.relative_path, self.dependent_tasks[1].output.get('wfile')))
            return

        if 'mo_population' ==self.task_name:

            gs_log = self.dependent_tasks[0].output.get('txt_out')
            gs_file = self.dependent_tasks[0].output.get('gpw_out')
            param['gfilename'] = str(Path.joinpath(self.relative_path,  gs_file))
            param['wfile'] = str(Path.joinpath(self.relative_path, self.dependent_tasks[1].output.get('wfile')))
            
            param['mopop_file'] = mo_pop_file ='mo_population.dat'
            self.mo_populationfile = self.task_dir / mo_pop_file
            
            self.task_info.output['mopop_file'] = str(self.task_dir.relative_to(self.directory) / mo_pop_file)
            data = get_eigen_energy(str(self.directory/gs_log))
            self.occupied_mo , self.unoccupied_mo = get_occ_unocc(data,energy_col=1,occupancy_col=2)
            return

    def create_template(self):
        template = gpaw_create_input(**self.user_input)
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = template

    def write_input(self):
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)
        
        infile = str(self.directory /self.task_info.input['engine_input']['path'])
        template = self.task_info.input['engine_input']['data']
        with open(infile , 'w+') as f:
            f.write(template)

    def read_results(self):
        if self.task_name in self.simulation_tasks:
            self.engine_log = self.directory / self.task_data.get('out_log')

    def create_job_script(self, np=1, remote_path=None) -> list:

        python_path = self.lsconfig['programs'].get('python', 'python3')
        job_script = super().create_job_script()
        engine_cmd = ' ' + str(self.input_filename)
 
        if remote_path:
            python_path = 'python3'
            engine_cmd = python_path + engine_cmd
            rpath = Path(remote_path) / self.task_dir.relative_to(self.directory.parent.parent)
            job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path= str(rpath),
                                            remote=True, module_load_block=self.get_engine_network_job_cmd())
        else:
            engine_cmd = python_path + engine_cmd
            job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path=str(self.task_dir),
                                            mpi_path=self.mpi_path)
    
        self.job_script = job_script
        return self.job_script

    def prepare_input(self):
        self.create_template()
        self.write_input()
        
        self.create_job_script()
        self.write_job_script()

    def get_engine_log(self):
        if self.check_output():
            return self.read_log(self.directory / self.task_info.output['txt_out'])
        

    def run_job_local(self, cmd):
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
   
    def plot(self, **kwargs):
    
        if self.task_name == tt.TCM:
            from PIL import Image        
            for item in self.user_input.get('frequency_list'):
                img_file = self.task_dir / f'tcm_{item:.2f}.png'
                image = Image.open(img_file)
                image.show()

        elif self.task_name == tt.MO_POPULATION:
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

    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of GPAW 

##eval "$(conda shell.bash hook)"
##conda activate <environment name>"""
        return job_script

def get_polarization_direction(task_info):
    laser=task_info.param.get('laser')
    if laser:
        pol = laser[0].get('polarization')
    else:
        pol = task_info.param.get('polarization')

    return get_direction(pol)

def get_direction(direction:list):
    pol_map = {'0' : 'x', '1' : 'y', '2': 'z'}
    index = direction.index(1)
    return index , pol_map[str(index)]

def format_gs_input(gen_dict: dict) -> dict:
    """ Converts a generalised dft input parameters to GPAW specific input
        parameters."""

    param_data = gpaw_gs_param_data
    gs_dict = copy.deepcopy(default_param)

    gs_dict['restart'] = gen_dict.get('restart', False)

    mode = gen_dict.get('basis_type')
    if mode not in param_data['basis_type']['values']:
        raise InputError(f"Undefined basis_type: {mode}")

    gs_dict.update({'mode': mode})

    gs_dict['mixing'] = gen_dict.get('mixing', None)
    gs_dict['smearing'] = gen_dict.get('smearing', None)

    gs_dict['extra_states'] = gen_dict.get('bands', 0)
    
    if mode == 'lcao':
        basis = gen_dict.get('basis')
        if basis not in param_data['basis']['metadata']['basis_type']['lcao']['values']:
            raise InputError(f'Basis:{basis} not compatable with basis_type:{mode}.')

        gs_dict.update({'basis':{'default': basis}})

    elif mode == 'fd':
        pass
    elif mode == 'pw':
        pass
    
    xc = gen_dict.get('xc')
    if xc not in param_data['xc']['values']:
        raise InputError(f'xc: {xc} is not supported in GPAW')
    gs_dict['xc'] = xc

    box = gen_dict.get('boxshape')
    if box != 'parallelepiped' and box is not None:
        raise InputError(f"Boxshape: {box} not compatable with gpaw.")

    box_dim = gen_dict.get('box_dim')
    if box_dim:
        gs_dict.update({'box_dim' : True})
        gs_dict.update({'vacuum' : None}) # Vacuum can't be used in box dimensions?
        gs_dict.update(box_dim)
    else:
        gs_dict.update({'box_dim' : False})
        vacuum = gen_dict.get('vacuum', 6)
        gs_dict.update({'vacuum': vacuum})

    spacing = gen_dict.get('spacing', 0.3)
    gs_dict.update({'h': spacing})

    spinpol = gen_dict.get('spin')
    if spinpol == 'polarized':
        gs_dict['spinpol'] = True
    elif spinpol == 'unpolarized':
        gs_dict['spinpol'] = False
    else:
        raise InputError(f"Unkown spin:{spinpol}")

    maxiter = gen_dict.get("max_iter", 333)
    gs_dict['maxiter'] = maxiter

    energy_conv = gen_dict.get('energy_conv')
    density_conv = gen_dict.get('density_conv')

    gs_dict['convergence']['energy'] = energy_conv
    gs_dict['convergence']['density'] = density_conv
    
    # TODO: Implement input of smearing functions
    smearing_func = gen_dict.get('smearing_fun', 'fermi-dirac')
    smearing_width = float(gen_dict.get('smearing', 0.0))

    if smearing_func not in param_data['smearing_fun']['values']:
        raise InputError(f'Unkown smearing function: {smearing_func}')

    gs_dict['occupations'] = {}
    gs_dict['occupations']['name'] = smearing_func
    gs_dict['occupations']['width'] = smearing_width

    return gs_dict
    

def update_td_input(param):
    pol = param.get('polarization', None)
    lasers = param.get('laser',None)
    if lasers:
        laser_list = []
        if not isinstance(lasers, list):
            laser_list.append(lasers)
        else:
            laser_list.extend(lasers)
        
        for laser in laser_list:
            if 'polarization' not in laser:
                laser['polarization'] = pol
                
            sigma = laser.get('sigma')
            time0 = laser.get('time0')
            if sigma == None:
                print( )
            else:
                laser['sigma'] = autime_to_eV/sigma
            laser['time0'] = time0 * au_to_as
        
        param['laser'] = laser_list
    
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

class GpawPostProMasking(GpawTask):

    def get_dm_files(self):
        """Gets dipole moment file names from TD task info"""
        td_info = self.dependent_tasks[0]
        self.dm_files = td_info.output.get('dm_files')
        copy_dms = copy.deepcopy(self.dm_files)
        self.total_dm_fname = copy_dms.pop(0)
        self.masked_dms = copy_dms
        self.total_dm_path = self.project_dir / str(self.total_dm_fname)
        self.masked_dm_files = []
        for dm in self.masked_dms:
            dm_fpath = self.project_dir / str(dm)
            self.masked_dm_files.append(dm_fpath)

    def extract_masked_dm(self):
        """Extracts dipole moment data"""
        from litesoph.post_processing.masking_utls import MaskedDipoleAnaylsis
        self.masked_dm_analysis = MaskedDipoleAnaylsis(task_dir=self.task_dir, 
                                                        focus_region_dms= self.masked_dm_files, 
                                                        total_dm= self.total_dm_path)
        self.create_directory(self.task_dir)
        self.state_mask_dm = True
        masked_dm_fpaths = []
        for i, dm_file in enumerate(self.masked_dm_files):
            r_i = i+1
            # out_fname = 'dm.dat_mask_complement_'+str(r_i)
            out_fname = 'dm_mask_complement_'+str(r_i)+'.dat'
            self.masked_dm_analysis.get_dm_complement(region_i=r_i, out_file=out_fname)
            out_fpath = self.task_dir.relative_to(self.directory) / out_fname
            masked_dm_fpaths.append(str(out_fpath))
        
        self.task_info.output['mask_dm_complement_files'] = masked_dm_fpaths
        self.task_info.local_copy_files.extend(masked_dm_fpaths)

    def setup_task(self, param):
        self.get_dm_files()
        self.state_mask_dm = False
        self.extract_masked_dm()  

    def get_energy_coupling_constant(self, **kwargs):        
        if not self.state_mask_dm:
            self.extract_masked_dm()
        region = kwargs.get('region_id')
        axis = kwargs.get('direction')
        focus = kwargs.get('focus')

        try:
            files_to_copy = []
            envelope_fpaths = []
            coupling_fpath = self.masked_dm_analysis.energy_coupling_file.relative_to(self.directory)
            coupling_val = self.masked_dm_analysis.get_energy_coupling(axis, region,focus= focus)
            for envelope_file in self.masked_dm_analysis.envelope_files:
                env_fpath = Path(envelope_file).relative_to(self.directory)
                envelope_fpaths.append(str(env_fpath))
                files_to_copy.append(str(env_fpath))

            self.task_info.output['envelope_files'] = envelope_fpaths
            self.task_info.output['energy_coupling_file'] = str(coupling_fpath)
            files_to_copy.append(str(coupling_fpath))
            
            for file in files_to_copy:
                if file not in self.task_info.local_copy_files:
                    self.task_info.local_copy_files.append(file)            
            return coupling_val
        except Exception as e:
            raise e

    def plot(self, **kwargs):
        if not self.state_mask_dm:
            self.extract_masked_dm()
        list_to_plot = kwargs.get('plot_data')
        plt = self.masked_dm_analysis.plot(list_to_plot)
        plt.show()

class PumpProbePostpro(GpawTask):

    """
    Step 1: get all the dipole moment files from different td task with corresponding delay from taskinfo
    Step 2: generate spectrum file from corresponding dmfile and save its information back to taskinfo
    Step 3: generate x,y,z data for contour plot from spectrum file and delay data
    """
    def setup_task(self,param):
        task_dir = self.project_dir / 'gpaw' / self.task_name
        self.task_dir = get_new_directory(task_dir)
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)  

        self.only_workflow_dirpath=self.project_dir.name
        self.only_task_dirpath=Path(self.task_dir).relative_to(self.project_dir)
    
    def extract_dm(self, gpaw_dm_file, index):
        data = np.loadtxt(str(gpaw_dm_file),comments="#",usecols=(0,2,3,4))      
        dm_axis_data=data[:,[0,index]]  
        return dm_axis_data

    def generate_spectrums(self,damping=None,padding=None):
        """generate spectrum file from dipole moment data"""
        
        for i in range(len(self.dependent_tasks)):
            axis_index,_=get_polarization_direction(self.dependent_tasks[i])
            sim_total_dm = Path(self.project_dir)/(self.dependent_tasks[i].output.get('dm_files')[0])
            gen_standard_dm_file=self.extract_dm(sim_total_dm, axis_index+1)
            delay=self.dependent_tasks[i].param.get('delay')             
            
            out_spectrum_file= Path(self.only_task_dirpath) /f'spec_delay_{delay}.dat'                   
            self.task_info.output[f'spec_delay_{delay}']=out_spectrum_file             
            out_standard_dm_file= Path(self.project_dir.parent/self.only_workflow_dirpath/self.only_task_dirpath) /f'dm_delay_{delay}.dat'            
            np.savetxt(out_standard_dm_file, gen_standard_dm_file, delimiter='\t', header="time \t dm")

            from litesoph.post_processing.spectrum import photoabsorption_spectrum            
            damping_var= None if damping is None else damping 
            padding_var= None if padding is None else padding 

            spec_file_path= Path(self.project_dir.parent/self.only_workflow_dirpath)/out_spectrum_file
            photoabsorption_spectrum(out_standard_dm_file,spec_file_path, process_zero=False,damping=damping_var,padding=padding_var)
                                    
    def generate_tas_data(self):
        from litesoph.visualization.plot_spectrum import get_spectrums_delays,prepare_tas_data                
        
        self.contour_x_data_file= Path(self.only_task_dirpath) /'contour_x_data.dat' 
        self.contour_y_data_file= Path(self.only_task_dirpath) /'contour_y_data.dat' 
        self.contour_z_data_file= Path(self.only_task_dirpath) /'contour_z_data.dat' 
        
        self.task_info.output['contour_x_data']=self.contour_x_data_file       
        self.task_info.output['contour_y_data']=self.contour_y_data_file             
        self.task_info.output['contour_z_data']=self.contour_z_data_file             
        
        contour_x_data_file=Path(self.project_dir.parent/self.only_workflow_dirpath)/self.contour_x_data_file
        contour_y_data_file=Path(self.project_dir.parent/self.only_workflow_dirpath)/self.contour_y_data_file
        contour_z_data_file=Path(self.project_dir.parent/self.only_workflow_dirpath)/self.contour_z_data_file
        
        delay_list,spectrum_data_list=get_spectrums_delays(self.task_info,self.dependent_tasks,self.project_dir,self.only_workflow_dirpath)
        prepare_tas_data(spectrum_data_list,delay_list,contour_x_data_file,contour_y_data_file,contour_z_data_file)

    def plot(self,delay_min=None,delay_max=None,freq_min=None,freq_max=None):     
        from litesoph.visualization.plot_spectrum import contour_plot
        x_data = np.loadtxt(self.project_dir.parent /self.only_workflow_dirpath/ (self.task_info.output.get('contour_x_data')))
        y_data = np.loadtxt(self.project_dir.parent /self.only_workflow_dirpath/ (self.task_info.output.get('contour_y_data')))
        z_data = np.loadtxt(self.project_dir.parent /self.only_workflow_dirpath/ (self.task_info.output.get('contour_z_data')))
                        
        if delay_min is None: x_min= np.min(x_data)
        elif delay_min < np.min(x_data): raise InputError(f'Minimum delay limit out of range. Allowed minimum delay limit is {np.min(x_data)}')
        else: x_min= delay_min

        if delay_max is None: x_max= np.max(x_data)
        elif delay_max > np.max(x_data): raise InputError(f'Maximum delay limit out of range. Allowed maximum delay limit is {np.max(x_data)}')
        else: x_max= delay_max
    
        if freq_min is None: y_min= np.min(y_data)
        elif freq_min < np.min(y_data): raise InputError(f'Minimum frequency limit out of range. Allowed minimum frequency limit is {np.min(y_data)}')
        else: y_min= freq_min

        if freq_max is None:y_max= np.max(y_data)
        elif freq_max > np.max(y_data):raise InputError(f'Maximum frequency limit out of range. Allowed maximum frequency is {np.max(y_data)}')
        else: y_max= freq_max
    
        plot=contour_plot(x_data,y_data,z_data, 'Delay Time (femtosecond)','Frequency (eV)', 'Pump Probe Analysis',x_min,x_max,y_min,y_max)
        return plot
