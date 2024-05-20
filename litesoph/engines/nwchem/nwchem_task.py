from typing import List, Dict, Union
from abc import abstractmethod
import copy
import pathlib
from pathlib import Path
from litesoph.utilities.units import as_to_au
from litesoph.common.utils import get_new_directory
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.post_processing.mo_population import calc_population_diff, get_energy_window, get_occ_unocc
from litesoph.common.task import InputError, Task, TaskFailed, TaskNotImplementedError, assemable_job_cmd
from litesoph.common.task_data import TaskTypes as tt
from litesoph.engines.nwchem.nwchem import NWChem
from litesoph.engines.nwchem.spectrum import photoabsorption_spectrum
from litesoph.visualization.plot_spectrum import plot_multiple_column, plot_spectrum
import numpy as np
from litesoph.post_processing.mo_population import create_states_index
from litesoph.engines.nwchem.task_data import nwchem_gs_param_data, nwchem_xc_map
from .task_data import nwchem_xc_map

nwchem_data = {
'ground_state' : {'inp':'nwchem/GS/gs.nwi',
            'out_log' : 'nwchem/GS/gs.nwo',
            'dir' : 'GS',
            'file_name':'gs',
            'req' : ['coordinate.xyz', 'nwchem/restart'],            
            'check_list':['Converged', 'Fermi level:','Total:']},

'rt_tddft' : {'inp':'nwchem/TD_Delta/td.nwi',
        'out_log' : 'td.nwo',
        'file_name' : 'td'},

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

'mo_population':{'inp':'nwchem/TD_Delta/td.nwi',
                            'out_log' : 'nwchem/TD_Delta/td.nwo',
                             'req' : ['nwchem/TD_Delta/td.nwo'],
                            'dir': 'mo_population'},
'restart': 'nwchem/restart'
}

class BaseNwchemTask(Task):

    NAME = 'nwchem'
    simulation_tasks =  [tt.GROUND_STATE, tt.RT_TDDFT]
    post_processing_tasks = [ tt.COMPUTE_SPECTRUM, tt.MO_POPULATION]
    implemented_task = simulation_tasks + post_processing_tasks

    def __init__(self, lsconfig, 
                task_info: TaskInfo, 
                dependent_tasks: Union[List[TaskInfo],None]= None
                ) -> None:
        
        super().__init__(lsconfig, task_info, dependent_tasks)
        
        self.task_data = nwchem_data.get(self.task_name)
        param = copy.deepcopy(self.task_info.param)
        
        self.user_input = param

        if self.task_info.job_info.directory is None:
            task_dir = self.directory / 'nwchem' / self.task_name
            task_dir = get_new_directory(task_dir)
            self.task_info.job_info.directory = task_dir.relative_to(self.directory)

        self.task_dir = self.directory / self.task_info.job_info.directory
        self.task_info.local_copy_files.append(str(self.task_dir.relative_to(self.directory)))
        self.create_engine(self.user_input)
    
    @abstractmethod
    def create_engine(self, param):
        pass

    def write_input(self,):
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)
        template = self.task_info.input['engine_input']['data']
        self.nwchem.write_input(template)

    def create_template(self):
        template = self.nwchem.create_input()
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = template

    def create_job_script(self, np=1, remote_path=None) -> list:
                
        if remote_path:
            self.engine_path = 'nwchem'

        if self.task_name in self.simulation_tasks:
            ofilename = self.outfile
            ifilename =  self.infile
            engine_cmd = self.engine_path + ' ' + str(ifilename) + ' ' + '>' + ' ' + str(ofilename)

            if remote_path:
                rpath = Path(remote_path) / self.task_dir.relative_to(self.directory.parent.parent)
                job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path=str(rpath),
                                        remote=True, module_load_block=self.get_engine_network_job_cmd())
            else:
                job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path= str(self.task_dir),
                                                mpi_path=self.mpi_path)
        self.job_script = job_script
        return self.job_script
    
    def prepare_input(self):
        pass            

    def get_engine_log(self):
        if self.check_output():
            log_file_path = str(self.directory/self.task_info.output['txt_out'])
            return self.read_log(log_file_path)


    def plot(self,**kwargs):
        pass

    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of NWCHEM or load the module

#eval "$(conda shell.bash hook)"
#conda activate <environment name>

#module load nwchem"""
        return job_script
    
