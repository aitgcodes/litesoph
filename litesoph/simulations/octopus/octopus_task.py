import copy
import os
from pathlib import Path
from litesoph.simulations.esmd import Task
from litesoph.simulations.octopus.octopus import Octopus
from litesoph.simulations.octopus.octopus_input import get_task
from litesoph import config

engine_dir = 'octopus'

engine_log_dir = f'{engine_dir}/log'

general_input_file = f'{engine_dir}/inp'

octopus_data = {    
    "unoccupied_task": {'out_log':f'{engine_log_dir}/unocc.log'},

    "ground_state": {'inp':general_input_file,
                    'out_log': f'{engine_log_dir}/gs.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['SCF converged']},

    "rt_tddft_delta": {'inp':general_input_file,
                    'out_log': f'{engine_log_dir}/delta.log',
                    'req' : ['coordinate.xyz'],
                    'check_list':['Finished writing information', 'Calculation ended']},   

    "rt_tddft_laser": {'inp':general_input_file,
                    'out_log': f'{engine_log_dir}/laser.log',
                    'req' : ['coordinate.xyz']},

    "spectrum": {'inp':general_input_file,
                'out_log': f'{engine_log_dir}/spec.log',
                'req' : ['coordinate.xyz'],
                'spectra_file': [f'{engine_dir}/cross_section_vector']},

    # "ksd": {'inp': f'{engine_dir}/ksd/oct.inp',
    #     'req':[f'{engine_dir}/static/info',
    #     f'{engine_dir}/td.general/projections'],
    #     'ksd_file': f'{engine_dir}/ksd/transwt.dat'}          
}

class OctopusTask(Task):
    """ Wrapper class to perform Octopus tasks """
    NAME = 'octopus'

    def __init__(self, project_dir, lsconfig, status=None, **kwargs) -> None:        

        self.task_name = get_task(kwargs)

        if not self.task_name in octopus_data.keys(): 
            raise Exception(f'{self.task_name} is not implemented.')

        self.task_data = octopus_data.get(self.task_name)
        super().__init__('octopus',status, project_dir, lsconfig)
        self.param = kwargs        
        self.create_engine(self.param)

    def create_engine(self, param):
        """ Creates Octopus class object """

        oct_dir = self.project_dir / engine_dir
        infile = self.task_data.get('inp')
        outfile = self.task_data.get('out_log')
        # self.infile = Path(infile).name
        self.infile = Path(infile).relative_to(engine_dir)
        self.outfile = Path(outfile).relative_to(engine_dir)

        indir = oct_dir / self.infile.parent
        outdir = oct_dir /self.outfile.parent
        for dir in [indir, outdir]:
            if not dir.is_dir():
                os.makedirs(dir)

        param['XYZCoordinates'] = str(self.project_dir / 'coordinate.xyz')
        param['FromScratch'] = 'yes'
        
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

    def create_template(self):
        self.template = self.octopus.create_input()

    def create_job_script(self, np=1, remote_path=None) -> list:
        
        job_script = super().create_job_script()

        ofilename = Path(self.task_data['out_log']).relative_to('octopus')

        cmd_mpi = config.get_mpi_command(self.NAME, self.lsconfig)    
        path_octopus = self.lsconfig.get('engine', 'octopus')
       
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
                path_cmd = Path(path_octopus).parent / cmd_suffix
                command = str(path_cmd) + ' ' + '&>' + ' ' + str(ofilename)
                if np > 1:
                    command = cmd_mpi + ' ' + '-np' + ' ' + str(np) + ' ' + command
                job_script.append(command)  

            return job_script

        if self.task_name in ["ground_state"] and self.user_input['ExtraStates'] != 0:
                unocc_ofilename = Path(octopus_data['unoccupied_task']['out_log']).relative_to(engine_dir)
                extra_cmd = ["cp inp gs.inp","perl -i -p0e 's/CalculationMode = gs/CalculationMode = unocc/s' inp"]
                local_cmd = f"{str(cmd_mpi)} -np {np:d}  {str(path_octopus)} &> {str(unocc_ofilename)}"
                remote_cmd = f"mpirun -np {np:d}  {str(path_octopus)} &> {str(unocc_ofilename)}"
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
        self.create_template()
        self.write_input(self.template)
        self.create_job_script()
        self.write_job_script(self.job_script)

    def plot(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        pol =  self.status.get_status('octopus.rt_tddft_delta.param.TDPolarizationDirection')
        spec_file = self.task_data['spectra_file'][int(pol-1)]
        file = Path(self.project_dir) / spec_file
        img = file.parent / f"spec_{pol}.png"
        plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")

    @staticmethod
    def get_engine_network_job_cmd():

        job_script = """
##### Please Provide the Excutable Path or environment of Octopus or load the module

#spack load octopus
#module load octopus"""
        return job_script
    
    def create_ksd_input(self, user_input:dict):
        pass