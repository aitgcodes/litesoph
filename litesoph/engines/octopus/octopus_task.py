import os
import copy
import shutil
from pathlib import Path
from typing import Any, List, Dict, Union

from numpy import true_divide
from litesoph.common.task import Task, InputError, TaskFailed, TaskNotImplementedError, assemable_job_cmd
from litesoph.engines.octopus.octopus import Octopus
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.data_sturcture.data_classes import TaskInfo 
from litesoph.common.utils import get_new_directory
from litesoph.engines.octopus.octopus_input import get_task
from litesoph import config
from litesoph.engines.octopus.gs2oct import create_oct_gs_inp


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
                
    tt.TCM: {'inp': None,
            'ksd_file': 'ksd/transwt.dat'},

    tt.MO_POPULATION:{'inp': None,
        'dir': 'population',
        'population_file': 'population.dat'},
    
    # "rt_tddft_delta": {'inp':general_input_file,
    #                 'task_inp': 'td_delta.inp',
    #                 'out_log': 'delta.log',
    #                 'req' : ['coordinate.xyz'],
    #                 'check_list':['Finished writing information', 'Calculation ended']},   

    # "rt_tddft_laser": {'inp':general_input_file,
    #                 'task_inp': 'td_laser.inp',
    #                 'out_log': f'{engine_log_dir}/laser.log',
    #                 'req' : ['coordinate.xyz']},
            
    # "tcm": {'inp': None,
    #         'req':[f'{engine_dir}/static/info',
    #         f'{engine_dir}/td.general/projections'],
    #         'dir': 'ksd',
    #         'ksd_file': f'{engine_dir}/ksd/transwt.dat'},

    # "ksd": {'inp': f'{engine_dir}/ksd/oct.inp',
    #     'req':[f'{engine_dir}/static/info',
    #     f'{engine_dir}/td.general/projections'],
    #     'ksd_file': f'{engine_dir}/ksd/transwt.dat'}
    # tt.MO_POPULATION:{'inp': None,
        # 'req':[f'{engine_dir}/static/info',
        # f'{engine_dir}/td.general/projections'],
        # 'dir': 'population',
        # 'population_file': 'population.dat'},          
}
class OctTask(Task):
    pass

