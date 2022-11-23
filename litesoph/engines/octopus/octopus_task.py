import copy
import shutil
from pathlib import Path
from typing import Any, List, Dict, Union

from numpy import true_divide
from litesoph.common.task import Task, TaskFailed, TaskNotImplementedError, assemable_job_cmd
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
                    'check_list':['SCF converged']},

    tt.RT_TDDFT: {'inp':general_input_file,
                    'task_inp': 'td.inp',
                    'out_log': 'td.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['Finished writing information', 'Calculation ended']},

    "rt_tddft_delta": {'inp':general_input_file,
                    'task_inp': 'td_delta.inp',
                    'out_log': 'delta.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['Finished writing information', 'Calculation ended']},   

    "rt_tddft_laser": {'inp':general_input_file,
                    'task_inp': 'td_laser.inp',
                    'out_log': f'{engine_log_dir}/laser.log',
                    'req' : ['coordinate.xyz']},

    tt.COMPUTE_SPECTRUM: {'inp':general_input_file,
                'task_inp': 'spec.inp',
                'out_log': 'spec.log',
                'req' : ['coordinate.xyz'],
                'spectra_file': ['cross_section_vector']},

    tt.TCM: {'inp': None,
            'ksd_file': 'ksd/transwt.dat'},
            # 'req':[f'{engine_dir}/static/info',
            # f'{engine_dir}/td.general/projections'],
            # 'dir': 'ksd',
            # 'ksd_file': f'{engine_dir}/ksd/transwt.dat'},
    # "tcm": {'inp': None,
    #         'req':[f'{engine_dir}/static/info',
    #         f'{engine_dir}/td.general/projections'],
    #         'dir': 'ksd',
    #         'ksd_file': f'{engine_dir}/ksd/transwt.dat'},

    # "mo_population":{'inp': None,
    #         'req':[f'{engine_dir}/static/info',
    #         f'{engine_dir}/td.general/projections'],
    #         'dir': 'population',
    #         'population_file': 'population.dat'}


    # "ksd": {'inp': f'{engine_dir}/ksd/oct.inp',
    #     'req':[f'{engine_dir}/static/info',
    #     f'{engine_dir}/td.general/projections'],
    #     'ksd_file': f'{engine_dir}/ksd/transwt.dat'}          
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

        if not self.task_name in self.implemented_task: 
            raise TaskNotImplementedError(f'{self.task_name} is not implemented.')
        if dependent_tasks:
            self.dependent_tasks = dependent_tasks

        self.task_data = octopus_data.get(self.task_name)
        self.params = copy.deepcopy(self.task_info.param)        
        self.user_input = {}
        self.user_input['task'] = self.task_name
        self.user_input = self.params

        self.setup_task(self.user_input) 
    
    def setup_task(self, param:dict):               
        if self.task_name in self.added_post_processing_tasks:
            relative_infile = None
            relative_outfile = None
        self.pre_run()
        self.update_task_param()   
        self.update_task_info()

        relative_infile = self.input_filename
        if self.task_info.output.get('txt_out'):
            relative_outfile = Path(self.task_info.output['txt_out']).relative_to(self.engine_dir)

        self.octopus = Octopus(infile= relative_infile, outfile=relative_outfile,
                             directory=Path(self.engine_dir), **self.user_input)

    def pre_run(self):
        self.input_filename = 'inp'
        self.task_input_filename = self.task_data.get('task_inp', 'inp')
        self.geom_file = str(self.project_dir / 'coordinate.xyz')
        self.engine_dir = str(self.project_dir / 'octopus')
        self.task_dir = str(Path(self.engine_dir) / self.task_name)
        self.output_dir = str(Path(self.engine_dir) / 'log')
        self.task_info.input['engine_input']={}

        for dir in [self.engine_dir, self.output_dir]:
            self.create_directory(Path(dir))

        if self.task_name == tt.COMPUTE_SPECTRUM:
            td_info = self.dependent_tasks[0]
            if td_info:
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)
            return

        elif self.task_name == tt.TCM:
            
            td_info = self.dependent_tasks[1]
            if td_info:
                oct_td_folder_path = str(Path(self.engine_dir) / 'td.general')
                td_folder_path = str(Path(td_info.output['task_dir']) / 'td.general')
                shutil.copytree(src=td_folder_path, dst=oct_td_folder_path, dirs_exist_ok=True)

    def update_task_param(self):
        """ Updates param for the task and returns"""
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
            param.update(create_oct_gs_inp(copy_input))
            self.user_input = param            
            return

        elif task == tt.RT_TDDFT:            
            param_copy.update(self.dependent_tasks[0].param)
            gs_oct_param = create_oct_gs_inp(param_copy)
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
    
    def update_task_info(self, **kwargs):
        """ Updates self.task_info with current task info"""
        if self.task_name in self.added_post_processing_tasks:
            # self.task_info.output['txt_out'] = str(Path(self.output_dir) / self.task_data.get('out_log'), '')
            # self.task_info.output['out_files'] = str(Path(self.output_dir) / self.task_data.get('out_log'))
            return
            
        self.task_info.input['engine_input']['path'] = str(Path(self.engine_dir) / self.input_filename)
        self.task_info.output['txt_out'] = str(Path(self.output_dir) / self.task_data.get('out_log'))
    
    def check_run_status(self):
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
        task = self.task_name
        if task == tt.GROUND_STATE:
            folders = ['exec']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.copy_task_dir)/ item)
        elif task == tt.RT_TDDFT:
            folders = ['td.general']
            for item in folders:
                shutil.copytree(Path(self.engine_dir) / item, Path(self.copy_task_dir)/ item)
        elif task == tt.COMPUTE_SPECTRUM:              
            folders = ['cross_section_vector']
            for item in folders:
                shutil.copy(Path(self.engine_dir) / item, Path(self.copy_task_dir)/ item)

    def write_input(self, template=None):
        inp_filepath = self.task_info.input['engine_input']['path']

        self.create_task_dir()             
        self.octopus.write_input(self.template)        
        shutil.copy(inp_filepath, self.copy_task_dir / 'inp')
    
    def create_task_dir(self):
        self.copy_task_dir = get_new_directory(Path(self.task_dir))
        self.task_info.output['task_dir'] = str(self.copy_task_dir)

        self.create_directory(self.copy_task_dir)   

    def create_template(self):
        self.template = self.octopus.create_input()
        self.task_info.engine_param.update(self.user_input)
        self.task_info.input['engine_input']['data'] = self.template

    def create_job_script(self, np=1, remote_path=None) -> list:
        
        job_script = super().create_job_script()      
        ofilename = 'log/'+ str(self.task_data['out_log'])
       
        engine_path = copy.deepcopy(self.engine_path)
        mpi_path = copy.deepcopy(self.mpi_path)
        cd_path = self.project_dir / self.engine_dir

        if remote_path:
            mpi_path = 'mpirun'
            engine_path = 'octopus'
            cd_path = Path(remote_path) / self.project_dir.parents[0].name / self.project_dir.name / 'octopus'
        
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
        if self.task_name in self.added_post_processing_tasks:
            self.create_task_dir()
            self.get_ksd_popln()
            return
        self.create_template()
        self.write_input(self.template)
        self.create_job_script()
        self.write_job_script(self.job_script)     

    def get_engine_log(self):
        out_log = Path(self.output_dir) / self.task_data.get('out_log')
        if self.check_output():
            return self.read_log(out_log)

    def plot(self,**kwargs):
        from litesoph.visualization.plot_spectrum import plot_spectrum,plot_multiple_column

        if self.task_name == tt.COMPUTE_SPECTRUM:
            energy_min = self.task_info.param['e_min']
            energy_max = self.task_info.param['e_max']
            spec_file = self.task_data['spectra_file'][0]
            file = self.copy_task_dir / str(spec_file)
            img = file.parent / f"spectrum.png"
            plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)", xlimit=(float(energy_min), float(energy_max)))
            return        

        if self.task_name == tt.TCM: 
            from litesoph.common.job_submit import execute

            fmin = kwargs.get('fmin')
            fmax = kwargs.get('fmax')
            axis_limit = kwargs.get('axis_limit')

            path = Path(__file__)
            path_python = self.lsconfig.get('programs', 'python')['python']
            path_plotdmat = str(path.parents[2]/ 'visualization/octopus/plotdmat.py')

            ksd_file = self.copy_task_dir / 'transwt.dat'
            cmd = f'{path_python} {path_plotdmat} {ksd_file} {fmin} {fmax} {axis_limit} -i'
        
            result = execute(cmd, self.task_dir)
            
            if result[cmd]['returncode'] != 0:
                raise Exception(f"{result[cmd]['error']}")
            return

        if self.task_name == 'mo_population':
            # first check if the file exists already 
            import numpy as np
            from litesoph.post_processing.mo_population import create_states_index
            below_homo = kwargs.get('num_occupied_mo_plot',1)
            above_lumo = kwargs.get('num_unoccupied_mo_plot',1)
            population_diff_file = self.task_dir/'population_diff.dat'
            self.occ = self.octopus.read_info()[0]
            
            # time_unit = kwargs.get('time_unit')            
            column_range = (self.occ-below_homo+1, self.occ+above_lumo)
            legend_dict = create_states_index(num_below_homo=below_homo, num_above_lumo=above_lumo, homo_index=self.occ)
            
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
        self.sumbit_local.run_job(cmd)
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
                self.octopus.compute_ksd(proj=proj_read, out_directory=self.copy_task_dir)
            elif self.task_name == 'mo_population':
                from litesoph.post_processing.mo_population import calc_population_diff
                population_file = self.task_dir/self.task_data.get('population_file')
                [proj_obj, population_array] = self.octopus.compute_populations(out_file = population_file, proj=proj_read)
                population_diff_file = self.task_dir/'population_diff.dat'
                calc_population_diff(homo_index=occ,infile=population_file, outfile=population_diff_file)
            self.task_info.local['returncode'] = 0
            # self.local_cmd_out = [0]
        except Exception:
            self.task_info.local['returncode'] = 1
            # self.local_cmd_out = [1]

    # def get_pol_list(self, status):
    #     e_pol = status.get('octopus.rt_tddft_delta.param.TDPolarizationDirection')
    #     assign_pol_list ={
    #         1 : [1,0,0],
    #         2 : [0,1,0],
    #         3 : [0,0,1]
    #     }
    #     return(assign_pol_list.get(e_pol))

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
        pol_list = inp_dict.pop('polarization')
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
            _dict2update = {'TDFunctions':[[str('"'+"envelope_gauss"+'"'),
                                    'tdf_gaussian',
                                    inp_dict.get('strength'),
                                    laser['sigma'],
                                    laser['time0']
                                    ]],
                    'TDExternalFields':[['electric_field',
                                        pol_list[0],pol_list[1],pol_list[2],
                                        str(laser['frequency'])+"*eV",
                                        str('"'+"envelope_gauss"+'"')
                                        ]] }
        else:
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
    """ calculates max limit for time step specific to Octopus engine"""

    from litesoph.utilities.units import ang_to_au, au_to_as
    h = spacing*ang_to_au
    dt = 0.0426-0.207*h+0.808*h*h
    max_dt_as = round(dt*au_to_as, 2)
    print(dt)
    return max_dt_as
  
