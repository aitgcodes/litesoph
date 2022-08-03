from pathlib import Path
import pathlib

from litesoph.simulations.esmd import Task
from litesoph.simulations.nwchem.nwchem import NWChem
from litesoph import config


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

'restart': 'nwchem/restart'
}


class NwchemTask(Task):

    NAME = 'nwchem'

    implemented_task = ['ground_state', 'rt_tddft_delta', 'rt_tddft_laser', 'spectrum']

    def __init__(self, project_dir, lsconfig, status=None, **kwargs) -> None:
        
        
        self.task_name = kwargs.pop('task', 'ground_state')
        
        
        if not self.task_name in nwchem_data.keys(): 
            raise Exception(f'{self.task_name} is not implemented.')

        self.task_data = nwchem_data.get(self.task_name)
        super().__init__('nwchem',status, project_dir, lsconfig)
        self.param = kwargs
        self.create_engine(self.param)
    
    def create_engine(self, param):
        infile_ext = '.nwi'
        outfile_ext = '.nwo'
        self.task_dir = self.project_dir / 'nwchem' / self.task_data.get('dir')
        
        param['perm'] = str(self.task_dir.parent / 'restart')
        param['geometry'] = str(self.project_dir / 'coordinate.xyz')
        
        if 'rt_tddft' in self.task_name:
            param['restart_kw'] = 'restart'
            param['basis'] = self.status.get_status('nwchem.ground_state.param').get('basis')
        self.user_input = param

        if 'spectrum' == self.task_name:
            file_name = nwchem_data['rt_tddft_delta'].get('file_name')
        else:   
            file_name = self.task_data.get('file_name')

        self.infile = file_name + infile_ext
        self.outfile = file_name + outfile_ext
        label = str(self.project_dir.name)

        self.nwchem = NWChem(infile= self.infile, outfile=self.outfile, 
                            label=label, directory=self.task_dir, **param)

    def write_input(self, template=None):
        self.create_directory(self.task_dir)
        self.nwchem.write_input(template)

    def create_template(self):
        self.template = self.nwchem.create_input()

    def create_spectrum_cmd(self, remote=False ):

        td_out = self.task_data['out_log']

        td_out = self.project_dir / td_out
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

        spec_cmd = f'{path_python} {spectrum_file} {self.pol}.dat spec_{self.pol}.dat'
        
        return [dm_cmd, spec_cmd]

    def create_job_script(self, np=1, remote_path=None, remote=None) -> list:

        ifilename =  self.infile
        ofilename = self.outfile
        command = self.lsconfig.get('engine', 'nwchem')

        job_script = super().create_job_script()

        if 'spectrum' in self.task_name:
            
            self.create_directory(self.task_dir)
            path = self.task_dir
            if remote_path:
                path = Path(remote_path) / self.task_dir.relative_to(self.project_dir.parent)
            job_script.append(f"cd {str(path)}")
            job_script.extend(self.create_spectrum_cmd(bool(remote_path)))
            self.job_script = "\n".join(job_script)
            self.write_job_script()
            return self.job_script

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

    def run_job_local(self, cmd):
        super().run_job_local(cmd)

    def plot(self):
        from litesoph.utilities.plot_spectrum import plot_spectrum

        file = self.task_dir / f"spec_{self.pol}.dat"
        img = file.parent / f"spec_{self.pol}.png"
        plot_spectrum(file,img,0, 1, "Energy(eV)","Strength")

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