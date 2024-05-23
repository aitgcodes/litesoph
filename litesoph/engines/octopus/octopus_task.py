import os
import copy
import numpy as np
import shutil
from pathlib import Path
from typing import Any, List, Dict, Union

from litesoph.common.task import Task, InputError, TaskFailed, TaskNotImplementedError, assemable_job_cmd
from litesoph.engines.octopus.octopus import Octopus
# from litesoph.engines.gpaw.gpaw_task import get_polarization_direction
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.data_sturcture.data_classes import TaskInfo 
from litesoph.common.utils import get_new_directory
from litesoph.engines.octopus.format_oct import get_gs_dict, get_oct_kw_dict
from litesoph.visualization.plot_spectrum import plot_multiple_column, plot_spectrum_octo_polarized


engine_log_dir = 'octopus/log'
engine_inp_dir = 'octopus/inputs'

general_input_file = 'octopus/inp'

octopus_data = {    
    "unoccupied_task": {'out_log':f'{engine_log_dir}/unocc.log'},

    tt.GROUND_STATE: {'inp':general_input_file,
                    'task_inp': 'gs.inp',
                    'out_log': 'gs.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['SCF converged'],
                    'copy_list': ['exec', 'static'],
                    'restart': 'restart/gs'
                    },

    tt.RT_TDDFT: {'inp':general_input_file,
                    'task_inp': 'td.inp',
                    'out_log': 'td.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['Finished writing information', 'Calculation ended'],
                    'copy_list': ['exec', 'td.general'],
                    'restart': 'restart/td'
                    },

    tt.COMPUTE_SPECTRUM: {'inp':general_input_file,
                'task_inp': 'spec.inp',
                'out_log': 'spec.log',
                'req' : ['coordinate.xyz'],
                'spectra_file': ['cross_section_vector'],
                'copy_list': ['cross_section_vector']
                },
    tt.COMPUTE_AVERAGED_SPECTRUM: {'inp':general_input_file,
                'task_inp': 'spec.inp',
                'out_log': 'spec.log',
                'req' : ['coordinate.xyz'],
                'output': ['avg_spectrum.dat'],
                'spectra_file': ['cross_section_tensor','cross_section_vector.1', 
                        'cross_section_vector.2', 'cross_section_vector.3']
                },
                
    tt.TCM: {'inp': None,
            'ksd_file': 'ksd/transwt.dat'},

    tt.MO_POPULATION:{'inp': None,
        'dir': 'population',
        'population_file': 'population.dat'},      
}