#------------------------------------------------------------------------------------------------------------

# class OctopusTask(Task):
#     """ Wrapper class to perform Octopus tasks """
#     NAME = 'octopus'
#     engine_tasks = ['ground_state', 'rt_tddft_delta', 'rt_tddft_laser','spectrum']
#     added_post_processing_tasks = ['tcm', 'mo_population']

#     def __init__(self, project_dir, lsconfig, status=None, **kwargs) -> None:   
#         try:
#             self.task_name = kwargs.pop('task')
#         except KeyError:
#             self.task_name = get_task(kwargs)

#         if not self.task_name in octopus_data.keys(): 
#             raise TaskNotImplementedError(f'{self.task_name} is not implemented.')

#         self.task_data = octopus_data.get(self.task_name)
#         super().__init__('octopus',status, project_dir, lsconfig)
#         self.user_input = kwargs     
#         self.create_engine(self.user_input)

#     def create_engine(self, param):
#         """ Creates Octopus class object """
#         oct_dir = self.project_dir / engine_dir
#         self.network_done_file = self.project_dir / engine_dir / 'Done'
#         if 'out_log' in self.task_data.keys():
#             self.engine_log = self.project_dir / self.task_data.get('out_log')
        
#         if self.task_name in self.added_post_processing_tasks:
#             self.task_dir = self.project_dir/engine_dir/self.task_data.get('dir')
            # self.create_directory(self.task_dir)
