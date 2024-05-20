from pathlib import Path
import copy
import numpy as np

from .nwchem_task import (BaseNwchemTask,
                        tt,
                        plot_spectrum,
                        get_new_directory,
                        get_pol_and_tag,
                        assemable_job_cmd,
                        NWChem)



class ComputeSpectrum(BaseNwchemTask):


    def create_engine(self, param):
        label = str(self.project_dir.name)
        self.network_done_file = self.task_dir / 'Done'

        outfile = self.directory / self.dependent_tasks[0].output.get('txt_out')

        self.nwchem = NWChem(outfile=outfile, 
                        label=label, directory=self.task_dir)

    def _create_spectrum_cmd(self, remote=False ):

        td_out = str(self.directory / self.dependent_tasks[0].output.get('txt_out'))

        self.pol, tag = get_pol_and_tag(self.dependent_tasks[0])

        path = Path(__file__)

        if remote:
            path_python = 'python3'
        else:
            path_python = self.python_path

        nw_rtparse = str(path.parent /'nwchem_read_rt.py')
        spectrum_file = str(path.parent / 'spectrum.py')
        
        dm_cmd = f'{path_python} {nw_rtparse} -x dipole -p {self.pol} -t {tag} {td_out} > {self.pol}.dat'

        spec_cmd = f'{path_python} {spectrum_file} dipole.dat spec_{self.pol}.dat'
        
        return spec_cmd

    def compute_spectrum(self):
        self.create_directory(self.task_dir)
        
        td_out = str(self.directory / self.dependent_tasks[0].output.get('txt_out'))

        self.pol, tag = get_pol_and_tag(self.dependent_tasks[0])
        self.dipole_file = self.task_dir / 'dipole.dat'
        self.spectra_file = self.task_dir / f'spec_{self.pol}.dat'
        self.task_info.output['spectrum_file'] = str(self.spectra_file.relative_to(self.directory))
        self.task_info.output['dm_file'] = str(self.dipole_file.relative_to(self.directory))
        try:
            self.nwchem.get_td_dipole(self.dipole_file, td_out, tag, polarization=self.pol)
        except Exception:
            raise
        #else:
        #    photoabsorption_spectrum(self.dipole_file, self.spectra_file,)

    def create_job_script(self, np=1, remote_path=None) -> list:
                
        job_script = assemable_job_cmd(job_id= self.task_info.uuid,
                                        cd_path=str(self.task_dir), extra_block= self._create_spectrum_cmd(bool(remote_path)))

        self.job_script = job_script
        return self.job_script
    
    def prepare_input(self):
        self.compute_spectrum()
        self.create_job_script()
        self.write_job_script()
            
    def plot(self,**kwargs):
        img = self.spectra_file.parent / f"spec_{self.pol}.png"
        plot_spectrum(self.spectra_file,img,0, 1, "Energy(eV)","Strength",xlimit=(self.user_input['e_min'], self.user_input['e_max']))



class ComputeAvgSpectrum(BaseNwchemTask):

    def create_engine(self, param):
        self.network_done_file = self.task_dir / 'Done'        
        self.averaged_spec_file = self.task_dir / 'averaged_spec.dat'
        self.task_info.output['spectrum_file'] = str(self.averaged_spec_file.relative_to(self.directory))
        self.spectrum_files = []
        for task in self.dependent_tasks:
            self.spectrum_files.append(str(self.directory / task.output['spectrum_file']))
        
    def copmute_average(self):
        spec_data = []
        time_data = []
        for i, spec_file in enumerate(self.spectrum_files):
            file = self.project_dir / spec_file
            data = np.loadtxt(file)
            time_data.append(data[:,0])
            spec_data.append(data[:,1])

        spec_data = np.column_stack(tuple(spec_data))
        averaged_data = np.average(spec_data, axis=1)
        spec_avg_data = np.column_stack((time_data[0], averaged_data))
        with open(self.averaged_spec_file, 'ab') as f:
            np.savetxt(f, np.array(spec_avg_data))

    def get_engine_log(self):
        pass        

    def run_job_local(self, cmd):
        try:
            self.copmute_average()
        except Exception as e:
            self.task_info.job_info.job_returncode = 1
            self.task_info.job_info.output = ''
            self.task_info.job_info.error = str(e)
        else:
            self.task_info.job_info.job_returncode = 0
            self.task_info.job_info.output = ''
            self.task_info.job_info.error = ''

    def prepare_input(self):
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)
        
            
    def plot(self, **kwargs):
        img = self.averaged_spec_file.with_suffix('.png')
        plot_spectrum(str(self.averaged_spec_file),
                        str(img),
                        0,
                        1, 
                        "Energy (in eV)", 
                        "Strength(in /eV)",
                        xlimit=(self.user_input['e_min'], self.user_input['e_max']))