class NwchemTask(BaseNwchemTask):

    def create_engine(self, param):
        
        self.network_done_file = self.task_dir / 'Done'
        label = str(self.directory.parent.name)

        if self.task_name in self.post_processing_tasks:
            outfile = str(self.directory / self.dependent_tasks[0].output.get('txt_out'))
            if self.task_name == tt.MO_POPULATION:
                outfile = str(self.directory / self.dependent_tasks[1].output.get('txt_out'))

            self.nwchem = NWChem(outfile=outfile, 
                            label=label, directory=self.task_dir)
            return
    
        
        infile_ext = '.nwi'
        outfile_ext = '.nwo'
        restart = param.get('restart', False)
        if restart:
            nrestart = self.task_info.task_data.get('nrestart', 0)
            nrestart += 1
            outfile_ext  = outfile_ext + str(nrestart)

        file_name = self.task_data.get('file_name')
        self.infile = file_name + infile_ext
        self.outfile = file_name + outfile_ext
        self.task_info.input['engine_input']={}

        if restart:
            self.task_info.output[f'txt_out{nrestart}'] = str(self.task_dir.relative_to(self.directory) / self.outfile)
        else:
            self.task_info.output['txt_out'] = str(self.task_dir.relative_to(self.directory) / self.outfile)
        
        
        if self.task_name == tt.GROUND_STATE:
            param = self.user_input = format_gs_param(param)
        
        param['perm'] = '../restart'
        param['geometry'] = '../../coordinate.xyz'
        
        self.task_info.local_copy_files.extend(['coordinate.xyz',
                                                str(self.task_dir.relative_to(self.directory).parent / 'restart')])
        if self.task_name == tt.RT_TDDFT:
            param['restart_kw'] = 'restart'
            param['basis'] =self.dependent_tasks[0].engine_param.get('basis')
            update_td_param(param)

        self.task_info.input['engine_input']['path'] = str(self.task_dir.relative_to(self.directory) / self.infile)
        
        self.nwchem = NWChem(infile= self.infile, outfile=self.outfile, 
                            label=label, directory=self.task_dir, **param)
            

    def write_input(self,):
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)
        template = self.task_info.input['engine_input']['data']
        self.nwchem.write_input(template)

    def create_template(self):
        template = self.nwchem.create_input()
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = template

    def extract_mo_population(self):
        self.below_homo = below_homo = self.user_input['num_occupied_mo']
        self.above_lumo = above_lumo = self.user_input['num_unoccupied_mo']

        self.create_directory(self.task_dir)
        td_out = str(self.directory / self.dependent_tasks[1].output.get('txt_out'))

        #self.energy_file = self.task_dir / 'energy_format.dat'
        eigen_data = self.nwchem.get_eigen_energy(td_out)
        occ, unocc = get_occ_unocc(eigen_data)
        if (len(occ) < below_homo) or (len(unocc) < above_lumo):
            raise InputError(f'The selected MO is out of range. Number of MO: below HOMO = {len(occ)}, above_LUMO = {len(unocc)}')
        self.mo_population_file = self.task_dir / 'mo_population.dat'
        self.task_info.output['mopop_file'] = str(self.mo_population_file.relative_to(self.directory))
        self.nwchem.get_td_moocc(str(self.mo_population_file), td_out, homo_index=len(occ),
                                     below_homo=below_homo, above_lumo=above_lumo)
        self.mo_population_diff_file = self.task_dir/ 'mo_pop_diff.dat'
        self.task_info.output['mopop_diff_file'] = str(self.mo_population_diff_file.relative_to(self.directory))
        calc_population_diff(homo_index=self.below_homo, infile=self.mo_population_file,
                                outfile=self.mo_population_diff_file)
        #get_energy_window(eigen_data, self.energy_file, below_homo, above_lumo)
    
    # def _create_mo_pop_correlation_cmd(self):
        
    #     bandpass_window = self.user_input['bandpass_window']
    #     hanning_window = self.user_input['hanning_window']
    #     path = pathlib.Path(mo_population_correlation.__file__)
        
    #     pop_py = str(path.parent /'population_correlation.py')
    #     pop_cmd = f'python {pop_py} {self.below_homo} {self.energy_file}'    
        
    #     band_py = str(path.parent / 'bandpass.py')
    #     band_cmd = f'python {band_py} {self.mo_population_file} {bandpass_window}'       
        
    #     hann_py = str(path.parent / 'test.py')
    #     hann_cmd = f'python {hann_py} frest.dat hanning {hanning_window}'
        
    #     dft_mod_py = str(path.parent /'dft-mod.py')
    #     dft_mod_cmd = f'python {dft_mod_py} fn_rest.dat'

    #     return '\n'.join([band_cmd, hann_cmd, dft_mod_cmd, pop_cmd])

    def create_job_script(self, np=1, remote_path=None) -> list:
                
        if remote_path:
            self.engine_path = 'nwchem'

        if self.task_name in self.simulation_tasks:
            ofilename = self.outfile
            ifilename =  self.infile
            engine_cmd = self.engine_path + ' ' + str(ifilename) + ' ' + '>' + ' ' + str(ofilename)

            if remote_path:
                rpath = Path(remote_path) / self.task_dir.relative_to(self.directory.parent.parent)
                job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path=str(rpath),
                                        remote=True, module_load_block=self.get_engine_network_job_cmd())
            else:
                job_script = assemable_job_cmd(job_id= self.task_info.uuid
                                            ,engine_cmd= engine_cmd, np=np, cd_path= str(self.task_dir),
                                                mpi_path=self.mpi_path)
        self.job_script = job_script
        return self.job_script
    
    def prepare_input(self):
        if self.task_name == 'mo_population':
            return

        if self.task_name in self.simulation_tasks:
            self.create_template()
            self.write_input()
        
        self.create_job_script()
        self.write_job_script()
            

    def run_job_local(self, cmd):
        if self.task_name == 'mo_population':
            try:
                self.extract_mo_population()
            except InputError as e:
                self.task_info.job_info.job_returncode = 1
                self.task_info.job_info.output = ''
                self.task_info.job_info.error = str(e)
            else:
                self.task_info.job_info.job_returncode = 0
                self.task_info.job_info.output = ''
                self.task_info.job_info.error = ''
            return
        super().run_job_local(cmd)

    def get_engine_log(self):
        if self.check_output():
            return self.read_log(self.directory / self.task_info.output['txt_out'])


    def plot(self,**kwargs):

        if self.task_name == 'mo_population':
        
            below_homo = kwargs.get('num_occupied_mo_plot',1)
            above_lumo = kwargs.get('num_unoccupied_mo_plot',1)
            homo_index = self.below_homo
            # time_unit = kwargs.get('time_unit')            
            column_range = (homo_index-below_homo+1, homo_index+above_lumo)
            legend_dict = create_states_index(num_below_homo=below_homo, num_above_lumo=above_lumo, homo_index=homo_index)
            
            pop_data = np.loadtxt(self.mo_population_diff_file)
            
            plot_multiple_column(pop_data, column_list=column_range, column_dict=legend_dict, xlabel='Time (au)')
    