#             self.octopus = Octopus(directory=oct_dir)  
#             return      

#         param['XYZCoordinates'] = str(self.project_dir / 'coordinate.xyz')
#         param['FromScratch'] = 'yes'

#         if self.task_name in self.engine_tasks:
#             infile = self.task_data.get('inp')
#             outfile = self.task_data.get('out_log')

#             self.infile = 'inp'
#             self.outfile = Path(outfile).relative_to(engine_dir)

#             indir = oct_dir / 'inputs'
#             outdir = oct_dir /self.outfile.parent
#             for dir in [indir, outdir]:
#                 self.create_directory(dir)

#         if self.task_name == 'ground_state':
#             from litesoph.gui.engine_views.octopus_views.gs2oct import create_oct_gs_inp
#             oct_gs_dict = create_oct_gs_inp(param)
#             param = oct_gs_dict

#         if self.task_name in ["rt_tddft_delta","rt_tddft_laser"]:
#             inp_dict = get_oct_kw_dict(param, self.task_name)
#             gs_from_status = self.status.get('octopus.ground_state.param')
#             gs_copy = copy.deepcopy(gs_from_status) 
#             gs_copy.pop("CalculationMode")
#             inp_dict.update(gs_copy)

#             td_output_list = [["energy"], ["multipoles"]]
#             added_list = inp_dict.get("TDOutput", [])
#             td_output_list.extend(added_list)
#             inp_dict["TDOutput"] = td_output_list
#             param.update(inp_dict)  