class OctopusTask(Task):
    """ Wrapper class to perform Octopus tasks """
    NAME = 'octopus'

    simulation_tasks =  [tt.GROUND_STATE, tt.RT_TDDFT]
    post_processing_tasks = [tt.COMPUTE_SPECTRUM, tt.TCM, tt.MO_POPULATION]
    added_post_processing_tasks = [tt.TCM, tt.MO_POPULATION]
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
        """Engine level validation of the input dict for the task\n
        """
        name = self.task_info.name
        if name == tt.RT_TDDFT:
            # Time step for TD simulation has a maximum limit bound by grid-spacing
            t_step = float(self.params.get('time_step'))                      
            gs_info = self.dependent_tasks[0]
            if gs_info:
                gs_spacing = gs_info.param.get('spacing')
            t_step_max = calc_td_range(gs_spacing)/2
            if t_step > t_step_max:
                raise InputError(f'Expected time step less than {t_step_max} as')
    
    def pre_run(self):
        """Sets task_dir for current task, creates engine dir and output dir if not exists\n
        For post-processing tasks, copies the required files to octopus folder structure"""

        self.input_filename = 'inp'
        self.task_input_filename = self.task_data.get('task_inp', 'inp')
       
        geom_fname = self.user_input.get('geom_fname','coordinate.xyz')
        self.geom_file = '../' + str(geom_fname)
        self.geom_fpath = str(self.wf_dir / str(geom_fname))

        # absolute path attributes
        self.engine_dir = str(self.wf_dir / 'octopus')
        task_dir = (Path(self.engine_dir) / self.task_name)
        self.task_dir = get_new_directory(task_dir)
        self.output_dir = str(Path(self.engine_dir) / 'log')
        self.network_done_file = Path(self.task_dir) / 'Done'
        
        self.task_info.input['engine_input']={}

        for dir in [self.engine_dir, self.output_dir]:
            self.create_directory(Path(dir))

        log_files = list(Path(self.output_dir).iterdir())
        for log in log_files:
            os.remove(Path(self.output_dir)/log)

        if self.task_name == tt.COMPUTE_SPECTRUM:
            td_info = self.dependent_tasks[0]
            if td_info:
                # modify relative paths to absolute path 
                # by prefixing wf_dir
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(self.wf_dir / Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)
            return

        elif self.task_name in self.added_post_processing_tasks:            
            td_info = self.dependent_tasks[1]
            if td_info:
                # modify relative paths to absolute path 
                # by prefixing wf_dir
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(self.wf_dir / Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)

        # Adding local copy files/folders
        geom_path = str(Path(self.geom_fpath).relative_to(self.wf_dir))
        restart_dir = self.task_data.get('restart')
        restart_path = 'octopus/'+str(restart_dir)
        self.task_info.local_copy_files.extend([geom_path,restart_path])
        self.task_info.local_copy_files.append(str(self.task_dir.relative_to(self.wf_dir)))
        
    def update_task_info(self, **kwargs):
        """ Updates current task info with relative paths of input and output files"""
        
        if self.task_name in self.added_post_processing_tasks:
            return
        
        # TODO:relative paths
        self.task_info.input['geom_file'] = Path(self.geom_fpath).relative_to(self.wf_dir)

        self.task_info.input['engine_input']['path'] = str(self.NAME) +'/'+ self.input_filename
        self.task_info.output['txt_out'] = str(Path(self.output_dir).relative_to(self.wf_dir) / self.task_data.get('out_log'))
        if self.task_name == tt.RT_TDDFT:
            self.task_info.output['multipoles'] = str(Path(self.task_dir).relative_to(self.wf_dir) / 'td.general'/ 'multipoles')
            
    def setup_task(self, param:dict): 
        """Sets the tasks and initiates Octopus class"""  

        if self.task_name in self.added_post_processing_tasks:
            relative_infile = None
            relative_outfile = None
        
        self.pre_run()
        self.update_task_param()   
        self.update_task_info()

        relative_infile = self.input_filename

        # relative paths
        if self.task_info.output.get('txt_out'):
            relative_outfile = Path(self.task_info.output['txt_out'])

        self.octopus = Octopus(infile= relative_infile, outfile=relative_outfile,
                             directory=Path(self.engine_dir), **self.user_input)
    
    def update_task_param(self):
        """ Updates task parameters to engine-specific parameters"""

        task = self.task_name
        copy_input = copy.deepcopy(self.user_input)
        param = {
            'XYZCoordinates' : self.geom_file,
            'FromScratch' : 'yes'
        }
        param_copy = copy.deepcopy(param)
        copy_input.update(param)

        if task == tt.GROUND_STATE:
            # Set Calculation Mode expliciltly            
            param.update(create_oct_gs_inp(copy_input, self.geom_fpath))
            self.user_input = param            
            return

        elif task == tt.RT_TDDFT:            
            param_copy.update(self.dependent_tasks[0].param)
            gs_oct_param = create_oct_gs_inp(param_copy, self.geom_fpath)
            param.update(gs_oct_param)
            oct_td_dict = get_oct_kw_dict(copy_input,task)            
            param.update(oct_td_dict)
            self.user_input = param            
            return

        elif task == tt.COMPUTE_SPECTRUM:
            param.update(get_oct_kw_dict(copy_input, task))
            self.user_input = param  
            return 

        elif task == tt.TCM:
            pass

        elif task == tt.MO_POPULATION:
            pass
   
    def check_run_status(self):
        """Returns run_status bool and returncode value"""

        run_status = False
        if hasattr(self, 'submit_network'):
            check = self.task_info.network.get('sub_returncode', None)
        else:
            check = self.task_info.local.get('returncode', None)
        if check is None:
            raise TaskFailed("Job not completed.")
        else:
            if check != 0:
                run_status = False
            else:
                run_status = True
        return run_status, check

    def post_run(self):
        """Handles copying output folders to task directory from octopus specific folder structure"""
        log_files = list(Path(self.output_dir).iterdir())
        for log in log_files:
            shutil.copy(Path(self.output_dir)/log, Path(self.task_dir))
        task = self.task_name
        if task == tt.GROUND_STATE:
            folders = ['exec']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.task_dir)/ item)
        elif task == tt.RT_TDDFT:
            folders = ['td.general']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.task_dir)/ item)
        elif task == tt.COMPUTE_SPECTRUM:              
            folders = ['cross_section_vector']
            for item in folders:
                shutil.copy(Path(self.engine_dir) / item, Path(self.task_dir)/ item)

    def write_input(self, template=None):
        """ Gets the input filepath and writes\n
        Creates task_dir and ccopies the input file to it after writing"""
        inp_filepath = self.wf_dir / str(self.task_info.input['engine_input']['path'])

        self.create_task_dir()             
        self.octopus.write_input(self.template)  
        shutil.copy(inp_filepath, self.task_dir / 'inp')      

    def create_task_dir(self):
        """Craetes task dir and stores to task info"""
        # relative paths
        self.task_info.output['task_dir'] = str(self.task_dir.relative_to(self.wf_dir))
        self.create_directory(self.task_dir)  

    def create_template(self):
        self.template = self.octopus.create_input()
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = self.template

    def create_job_script(self, np=1, remote_path=None) -> list:
        
        job_script = super().create_job_script()      
        ofilename = 'log/'+ str(self.task_data['out_log'])
       
        engine_path = copy.deepcopy(self.engine_path)
        mpi_path = copy.deepcopy(self.mpi_path)
        cd_path = self.wf_dir / self.engine_dir

        if remote_path:
            mpi_path = 'mpirun'
            engine_path = 'octopus'
            cd_path = Path(remote_path) / self.wf_dir.parents[0].name / self.wf_dir.name / 'octopus'
        
        extra_cmd = None
        if self.task_name == tt.GROUND_STATE and self.user_input['ExtraStates'] != 0:
                unocc_ofilename = Path(octopus_data['unoccupied_task']['out_log']).relative_to('octopus')
                extra_cmd = "perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp\n"
                extra_cmd = extra_cmd + f"{mpi_path} -np {np:d} {str(engine_path)} &> {str(unocc_ofilename)}"
                
        if self.task_name == tt.COMPUTE_SPECTRUM:
            engine_path = Path(self.engine_path).parent / 'oct-propagation_spectrum'

        engine_cmd = str(engine_path) + ' ' + '&>' + ' ' + str(ofilename)
        job_script = assemable_job_cmd(engine_cmd, np, cd_path, mpi_path=mpi_path, remote=bool(remote_path),
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
        out_log = Path(self.output_dir) / self.task_data.get('out_log')
        if self.check_output():
            return self.read_log(out_log)

    def plot(self,**kwargs):
        """Method related to plot in post-processing"""
        from litesoph.visualization.plot_spectrum import plot_spectrum,plot_multiple_column

        if self.task_name == tt.COMPUTE_SPECTRUM:
            energy_min = self.task_info.param['e_min']
            energy_max = self.task_info.param['e_max']
            spec_file = self.task_data['spectra_file'][0]
            file = self.task_dir / str(spec_file)
            img = file.parent / f"spectrum.png"
            plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)", xlimit=(float(energy_min), float(energy_max)))
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
            # self.occ = self.octopus.read_info()[0] 

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
        if self.check_run_status()[0]:
            self.post_run()

    def get_ksd_popln(self):
        td_info = self.dependent_tasks[1] 
        if td_info:
            _axis = td_info.param['polarization']
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
            elif self.task_name == tt.MO_POPULATION:
                from litesoph.post_processing.mo_population import calc_population_diff
                population_file = self.task_dir/self.task_data.get('population_file')
                population_diff_file = self.task_dir/'population_diff.dat'
                [proj_obj, population_array] = self.octopus.compute_populations(out_file = population_file, proj=proj_read)
                
                calc_population_diff(homo_index=below_homo,infile=population_file, outfile=population_diff_file)
            self.task_info.local['returncode'] = 0
            # self.local_cmd_out = [0]
        except Exception:
            self.task_info.local['returncode'] = 1
            # self.local_cmd_out = [1]