class OctopusTask(Task):
    """ Wrapper class to perform Octopus tasks """
    NAME = 'octopus'

    simulation_tasks =  [tt.GROUND_STATE, tt.RT_TDDFT]
    post_processing_tasks = [tt.COMPUTE_SPECTRUM, tt.COMPUTE_AVERAGED_SPECTRUM, tt.TCM, tt.MO_POPULATION]    
    added_post_processing_tasks = [tt.TCM, tt.MO_POPULATION]     # Post-Processing Tasks without octopus simulation
    implemented_task = simulation_tasks + post_processing_tasks
    
    def __init__(self, lsconfig, 
                task_info: TaskInfo, 
                dependent_tasks: Union[List[TaskInfo],None]= None
                ) -> None:  
        super().__init__(lsconfig, task_info, dependent_tasks)

        if dependent_tasks:
            self.dependent_tasks = dependent_tasks
        self.wf_dir = self.project_dir
        self.task_data = octopus_data.get(self.task_name)
        self.params = copy.deepcopy(self.task_info.param)        
        self.user_input = {}
        self.user_input['task'] = self.task_name
        self.user_input = self.params

        self.validate_task_param()
        self.setup_task(self.user_input)
    
    def validate_task_param(self):
        """Engine level validation of the input dict for the task
        \n
        """
        self.restart = self.params.get('restart', False)
        name = self.task_info.name
        if name == tt.RT_TDDFT:
            from litesoph.engines.octopus.format_oct import calc_td_range
            # Time step for TD simulation has a maximum limit bound by grid-spacing
            t_step = float(self.params.get('time_step'))                      
            gs_info = self.dependent_tasks[0]
            if gs_info:
                gs_spacing = gs_info.param.get('spacing')
            t_step_max = calc_td_range(gs_spacing)
            if t_step > t_step_max:
                raise InputError(f'Expected time step less than {t_step_max} as')
    
    def setup_task(self, param:dict): 
        """
        General method for Octopus driven tasks,
        Sets the tasks and initiates Octopus class by default.\n

        Needs modification for added post-processing task        
        """  

        if self.task_name in self.added_post_processing_tasks:
            relative_infile = None
            relative_outfile = None
        
        self.set_dir()
        self.pre_run()
        self.update_task_param()   
        self.update_task_info()

        relative_infile = self.input_filename
        if self.task_info.output.get('txt_out'):
            relative_outfile = Path(self.task_info.output['txt_out'])

        self.octopus = Octopus(infile= relative_infile, outfile=relative_outfile,
                             directory=Path(self.engine_dir), **self.user_input)
    
    def set_dir(self):
        """
        Sets task_dir for current task, creates engine dir and output dir if not exists.
        """

        # Engine & Task dir
        self.engine_dir = str(self.wf_dir / 'octopus')
        if self.task_info.job_info.directory is None:
            task_dir = Path(self.engine_dir) / self.task_name
            self.task_dir = get_new_directory(task_dir)
            self.task_info.job_info.directory = self.task_dir.relative_to(self.wf_dir)
        else:
            self.task_dir = self.wf_dir / self.task_info.job_info.directory

        # Only needed for Octopus simulation
        # Specific to Octopus interfaced tasks
        self.input_filename = 'inp'
        self.task_input_filename = self.task_data.get('task_inp', 'inp')
        geom_fname = self.user_input.get('geom_fname','coordinate.xyz')
        self.geom_file = '../' + str(geom_fname)
        self.geom_fpath = str(self.wf_dir / str(geom_fname))
        self.output_dir = str(Path(self.engine_dir) / 'log')
        self.network_done_file = Path(self.engine_dir) / 'Done'

        for dir in [self.engine_dir, self.output_dir]:
            self.create_directory(Path(dir))
        log_files = list(Path(self.output_dir).iterdir())
        for log in log_files:
            os.remove(Path(self.output_dir)/log) 

        # Restart dir
        restart_dir = self.task_data.get('restart')
        if self.restart:
            if restart_dir is not None:
                restart_path = Path(self.engine_dir) / str(restart_dir)
                if not Path.is_dir(restart_path):
                    raise InputError(f'Can not restart! Restart folder: {str(restart_path)} not found.')
            else:
                raise InputError(f'No restart folder assigned!')
        
    def pre_run(self):
        """
        Handles file related actions.
        Uses dependent task info in context of current task,
        Includes:
            Defining task related variable for required/output files, 
            Copying the required files to octopus folder structure
        """

        if self.task_name == tt.COMPUTE_SPECTRUM:
            td_info = self.dependent_tasks[0]
            if td_info:
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(self.wf_dir / Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)
            return

        elif self.task_name in self.added_post_processing_tasks:            
            td_info = self.dependent_tasks[1]
            if td_info:
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(self.wf_dir / Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)
        
    def update_task_info(self, **kwargs):
        """ Updates current task info with relative paths of input and output files
        """    

        # TODO: add these
        if self.task_name in self.added_post_processing_tasks:
            return  

        # Specific to Octopus interfaced tasks 
        self.task_info.input['engine_input']={}
        self.task_info.input['geom_file'] = Path(self.geom_fpath).relative_to(self.wf_dir)
        self.task_info.input['engine_input']['path'] = str(self.NAME) +'/'+ self.input_filename
        
        if self.restart is True:
            n_restart = self.task_info.task_data.get('nrestart', 0)
            out_log = self.get_restart_log(folder=self.task_dir,fname=self.task_data.get('out_log'))
            self.task_info.output['txt_out'] = str(out_log.relative_to(self.wf_dir))
        else:
            self.task_info.output['txt_out'] = str(Path(self.task_dir).relative_to(self.wf_dir) / self.task_data.get('out_log'))
        
        if self.task_info.output.get('txt_out_files', None) is None:
            self.task_info.output['txt_out_files'] = []
            self.task_info.output['txt_out_files'].append(self.task_info.output['txt_out'])
        elif isinstance(self.task_info.output['txt_out_files'], list):
            self.task_info.output['txt_out_files'].append(self.task_info.output['txt_out'])

        # Adding local copy files/folders
        geom_path = str(Path(self.geom_fpath).relative_to(self.wf_dir))
        restart_dir = self.task_data.get('restart')
        if restart_dir is not None:
            restart_path = 'octopus/'+str(restart_dir)
            self.task_info.local_copy_files.extend([geom_path,restart_path])
        self.task_info.local_copy_files.append(str(self.task_dir.relative_to(self.wf_dir)))
        self.update_added_task_info()

    def update_added_task_info(self):
        """Updates task info specific to the tasks, related to output files"""

        if self.task_name == tt.RT_TDDFT:
            self.task_info.output['multipoles'] = str(Path(self.task_dir).relative_to(self.wf_dir)
                                                     / 'td.general'/ 'multipoles')
        elif self.task_name == tt.COMPUTE_SPECTRUM:
            self.task_info.output['spectra_file'] = []
            for spec_file in self.task_data.get('spectra_file'):
                spectra_fpath = str(Path(self.task_dir).relative_to(self.wf_dir) / spec_file)
                self.task_info.output['spectra_file'].append(spectra_fpath)
        
    def update_task_param(self):
        """ 
        Updates input task parameters to engine-specific parameters
        """
        task = self.task_name
        copy_input = copy.deepcopy(self.user_input)
        param = {
            'XYZCoordinates' : self.geom_file,
            'FromScratch' : 'yes'
        }
        if self.restart is True:
            param.update({'FromScratch': 'no'})
        
        param_copy = copy.deepcopy(param)
        copy_input.update(param)

        if task == tt.GROUND_STATE:
            # Set Calculation Mode expliciltly            
            param.update(get_gs_dict(copy_input, self.geom_fpath))
            self.user_input = param            
            return

        elif task == tt.RT_TDDFT:            
            param_copy.update(self.dependent_tasks[0].param)
            gs_oct_param = get_gs_dict(param_copy, self.geom_fpath)
            param.update(gs_oct_param)
            oct_td_dict = get_oct_kw_dict(copy_input,task)            
            param.update(oct_td_dict)
            self.user_input = param            
            return

        elif task in [tt.COMPUTE_SPECTRUM, tt.COMPUTE_AVERAGED_SPECTRUM]:
            param.update(get_oct_kw_dict(copy_input, task))
            self.user_input = param  
            return      

    def get_restart_log(self, folder:str=Path, fname:str= None):
        """
        Method to get updated name of restart file for multiple run.
        Checks if the {fname}_restart_{i} exists in the folder. 
        If so,appends suffix index and returns
        """
        import re
        if folder is None:
            folder = self.task_dir
        if fname is None:
            fname = str(self.task_data.get('out_log'))

        r_prefix = fname + '_restart_'
        r_fname = r_prefix + str(1)
        fpath = Path(folder)/r_fname
        
        if Path.exists(Path(fpath)):
            _name = Path(fpath).name
            suff_int = int(re.match('.*?([0-9]+)$', _name).group(1))+1
            new_r_fname = r_prefix + str(suff_int)
            new_r_fpath = Path(folder)/new_r_fname
            return new_r_fpath
        else:
            return fpath

    #--------------------------------------------------------------------------------------------

    def check_run_status(self):
        """Returns run_status bool and returncode value"""

        run_status = False
        if self.task_info.job_info.submit_mode == 'remote':
            check = self.task_info.job_info.submit_returncode
        else:
            check = self.task_info.job_info.job_returncode
        if check is None:
            raise TaskFailed("Job not completed.")
        else:
            if check != 0:
                run_status = False
            else:
                run_status = True
        return run_status, check

    def post_run(self):
        """Handles copying output folders to task directory from octopus specific folder structure
        for local run"""
        
        log_files = list(Path(self.output_dir).iterdir())
        for log in log_files:
            shutil.copy(Path(self.output_dir)/log, Path(self.task_dir))
        task = self.task_name
        if task == tt.GROUND_STATE:
            folders = ['exec', 'static']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.task_dir)/ item, dirs_exist_ok=True)
        elif task == tt.RT_TDDFT:
            folders = ['td.general']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.task_dir)/ item, dirs_exist_ok=True)
        elif task == tt.COMPUTE_SPECTRUM:              
            folders = ['cross_section_vector']
            for item in folders:
                shutil.copy(Path(self.engine_dir) / item, Path(self.task_dir)/ item)

    def write_input(self, template=None):
        """ Gets the input filepath and writes\n
        Creates task_dir and ccopies the input file to it after writing"""
        inp_filepath = self.wf_dir / str(self.task_info.input['engine_input']['path'])

        self.create_task_dir()             
        self.octopus.write_input(self.task_info.input['engine_input']['data'])  
        shutil.copy(inp_filepath, self.task_dir / 'inp')      

    def create_task_dir(self):
        """Craetes task dir and stores to task info"""
        self.task_info.output['task_dir'] = str(self.task_dir.relative_to(self.wf_dir))
        self.create_directory(self.task_dir)  

    def create_template(self):
        self.template = self.octopus.create_input()
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = self.template

    def add_cp_mv_on_remote(self, dst:str):
        task_data = octopus_data.get(self.task_name)
        copy_list = task_data.get('copy_list', None)
        add_lines = []
        if isinstance(copy_list, list):
            for item in copy_list:
                line = "mv "+ str(item) + ' '+ dst
                add_lines.append(line)
            lines_str = "\n".join(add_lines)
        else:
            lines_str = None       
        return lines_str

    def create_job_script(self, np=None, remote_path=None):
        
        job_script = super().create_job_script()  
        ofilename = Path(self.task_info.output['txt_out']).relative_to('octopus')
       
        engine_path = copy.deepcopy(self.engine_path)
        mpi_path = copy.deepcopy(self.mpi_path)
        cd_path = self.wf_dir / self.engine_dir
        extra_cmd = None
        cp_mv_lines = None

        # Unoccupied state calculation
        if self.task_name == tt.GROUND_STATE and self.user_input['ExtraStates'] != 0:
            unocc_ofilename = (Path(self.task_dir) / 'unocc.log').relative_to(self.engine_dir)
            if self.restart:
                unocc_log = self.get_restart_log(folder= str(self.task_dir), fname='unocc.log')
                unocc_ofilename = Path(self.task_dir/unocc_log).relative_to(self.engine_dir)
            extra_cmd = "perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp\n"
            extra_cmd = extra_cmd + f"{mpi_path} -np {np:d} {str(engine_path)} &> {str(unocc_ofilename)}"
                
        # Absorption Spectrum utility
        if self.task_name == tt.COMPUTE_SPECTRUM:
            engine_path = Path(self.engine_path).parent / 'oct-propagation_spectrum'

        if remote_path:
            mpi_path = 'mpirun'
            engine_path = 'octopus'
            cd_path = Path(remote_path) / self.wf_dir.parents[0].name / self.wf_dir.name / 'octopus'
            r_task_path = Path(remote_path) / self.wf_dir.parents[0].name / self.wf_dir.name / self.task_dir.relative_to(self.wf_dir)
            cp_mv_lines = self.add_cp_mv_on_remote(dst= str(r_task_path))
        
        #TODO: adding cp/mv lines for local condition     
        # Adding lines to copy/move folders
        if cp_mv_lines is not None:
            if isinstance(extra_cmd, str):
                extra_cmd = extra_cmd + cp_mv_lines 
            else:
                extra_cmd = cp_mv_lines
        engine_cmd = str(engine_path) + ' ' + '&>' + ' ' + str(ofilename)
        job_script = assemable_job_cmd(self.task_info.uuid, engine_cmd, np, cd_path, mpi_path=mpi_path, remote=bool(remote_path),
                                                module_load_block=self.get_engine_network_job_cmd(),
                                                extra_block=extra_cmd)
        self.job_script = job_script
        return self.job_script

    def prepare_input(self):
        """Modifies the same method in Task class\n
        Creates/writes input and job script"""
        if self.task_name in self.added_post_processing_tasks:
            self.create_task_dir()
            self.get_ksd_popln()
            return
        self.create_template()
        self.write_input(self.template)
        self.create_job_script()
        self.write_job_script(self.job_script)     

    def get_engine_log(self):
        """Gets engine log filepath and content, if check_output() returns True"""
        
        out_rel_path = self.task_info.output['txt_out']
        out_log = Path(self.wf_dir) / str(out_rel_path)
        if self.check_output():
            return self.read_log(out_log)

    def plot(self,**kwargs):
        """Method related to plot in post-processing"""

        self.post_run()

        if self.task_name == tt.COMPUTE_SPECTRUM:
            energy_min = self.task_info.param['e_min']
            energy_max = self.task_info.param['e_max']
            spec_file = self.task_data['spectra_file'][0]
            file = self.task_dir / str(spec_file)
            img = file.parent / f"spectrum.png"
            # Plot function automatically checks for Polarization and acts accordingly!
            # By default singlet is passed
            plot_spectrum_octo_polarized(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)", xlimit=(float(energy_min), float(energy_max)))
            return        

        if self.task_name == tt.TCM: 
            from litesoph.common.job_submit import execute_cmd_local

            fmin = kwargs.get('fmin')
            fmax = kwargs.get('fmax')
            axis_limit = kwargs.get('axis_limit')

            path = Path(__file__)
            path_python = self.lsconfig.get('programs', 'python')['python']
            path_plotdmat = str(path.parents[2]/ 'visualization/octopus/plotdmat.py')

            ksd_file = self.task_dir / 'transwt.dat'
            cmd = f'{path_python} {path_plotdmat} {ksd_file} {fmin} {fmax} {axis_limit} -i'
        
            result = execute_cmd_local(cmd, self.task_dir)
            
            if result[cmd]['returncode'] != 0:
                raise Exception(f"{result[cmd]['error']}")
            return

        if self.task_name == tt.MO_POPULATION:
            # first check if the file exists already 
            import numpy as np
            from litesoph.post_processing.mo_population import create_states_index
            below_homo_plot = kwargs.get('num_occupied_mo_plot',1)
            above_lumo_plot = kwargs.get('num_unoccupied_mo_plot',1)
            population_diff_file = self.task_dir/'population_diff.dat'
            homo_index = self.user_input['num_occupied_mo']

            column_range = (homo_index-below_homo_plot+1, homo_index+above_lumo_plot)
            legend_dict = create_states_index(num_below_homo=below_homo_plot, 
                                            num_above_lumo=above_lumo_plot, homo_index=homo_index)            
            population_data = np.loadtxt(population_diff_file)
            plot_multiple_column(population_data, column_list=column_range, column_dict=legend_dict, xlabel='Time (in h_cut/eV)')
            return        

    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of Octopus or load the module

