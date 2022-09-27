import copy
import shutil
from pathlib import Path
from litesoph.simulations.esmd import Task, TaskFailed, TaskNotImplementedError, assemable_job_cmd
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

        if not self.task_name in octopus_data.keys(): 
            raise TaskNotImplementedError(f'{self.task_name} is not implemented.')

        self.task_data = octopus_data.get(self.task_name)
        super().__init__('octopus',status, project_dir, lsconfig)
        self.user_input = kwargs     
        self.create_engine(self.user_input)

    def create_engine(self, param):
        """ Creates Octopus class object """
        oct_dir = self.project_dir / engine_dir
        self.network_done_file = self.project_dir / engine_dir / 'Done'
        if 'out_log' in self.task_data.keys():
            self.engine_log = self.project_dir / self.task_data.get('out_log')
        
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

            self.infile = 'inp'
            self.outfile = Path(outfile).relative_to(engine_dir)

            indir = oct_dir / 'inputs'
            outdir = oct_dir /self.outfile.parent
            for dir in [indir, outdir]:
                self.create_directory(dir)
        
        if self.task_name in ["rt_tddft_delta","rt_tddft_laser"]:
            inp_dict = get_oct_kw_dict(param, self.task_name)
            gs_from_status = self.status.get('octopus.ground_state.param')
            gs_copy = copy.deepcopy(gs_from_status) 
            gs_copy.pop("CalculationMode")
            inp_dict.update(gs_copy)

            td_output_list = [["energy"], ["multipoles"]]
            added_list = inp_dict.get("TDOutput", [])
            td_output_list.extend(added_list)
            inp_dict["TDOutput"] = td_output_list
            param.update(inp_dict)  

        elif self.task_name == 'spectrum':
            inp_dict = get_oct_kw_dict(param, self.task_name)
            param.update(inp_dict) 

        elif self.task_name == 'tcm':
            param.update({'output':['DMAT', 'POP']})

        self.user_input = param
        self.octopus = Octopus(infile= self.infile, outfile=self.outfile,
                             directory=oct_dir, **param)

    def write_input(self, template=None):
        self.template = template
        self.octopus.write_input(self.template)
        copy_infile = self.project_dir / engine_inp_dir /self.task_data.get('task_inp')
        inp_file = self.project_dir / engine_dir / self.infile
        shutil.copy(inp_file, copy_infile)

    def create_template(self):
        self.template = self.octopus.create_input()

    def create_job_script(self, np=1, remote_path=None) -> list:
        
        job_script = super().create_job_script()
        
        ofilename = Path(self.task_data['out_log']).relative_to('octopus')
       
        engine_path = copy.deepcopy(self.engine_path)
        mpi_path = copy.deepcopy(self.mpi_path)
        cd_path = self.project_dir / engine_dir

        if remote_path:
            mpi_path = 'mpirun'
            engine_path = 'octopus'
            cd_path = Path(remote_path) / self.project_dir.name / 'octopus'
        
        extra_cmd = None
        if self.task_name in ["ground_state"] and self.user_input['ExtraStates'] != 0:
                unocc_ofilename = Path(octopus_data['unoccupied_task']['out_log']).relative_to(engine_dir)
                extra_cmd = "perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp\n"
                extra_cmd = extra_cmd + f"{mpi_path} -np {np:d} {str(engine_path)} &> {str(unocc_ofilename)}"
                
        if self.task_name == 'spectrum':
            engine_path = Path(self.engine_path).parent / 'oct-propagation_spectrum'

        engine_cmd = str(engine_path) + ' ' + '&>' + ' ' + str(ofilename)
        job_script = assemable_job_cmd(engine_cmd, np, cd_path, mpi_path=mpi_path, remote=bool(remote_path),
                                                module_load_block=self.get_engine_network_job_cmd(),
                                                extra_block=extra_cmd)
        self.job_script = job_script
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
            pol =  self.status.get('octopus.rt_tddft_delta.param.TDPolarizationDirection')
            energy_min = self.user_input['PropagationSpectrumMinEnergy']
            energy_max = self.user_input['PropagationSpectrumMaxEnergy']
            e_min_eV = str(energy_min).rpartition('*')[0]
            e_max_eV = str(energy_max).rpartition('*')[0]
            spec_file = self.task_data['spectra_file'][0]
            file = Path(self.project_dir) / spec_file
            img = file.parent / f"spec_{pol}.png"
            plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)", xlimit=(float(e_min_eV), float(e_max_eV)))
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
        max_step = self.status.get('octopus.rt_tddft_delta.param.TDMaxSteps')
        output_freq = self.status.get('octopus.rt_tddft_delta.param.TDOutputComputeInterval') 
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
        e_pol = status.get('octopus.rt_tddft_delta.param.TDPolarizationDirection')
        assign_pol_list ={
            1 : [1,0,0],
            2 : [0,1,0],
            3 : [0,0,1]
        }
        return(assign_pol_list.get(e_pol))

##---------------------------------------------------------------------------------------------------------------

pol_list2dir = [([1,0,0], 1),
                ([0,1,0], 2),
                ([0,0,1], 3)]

property_dict = {
    "default": ["energy", "multipoles"],
    "ksd": "td_occup",
    "mo_population": "td_occup"}


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
            td_key = property_dict.get(item)
            if td_key:
                _list.append(td_key)
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