def format_gs_param(gen_dict:dict) -> dict:
    param_data = nwchem_gs_param_data
    restart = gen_dict.get('restart', False)
    

    gs_input = {'dft': {}}
    
    if restart:
        gs_input['restart_kw'] = 'restart'

    basis_type = gen_dict.get('basis_type')
    if basis_type != 'gaussian':
        raise InputError(f'Unkown basis type: {basis_type}')

    xc = gen_dict.get('xc')
    if xc not in param_data['xc']['values']:
        raise InputError('Unkown xc: {xc}')
    gs_input['dft']['xc'] = copy.deepcopy(nwchem_xc_map.get(xc))

    basis = gen_dict.get('basis')
    if basis not in param_data['basis']['values']:
        raise InputError('Unkown basis: {xc}')
    gs_input['basis'] = basis
    
    energy_conv = gen_dict.get('energy_conv', 1e-5)
    density_conv = gen_dict.get('density_conv', 1e-7)

    convergence = gs_input['dft']['convergence'] = {}
    convergence['energy'] = energy_conv
    convergence['density'] = density_conv

    gs_input['dft']['iterations'] = gen_dict.get('max_iter')

    return gs_input

def update_td_param(param):
    restart = param.pop('restart', False)
    strength = param.pop('strength', None)
    pol = param.pop('polarization', None)
    time_step = param.pop('time_step')
    num_step = param.pop('number_of_steps')
    out_freq = param.pop('output_freq')
    properties = param.pop('properties')
    lasers = param.pop('laser', None)
    masking = param.pop('masking', None)
    
    param['rt_tddft'] = {'tmax': num_step * time_step * as_to_au,
                        'dt': time_step * as_to_au,
                        'print':out_print(properties)}

    if restart:
        param['rt_tddft']['load'] = 'restart'

    if lasers:
        
        laser_l = []
        if not isinstance(lasers, list):
            laser_l.append(lasers)
        else:
            laser_l.extend(lasers)

        delay = param.pop('delay', None)
        param['rt_tddft']['field'] = laser_list = []     
        
        for i, laser in enumerate(laser_l):
            
            if 'polarization' not in laser:
                laser['polarization'] = pol

            if laser['type'] == 'gaussian':
                laser_dict = add_gaussian_laser(str(i), laser)
            elif laser['type'] == 'delta':
                laser_dict = add_delta_laser(str(i), laser)

            laser_list.append(laser_dict)
    else:
        param['rt_tddft']['field'] = {'name': 'kick_' + read_pol_dir(pol)[1],
                                        'type': 'delta',
                                        'polarization':read_pol_dir(pol)[1],
                                        'max': strength}