#spack load octopus
#module load octopus"""
        return job_script

    def run_job_local(self,cmd):
        if self.task_name in [tt.TCM, tt.MO_POPULATION]:
            return
        cmd = cmd + ' ' + self.BASH_filename
        self.submit_local.run_job(cmd)

    def get_ksd_popln(self):
        td_info = self.dependent_tasks[1] 
        if td_info:
            _axis = td_info.param.get('polarization')
            if not _axis:
                _axis = td_info.param['laser'][0]['polarization']
            max_step = td_info.param['number_of_steps']
            output_freq = td_info.param['output_freq']
            nt = int(max_step/output_freq) 

        below_homo = self.user_input['num_occupied_mo']
        above_lumo = self.user_input['num_unoccupied_mo']

        [occ,homo,lumo]=self.octopus.read_info()
        proj_read = self.octopus.read_projections(time_end= nt,
                                number_of_proj_occupied= below_homo,
                                number_of_proj_unoccupied=above_lumo,
                                axis=_axis)
        try:            
            if self.task_name == tt.TCM:
                self.octopus.compute_ksd(proj=proj_read, out_directory=self.task_dir)
            if self.task_name == tt.MO_POPULATION:
                from litesoph.post_processing.mo_population import calc_population_diff
                population_file = self.task_dir/self.task_data.get('population_file')
                population_diff_file = self.task_dir/'population_diff.dat'
                [proj_obj, population_array] = self.octopus.compute_populations(out_file = population_file, proj=proj_read)
                
                calc_population_diff(homo_index=below_homo,infile=population_file, outfile=population_diff_file)
            self.task_info.job_info.job_returncode = 0
            self.task_info.job_info.output = ''
        except Exception:
            self.task_info.job_info.job_returncode = 1