##---------------------------------------------------------------------------------------------------------------

pol_list2dir = [([1,0,0], 1),
                ([0,1,0], 2),
                ([0,0,1], 3)]

property_dict = {
    "default": ["energy", "multipoles"],
    "ksd": ["td_occup"],
    "mo_population": ["td_occup"]}

def get_oct_kw_dict(inp_dict:dict, task_name:str):
    """ Acts on the input dictionary to return Octopus specifc keyword dictionary
        inp_dict: dictionary from gui
        task_name
    """
    from litesoph.utilities.units import as_to_au

    if 'rt_tddft' in task_name:
        t_step = inp_dict.pop('time_step')
        property_list = inp_dict.pop('properties')
        laser = inp_dict.pop('laser', None)
                  
        ### add appropriate keywords from property list
        _list = []
        td_out_list = []
        for item in property_list:
            td_key = property_dict.get(item, ["energy", "multipoles"])
            if td_key:
                _list.extend(td_key)
        td_list = list(set(_list))
        for item in td_list:
            td_out_list.append([item])
        
        _dict ={
        'CalculationMode': 'td', 
        'TDPropagator': 'aetrs',
        'TDMaxSteps': inp_dict.pop('number_of_steps'),
        'TDTimeStep':round(t_step*as_to_au, 3),
        'TDOutput': td_out_list ,
        'TDOutputComputeInterval':inp_dict.pop('output_freq')
        }

        if laser:
            # State Preparation/Pump-Probe
            assert isinstance(laser, list)
            _dict2update = {'task': 'rt_tddft_laser'}
                
            td_functions_list = []
            td_ext_fields_list = []

            for i, laser_inp in enumerate(laser):
                laser_type = laser_inp.get("type")
                pol_list = laser_inp.get('polarization')    

                if laser_type != "delta":
                    # for laser other than delta pulse
                    # Construct the td_functions, ext fields block
                    laser_str = "laser"+str(i)
                    td_functions_list.append(get_td_function(laser_dict=laser_inp,
                                            laser_type= laser_type,
                                            td_function_name=laser_str
                                            ))
                    td_ext_field = ['electric_field',
                                pol_list[0],pol_list[1],pol_list[2],
                                str(laser[i]['frequency'])+"*eV",
                                str('"'+laser_str+'"')
                                ]
                    td_ext_fields_list.append(td_ext_field)

                    _dict2update.update({
            'TDFunctions': td_functions_list,
            'TDExternalFields': td_ext_fields_list
                })

                else:
                    # Get dict for delta pulse
                    # td_laser_dict = laser[i]
                    pol_list = laser_inp.get('polarization') 

                    if isinstance(pol_list, list):      
                        for item in pol_list2dir:
                            if item[0] == pol_list:
                                pol_dir = item[1]
                    _dict2update.update({
                    "TDDeltaStrength": laser_inp.get('strength'),
                    "TDPolarizationDirection": pol_dir,
                    "TDDeltaKickTime":laser_inp.get('time0'),
                })
               
            # else:
            #     _dict2update = {'TDFunctions':[[str('"'+"envelope_gauss"+'"'),
            #                             'tdf_gaussian',
            #                             inp_dict.get('strength'),
            #                             laser[0]['sigma'],
            #                             laser[0]['time0']
            #                             ]],
            #             'TDExternalFields':[['electric_field',
            #                                 pol_list[0],pol_list[1],pol_list[2],
            #                                 str(laser[0]['frequency'])+"*eV",
            #                                 str('"'+"envelope_gauss"+'"')
            #                                 ]] }
        else:
            # Delta Kick for spectrum calculation
            pol_list = inp_dict.pop('polarization')
            if isinstance(pol_list, list):      
                for item in pol_list2dir:
                    if item[0] == pol_list:
                        pol_dir = item[1]

            _dict2update = {
                'TDDeltaStrength':inp_dict.get('strength'),
                'TDPolarizationDirection':pol_dir,
        }
        _dict.update(_dict2update)

    elif task_name == 'spectrum':
        delta_e = inp_dict.pop('delta_e')
        e_max = inp_dict.pop('e_max')
        e_min = inp_dict.pop('e_min') 
        
        _dict = {
        "UnitsOutput": 'eV_angstrom',
        "PropagationSpectrumEnergyStep": str(delta_e)+"*eV",
        "PropagationSpectrumMaxEnergy": str(e_max)+"*eV",
        "PropagationSpectrumMinEnergy": str(e_min)+"*eV"
        }
    return _dict

def calc_td_range(spacing:float):
    """ spacing:float = Grid-spacing in angstrom\n
    calculates max limit(in as) for time step specific to Octopus engine
    """

    from litesoph.utilities.units import ang_to_au, au_to_as
    h = spacing*ang_to_au
    dt = 0.0426-0.207*h+0.808*h*h
    max_dt_as = round(dt*au_to_as, 2)
    print(dt)
    return max_dt_as

def get_td_function(laser_dict:dict,laser_type:str,td_function_name:str = "envelope_gauss"):
    laser_td_function_map = {
        "gaussian": "tdf_gaussian"
    }
    # td_function block for gaussian pulse
    td_func = [str('"'+td_function_name+'"'),
                    laser_td_function_map.get(laser_type),
                    laser_dict.get('strength'),
                    laser_dict['sigma'],
                    laser_dict['time0']
                    ]
    return td_func