def add_gaussian_laser(name, laser):
    laser_dict = {'name': f'{name}_'  + read_pol_dir(laser['polarization'])[1],
                    'type': 'gaussian',
                    'frequency' : laser['frequency'],
                    'center': laser['time0'],
                    'width': laser['sigma'],
                    'polarization':read_pol_dir(laser['polarization'])[1],
                    'max':laser['strength']}

                    
    return laser_dict

def add_delta_laser(name, laser):
    laser_dict = {'name': f'{name}_' + read_pol_dir(laser['polarization'])[1],
                'type': 'delta',
                'polarization':read_pol_dir(laser['polarization'])[1],
                'max': laser['strength']}
    return laser_dict

def out_print(property):
        p = [] 
        if 'spectrum' in property:
            p.append('dipole')
        if 'mo_population'in property:
            p.append('moocc')
        return p

def read_pol_dir(pol):        
        if pol == [1,0,0]:
            return (0,'x')
        elif pol == [0,1,0]:
            return (1,'y') 
        elif pol == [0,0,1]:
            return (2,'z')


def get_pol_and_tag(taskinfo):
    # if the multiple lasers are passed in the field, polarization will be taken for first laser
    if  type(taskinfo.engine_param['rt_tddft']['field']) is list:        
        pol = taskinfo.engine_param['rt_tddft']['field'][0].get('polarization', 'x')
    else:
        pol = taskinfo.engine_param['rt_tddft']['field'].get('polarization', 'x')
    tag = taskinfo.engine_param['rt_tddft'].get('tag', 'rt_tddft')
    return pol, tag


class PumpProbePostpro(NwchemTask):

    """
    Step 1: get all the dipole moment files from different td task with corresponding delay from taskinfo
    Step 2: generate spectrum file from corresponding dmfile and save its information back to taskinfo
    Step 3: generate x,y,z data for contour plot from spectrum file and delay data
    """        

    def create_engine(self, param):
        task_dir = self.project_dir / 'nwchem' / self.task_name
        self.task_dir = get_new_directory(task_dir)
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)  

        self.network_done_file = self.task_dir / 'Done'
        self.only_workflow_dirpath=self.project_dir.name
        self.only_task_dirpath=Path(self.task_dir).relative_to(self.project_dir)
    
    def extract_dm(self,td_out_file,pol,tag):
        from litesoph.engines.nwchem.nwchem_read_rt import nwchem_rt_parser                
        dm_data=nwchem_rt_parser(td_out_file, outfile=None, tag=tag,
                    geometry='system', 
                    target='dipole', spin='closedshell', 
                    polarization=pol, zero=False, retrun_data=True)
        return dm_data
        
    def generate_spectrums(self,damping=None,padding=None):
        """generate spectrum file from dipole moment data"""
        
        for i in range(len(self.dependent_tasks)):            
            self.pol, tag = get_pol_and_tag(self.dependent_tasks[i])
            td_out_file = (self.project_dir / (self.dependent_tasks[i].output.get('txt_out'))) 

            gen_standard_dm_file=self.extract_dm(td_out_file,self.pol,tag)
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
        x_data = np.loadtxt(self.project_dir.parent / (self.task_info.output.get('contour_x_data')))
        y_data = np.loadtxt(self.project_dir.parent / (self.task_info.output.get('contour_y_data')))
        z_data = np.loadtxt(self.project_dir.parent / (self.task_info.output.get('contour_z_data')))
                        
        x_min= np.min(x_data) if delay_min is None else delay_min 
        x_max= np.max(x_data) if delay_max is None else delay_max 
        y_min= np.min(y_data) if freq_min is None else freq_min 
        y_max= np.max(y_data) if freq_max is None else freq_max 

        plot=contour_plot(x_data,y_data,z_data, 'Delay Time (femtosecond)','Frequency (eV)', 'Pump Probe Analysis',x_min,x_max,y_min,y_max)
        return plot
        
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