class OctAveragedSpectrum(OctopusTask):
    """Added Post-Processing Class to compute Averaged Spectrum"""

    def validate_task_param(self):
        self.restart = False

    def pre_run(self):
        """Gets dependent tasks info and defines class variables"""

        self.spectrum_files = []
        for i, td_task in enumerate(self.dependent_tasks):
            td_info = td_task
            if td_info:
                spec_file = td_info.output['spectra_file'][0]
                spec_file_path = str(self.wf_dir / spec_file)
                self.spectrum_files.append(spec_file_path)
        self.averaged_spec_file = self.task_dir / 'averaged_spec.dat'

    def update_added_task_info(self):
        """Modified to store output files"""

        self.task_info.output['spectra_file'] = []
        for spec_file in self.task_data.get('spectra_file', []):
            spectra_fpath = str(Path(self.task_dir).relative_to(self.wf_dir) / spec_file)
            self.task_info.output['spectra_file'].append(spectra_fpath)

    def setup_task(self, param: dict):        
        self.set_dir()
        self.pre_run()
        self.update_task_info()

    def prepare_input(self):
        """Modifies the same method in Task class
        Creates/writes input and job script"""

        self.create_task_dir()
        self.compute_avg_spectra()
    
    def compute_avg_spectra(self):
        """Computes average or differential of spectra data based on polarization"""
        
        time_data = []
        data_1 = np.loadtxt(self.spectrum_files[0])
        self.isPolarized = True if data_1.shape[1] == 9 else False

        if self.isPolarized:
            polarized_data_sum = []
            polarized_data_diff = []
        else:
            spec_data = []

        for i, file in enumerate(self.spectrum_files):
            data = np.loadtxt(file)
            time_data.append(data[:, 0])

            if self.isPolarized:
                sum_data = data[:, 7] + data[:, 8]  # Sum of 8th and 9th columns
                diff_data = data[:, 7] - data[:, 8] # Difference of 8th and 9th columns
                polarized_data_sum.append(sum_data)
                polarized_data_diff.append(diff_data)
            else:
                spec_data.append(data[:, 4])  # Default to 5th column for non-polarized data

        if self.isPolarized:
            # Handling polarized data
            sum_data_stacked = np.column_stack(tuple(polarized_data_sum))
            diff_data_stacked = np.column_stack(tuple(polarized_data_diff))
            averaged_sum_data = np.average(sum_data_stacked, axis=1)
            averaged_diff_data = np.average(diff_data_stacked, axis=1)
            spec_avg_data = np.column_stack((time_data[0], averaged_sum_data, averaged_diff_data))

            # Plot sum and diff data
            # self.plot(data_type='sum')
            # self.plot(data_type='difference')
        else:
            # Handling default non-polarized data
            spec_data = np.column_stack(tuple(spec_data))
            averaged_data = np.average(spec_data, axis=1)
            spec_avg_data = np.column_stack((time_data[0], averaged_data))
        np.savetxt(self.averaged_spec_file, spec_avg_data)


    def plot(self, data_type='average', **kwargs):
        """Method to plot average, summed, or subtracted spectrum based on polarization status."""
        from litesoph.visualization.plot_spectrum import plot_spectrum
        self.post_run()

        energy_min = self.task_info.param['e_min']
        energy_max = self.task_info.param['e_max']

        # Determine the file to plot and title based on data_type
        if data_type == 'sum':
            data_file = self.averaged_spec_file.with_name(f"{self.averaged_spec_file.stem}_sum.dat")
            plot_title = "Summed Polarized Spectrum"
        elif data_type == 'difference':
            data_file = self.averaged_spec_file.with_name(f"{self.averaged_spec_file.stem}_diff.dat")
            plot_title = "Differential Polarized Spectrum"
        else:  # Default to 'average'
            data_file = self.averaged_spec_file
            plot_title = "Average Spectrum"

        # Plotting
        spec_file = data_file.with_suffix('.png')
        if self.isPolarized:
            plot_spectrum(data_file, spec_file, 0, [1, 2], "Energy (in eV)", "Strength (in /eV)", xlimit=(float(energy_min), float(energy_max)), legends = ["Singlet", "Triplet"])
        else:
            plot_spectrum(data_file, spec_file, 0, 1, "Energy (in eV)", "Strength (in /eV)", xlimit=(float(energy_min), float(energy_max)), legends = ["Singlet"])