#         elif self.task_name == 'spectrum':
#             inp_dict = get_oct_kw_dict(param, self.task_name)
#             param.update(inp_dict) 

#         elif self.task_name == 'tcm':
#             param.update({'output':['DMAT', 'POP']})

#         self.user_input = param
#         self.octopus = Octopus(infile= self.infile, outfile=self.outfile,
#                              directory=oct_dir, **param)

#     def write_input(self, template=None):
#         self.template = template
#         self.octopus.write_input(self.template)
#         copy_infile = self.project_dir / engine_inp_dir /self.task_data.get('task_inp')
#         inp_file = self.project_dir / engine_dir / self.infile
#         shutil.copy(inp_file, copy_infile)

#     def create_template(self):
#         self.template = self.octopus.create_input()

#     def create_job_script(self, np=1, remote_path=None) -> list:
        
#         job_script = super().create_job_script()
        
#         ofilename = Path(self.task_data['out_log']).relative_to('octopus')
       
#         engine_path = copy.deepcopy(self.engine_path)
#         mpi_path = copy.deepcopy(self.mpi_path)
#         cd_path = self.project_dir / engine_dir

#         if remote_path:
#             mpi_path = 'mpirun'
#             engine_path = 'octopus'
#             cd_path = Path(remote_path) / self.project_dir.name / 'octopus'
        
#         extra_cmd = None
#         if self.task_name in ["ground_state"] and self.user_input['ExtraStates'] != 0:
#                 unocc_ofilename = Path(octopus_data['unoccupied_task']['out_log']).relative_to(engine_dir)
#                 extra_cmd = "perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp\n"
#                 extra_cmd = extra_cmd + f"{mpi_path} -np {np:d} {str(engine_path)} &> {str(unocc_ofilename)}"
                
#         if self.task_name == 'spectrum':
#             engine_path = Path(self.engine_path).parent / 'oct-propagation_spectrum'

#         engine_cmd = str(engine_path) + ' ' + '&>' + ' ' + str(ofilename)
#         job_script = assemable_job_cmd(engine_cmd, np, cd_path, mpi_path=mpi_path, remote=bool(remote_path),
#                                                 module_load_block=self.get_engine_network_job_cmd(),
#                                                 extra_block=extra_cmd)
#         self.job_script = job_script
#         return self.job_script

#     def prepare_input(self):
#         if self.task_name in self.added_post_processing_tasks:
#             self.get_ksd_popln()
#             return
#         self.create_template()
#         self.write_input(self.template)
#         copy_infile = self.project_dir / engine_inp_dir /self.task_data.get('task_inp')
#         inp_file = self.project_dir / engine_dir / self.infile
#         shutil.copy(inp_file, copy_infile)
#         self.create_job_script()
#         self.write_job_script(self.job_script)

#     def get_engine_log(self):
#         out_log = self.project_dir / self.task_data.get('out_log')
#         if self.check_output():
#             return self.read_log(out_log)

#     def plot(self,**kwargs):
#         from litesoph.visualization.plot_spectrum import plot_spectrum,plot_multiple_column

