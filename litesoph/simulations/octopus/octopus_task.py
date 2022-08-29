import copy
import shutil
from pathlib import Path
from litesoph.simulations.esmd import Task, TaskFailed, TaskNotImplementedError
from litesoph.simulations.octopus.octopus import Octopus
from litesoph.simulations.octopus.octopus_input import get_task
from litesoph import config

engine_dir = 'octopus'

engine_log_dir = f'{engine_dir}/log'
engine_inp_dir = f'{engine_dir}/inputs'

general_input_file = f'{engine_dir}/inp'

octopus_data = {    
    "unoccupied_task": {'out_log':f'{engine_log_dir}/unocc.log'},

    "ground_state": {'inp':general_input_file,
                    'task_inp': 'gs.inp',
                    'out_log': f'{engine_log_dir}/gs.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['SCF converged']},

    "rt_tddft_delta": {'inp':general_input_file,
                    'task_inp': 'td_delta.inp',
                    'out_log': f'{engine_log_dir}/delta.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['Finished writing information', 'Calculation ended']},   

    "rt_tddft_laser": {'inp':general_input_file,
                    'task_inp': 'td_laser.inp',
                    'out_log': f'{engine_log_dir}/laser.log',
                    'req' : ['coordinate.xyz']},

    "spectrum": {'inp':general_input_file,
                'task_inp': 'spec.inp',
                'out_log': f'{engine_log_dir}/spec.log',
                'req' : ['coordinate.xyz'],
                'spectra_file': [f'{engine_dir}/cross_section_vector']},

    "tcm": {'inp': None,
            'req':[f'{engine_dir}/static/info',
            f'{engine_dir}/td.general/projections'],
            'dir': 'ksd',
            'ksd_file': f'{engine_dir}/ksd/transwt.dat'},

    "mo_population":{'inp': None,
            'req':[f'{engine_dir}/static/info',
            f'{engine_dir}/td.general/projections'],
            'dir': 'population',
            'population_file': 'population.dat'}


    # "ksd": {'inp': f'{engine_dir}/ksd/oct.inp',
    #     'req':[f'{engine_dir}/static/info',
    #     f'{engine_dir}/td.general/projections'],
    #     'ksd_file': f'{engine_dir}/ksd/transwt.dat'}          
}

class OctopusTask(Task):
    """ Wrapper class to perform Octopus tasks """
    NAME = 'octopus'
    engine_tasks = ['ground_state', 'rt_tddft_delta', 'rt_tddft_laser','spectrum']
    added_post_processing_tasks = ['tcm', 'mo_population']

    def __init__(self, project_dir, lsconfig, status=None, **kwargs) -> None:        
        
        try:
            self.task_name = kwargs.pop('task')
        except KeyError:
            self.task_name = get_task(kwargs)
        # self.task_name = get_task(kwargs)

        if not self.task_name in octopus_data.keys(): 
            raise TaskNotImplementedError(f'{self.task_name} is not implemented.')

        self.task_data = octopus_data.get(self.task_name)
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = kwargs     
        self.create_engine(self.user_input)

    def create_engine(self, param):
        """ Creates Octopus class object """
        oct_dir = self.project_dir / engine_dir

        if self.task_name in self.added_post_processing_tasks:
            self.task_dir = self.project_dir/engine_dir/self.task_data.get('dir')
            self.create_directory(self.task_dir)
            self.octopus = Octopus(directory=oct_dir)  
            return      

        param['XYZCoordinates'] = str(self.project_dir / 'coordinate.xyz')
        param['FromScratch'] = 'yes'

        if self.task_name in self.engine_tasks:
            infile = self.task_data.get('inp')
            outfile = self.task_data.get('out_log')
            # self.infile = Path(infile).name
        
            # self.infile = Path(infile).relative_to(engine_dir)
            self.infile = 'inp'
            self.outfile = Path(outfile).relative_to(engine_dir)

            # indir = oct_dir / self.infile.parent
            indir = oct_dir / 'inputs'
            outdir = oct_dir /self.outfile.parent
            for dir in [indir, outdir]:
                self.create_directory(dir)
        
        if self.task_name in ["rt_tddft_delta","rt_tddft_laser"]:
            gs_from_status = self.status.get_status('octopus.ground_state.param')
            gs_copy = copy.deepcopy(gs_from_status) 
            gs_copy.pop("CalculationMode")
            param.update(gs_copy)
            td_output_list = [["energy"], ["multipoles"]]
            added_list = param.get("TDOutput", [])
            td_output_list.extend(added_list)
            param["TDOutput"] = td_output_list         
            
        self.user_input = param
        self.octopus = Octopus(infile= self.infile, outfile=self.outfile,
                             directory=oct_dir, **param)

    def write_input(self, template=None):
        self.octopus.write_input(template)
        copy_infile = self.project_dir / engine_inp_dir /self.task_data.get('task_inp')
        inp_file = self.project_dir / engine_dir / self.infile
        shutil.copy(inp_file, copy_infile)

    def create_template(self):
        self.template = self.octopus.create_input()

    def create_job_script(self, np=1, remote_path=None) -> list:
        
        job_script = super().create_job_script()

        ofilename = Path(self.task_data['out_log']).relative_to('octopus')
       
        def create_default_job_script(cmd:str=None):
            """ Creates Octopus job script format"""

            if cmd:
                cmd_suffix = cmd
            else:
                cmd_suffix = 'octopus'
            if remote_path:
                rpath = Path(remote_path) / self.project_dir.name / 'octopus'
                job_script.append(self.get_engine_network_job_cmd())
                job_script.append(f"cd {str(rpath)}")
                job_script.append(f"mpirun -np {np:d}  {cmd_suffix} > {str(ofilename)}")
                job_script.append(self.remote_job_script_last_line)
            else:
                lpath = self.project_dir / engine_dir
                job_script.append(f"cd {str(lpath)}")
                path_cmd = Path(self.engine_path).parent / cmd_suffix
                command = str(path_cmd) + ' ' + '&>' + ' ' + str(ofilename)
                if np > 1:
                    command = self.mpi_path + ' ' + '-np' + ' ' + str(np) + ' ' + command
                job_script.append(command)  

            return job_script

        if self.task_name in ["ground_state"] and self.user_input['ExtraStates'] != 0:
                unocc_ofilename = Path(octopus_data['unoccupied_task']['out_log']).relative_to(engine_dir)
                extra_cmd = ["cp inp gs.inp","perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp"]
                local_cmd = f"{str(self.mpi_path)} -np {np:d}  {str(self.engine_path)} &> {str(unocc_ofilename)}"
                remote_cmd = f"mpirun -np {np:d}  {str(self.engine_path)} &> {str(unocc_ofilename)}"
                job_script_var = create_default_job_script()
                job_script_var.extend(extra_cmd)
                if remote_path:
                    job_script_var.append(remote_cmd)
                else:
                    job_script_var.append(local_cmd)

        elif self.task_name == 'spectrum':
            job_script_var = create_default_job_script('oct-propagation_spectrum')
        else:
            job_script_var = create_default_job_script()
        
        self.job_script = "\n".join(job_script_var)
        return self.job_script

    def prepare_input(self):
        if self.task_name in self.added_post_processing_tasks:
            self.get_ksd_popln()
            return
        self.create_template()
        self.write_input(self.template)
        copy_infile = self.project_dir / engine_inp_dir /self.task_data.get('task_inp')
        inp_file = self.project_dir / engine_dir / self.infile
        shutil.copy(inp_file, copy_infile)
        self.create_job_script()
        self.write_job_script(self.job_script)

    def get_engine_log(self):
        out_log = self.project_dir / self.task_data.get('out_log')
        if self.check_output():
            return self.read_log(out_log)

    def plot(self,**kwargs):
        from litesoph.utilities.plot_spectrum import plot_spectrum,plot_multiple_column

        if self.task_name == 'spectrum':
            pol =  self.status.get_status('octopus.rt_tddft_delta.param.TDPolarizationDirection')
            spec_file = self.task_data['spectra_file'][int(pol-1)]
            file = Path(self.project_dir) / spec_file
            img = file.parent / f"spec_{pol}.png"
            plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")
            return

        if self.task_name == 'tcm': 
            from litesoph.utilities.job_submit import execute

            fmin = kwargs.get('fmin')
            fmax = kwargs.get('fmax')
            axis_limit = kwargs.get('axis_limit')

            path = Path(__file__)
            path_python = self.lsconfig.get('programs', 'python')['python']
            path_plotdmat = str(path.parents[2]/ 'visualization/octopus/plotdmat.py')

            ksd_file = self.project_dir / self.task_data['ksd_file']
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
        if self.task_name in ['tcm','mo_population']:
            return
        cmd = cmd + ' ' + self.BASH_filename
        self.sumbit_local.run_job(cmd)

    def get_ksd_popln(self):        
        _axis = self.get_pol_list(self.status)
        max_step = self.status.get_status('octopus.rt_tddft_delta.param.TDMaxSteps')
        output_freq = self.status.get_status('octopus.rt_tddft_delta.param.TDOutputComputeInterval') 
        nt = int(max_step/output_freq) 
        below_homo = self.user_input['num_occupied_mo']
        above_lumo = self.user_input['num_unoccupied_mo']

        [occ,homo,lumo]=self.octopus.read_info()
        proj_read = self.octopus.read_projections(time_end= nt,
                                number_of_proj_occupied= below_homo,
                                number_of_proj_unoccupied=above_lumo,
                                axis=_axis)
        try:            
            if self.task_name == 'tcm':
                self.octopus.compute_ksd(proj=proj_read, out_directory=self.task_dir)
            elif self.task_name == 'mo_population':
                from litesoph.post_processing.mo_population import calc_population_diff
                population_file = self.task_dir/self.task_data.get('population_file')
                [proj_obj, population_array] = self.octopus.compute_populations(out_file = population_file, proj=proj_read)
                population_diff_file = self.task_dir/'population_diff.dat'
                calc_population_diff(homo_index=occ,infile=population_file, outfile=population_diff_file)
            self.local_cmd_out = [0]
        except Exception:
            self.local_cmd_out = [1]

    def get_pol_list(self, status):
        e_pol = status.get_status('octopus.rt_tddft_delta.param.TDPolarizationDirection')
        assign_pol_list ={
            1 : [1,0,0],
            2 : [0,1,0],
            3 : [0,0,1]
        }
        return(assign_pol_list.get(e_pol))