class PumpProbePostpro(OctopusTask):

    """
    Step 1: get all the dipole moment files from different td task with corresponding delay from taskinfo
    Step 2: generate spectrum file from corresponding dmfile and save its information back to taskinfo
    Step 3: generate x,y,z data for contour plot from spectrum file and delay data
    """        
    def setup_task(self,param):
        task_dir = self.project_dir / 'octopus' / self.task_name
        self.task_dir = get_new_directory(task_dir)

        if not self.task_dir.exists():
            self.create_directory(self.task_dir)  

        self.only_workflow_dirpath=self.project_dir.name
        self.only_task_dirpath=Path(self.task_dir).relative_to(self.project_dir)
        
    def extract_dm(self, dm_file, index):
        data = np.loadtxt(str(dm_file),comments="#",usecols=(1,3,4,5))      
        dm_axis_data=data[:,[0,index]]  
        dm_axis_data[:,0]*= 27.12 # time unit conversion to au
        return dm_axis_data
    
    def generate_spectrums(self,damping=None,padding=None):
        """generate spectrum file from dipole moment data"""
        from litesoph.engines.gpaw.gpaw_task import get_polarization_direction

        for i in range(len(self.dependent_tasks)):
            axis_index,_=get_polarization_direction(self.dependent_tasks[i])

            sim_total_dm = Path(self.project_dir)/(self.dependent_tasks[i].output.get('multipoles'))

            gen_standard_dm_file=self.extract_dm(sim_total_dm, axis_index+1)
            delay=self.dependent_tasks[i].param.get('delay')             

            out_spectrum_file= Path(self.only_task_dirpath) /f'spec_delay_{delay}.dat'                   
            self.task_info.output[f'spec_delay_{delay}']=out_spectrum_file             
            out_standard_dm_file= Path(self.project_dir.parent/self.only_workflow_dirpath/self.only_task_dirpath) /f'dm_delay_{delay}.dat'            
            np.savetxt(out_standard_dm_file, gen_standard_dm_file, delimiter='\t', header="time \t dm")

            from litesoph.post_processing.spectrum import photoabsorption_spectrum            
            damping_var= damping 
            padding_var= padding 

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
        self.post_run()
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