#         if self.task_name == 'spectrum':
#             pol =  self.status.get('octopus.rt_tddft_delta.param.TDPolarizationDirection')
#             energy_min = self.user_input['PropagationSpectrumMinEnergy']
#             energy_max = self.user_input['PropagationSpectrumMaxEnergy']
#             e_min_eV = str(energy_min).rpartition('*')[0]
#             e_max_eV = str(energy_max).rpartition('*')[0]
#             spec_file = self.task_data['spectra_file'][0]
#             file = Path(self.project_dir) / spec_file
#             img = file.parent / f"spec_{pol}.png"
#             plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)", xlimit=(float(e_min_eV), float(e_max_eV)))
#             return

#         if self.task_name == 'tcm': 
#             from litesoph.common.job_submit import execute

#             fmin = kwargs.get('fmin')
#             fmax = kwargs.get('fmax')
#             axis_limit = kwargs.get('axis_limit')

#             path = Path(__file__)
#             path_python = self.lsconfig.get('programs', 'python')['python']
#             path_plotdmat = str(path.parents[2]/ 'visualization/octopus/plotdmat.py')

#             ksd_file = self.project_dir / self.task_data['ksd_file']
#             cmd = f'{path_python} {path_plotdmat} {ksd_file} {fmin} {fmax} {axis_limit} -i'
        
#             result = execute(cmd, self.task_dir)
            
#             if result[cmd]['returncode'] != 0:
#                 raise Exception(f"{result[cmd]['error']}")
#             return

#         if self.task_name == 'mo_population':
#             # first check if the file exists already 
#             import numpy as np
#             from litesoph.post_processing.mo_population import create_states_index
#             below_homo = kwargs.get('num_occupied_mo_plot',1)
#             above_lumo = kwargs.get('num_unoccupied_mo_plot',1)
#             population_diff_file = self.task_dir/'population_diff.dat'
#             self.occ = self.octopus.read_info()[0]
            
#             # time_unit = kwargs.get('time_unit')            
#             column_range = (self.occ-below_homo+1, self.occ+above_lumo)
#             legend_dict = create_states_index(num_below_homo=below_homo, num_above_lumo=above_lumo, homo_index=self.occ)
            
#             population_data = np.loadtxt(population_diff_file)            
#             plot_multiple_column(population_data, column_list=column_range, column_dict=legend_dict, xlabel='Time (in h_cut/eV)')
#             return        

#     @staticmethod
#     def get_engine_network_job_cmd():

#         job_script = """
# ##### Please Provide the Excutable Path or environment of Octopus or load the module

# #spack load octopus
# #module load octopus"""
#         return job_script

#     def run_job_local(self,cmd):
#         if self.task_name in ['tcm','mo_population']:
#             return
#         cmd = cmd + ' ' + self.BASH_filename
#         self.sumbit_local.run_job(cmd)

#     def get_ksd_popln(self):        
#         _axis = self.get_pol_list(self.status)
#         max_step = self.status.get('octopus.rt_tddft_delta.param.TDMaxSteps')
#         output_freq = self.status.get('octopus.rt_tddft_delta.param.TDOutputComputeInterval') 
#         nt = int(max_step/output_freq) 
#         below_homo = self.user_input['num_occupied_mo']
#         above_lumo = self.user_input['num_unoccupied_mo']

#         [occ,homo,lumo]=self.octopus.read_info()
#         proj_read = self.octopus.read_projections(time_end= nt,
#                                 number_of_proj_occupied= below_homo,
#                                 number_of_proj_unoccupied=above_lumo,
#                                 axis=_axis)
#         try:            
#             if self.task_name == 'tcm':
#                 self.octopus.compute_ksd(proj=proj_read, out_directory=self.task_dir)
#             elif self.task_name == 'mo_population':
#                 from litesoph.post_processing.mo_population import calc_population_diff
#                 population_file = self.task_dir/self.task_data.get('population_file')
#                 [proj_obj, population_array] = self.octopus.compute_populations(out_file = population_file, proj=proj_read)
#                 population_diff_file = self.task_dir/'population_diff.dat'
#                 calc_population_diff(homo_index=occ,infile=population_file, outfile=population_diff_file)
#             self.local_cmd_out = [0]
#         except Exception:
#             self.local_cmd_out = [1]

#     def get_pol_list(self, status):
#         e_pol = status.get('octopus.rt_tddft_delta.param.TDPolarizationDirection')
#         assign_pol_list ={
#             1 : [1,0,0],
#             2 : [0,1,0],
#             3 : [0,0,1]
#         }
#         return(assign_pol_list.get(e_pol))

