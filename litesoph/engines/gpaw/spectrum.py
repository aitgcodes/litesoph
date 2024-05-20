from pathlib import Path
from typing import Union, List, Dict
import copy
import numpy as np
from litesoph.visualization.plot_spectrum import plot_multiple_column, plot_spectrum

from litesoph.engines.gpaw.gpaw_task import (GpawTask,
                        TaskInfo, 
                        tt, 
                        gpaw_data, 
                        get_new_directory,
                        get_polarization_direction,
                        update_spectrum_input)


class ComputeSpectrum(GpawTask):

    def setup_task(self, param):
        infile_ext = '.py'
        input_filename = self.task_data.get('file_name', 'spec')
        self.network_done_file = self.task_dir / 'Done'
        self.task_info.input['engine_input']={}
        self.input_filename = input_filename + infile_ext
        
        self.task_info.input['engine_input']['path'] = str(self.task_dir.relative_to(self.project_dir) / self.input_filename)
        param['dm_file'] = self.project_dir / self.dependent_tasks[0].output.get('dm_files')[0]
        self.pol = get_polarization_direction(self.dependent_tasks[0])
        param['polarization'] = list(self.pol)
        param['spectrum_file'] = spec_file = f'spec_{self.pol[1]}.dat'

        self.task_info.output['spectrum_file'] = str(self.task_dir.relative_to(self.project_dir) / param['spectrum_file'])
        update_spectrum_input(param)
        self.spec_file = self.task_dir / spec_file
        return

    def get_engine_log(self):
        pass        

    def run_job_local(self, cmd):
        self.write_job_script(self.job_script)
        super().run_job_local(cmd)
   
    def plot(self, **kwargs):
        img = self.spec_file.with_suffix('.png')
        plot_spectrum(str(self.spec_file),str(img),0, self.pol[0]+1, "Energy (in eV)", "Strength(in /eV)",xlimit=(self.user_input['e_min'], self.user_input['e_max']))
    
class ComputeAveragedSpectrum(GpawTask):


    def setup_task(self, param):
        self.averaged_spec_file = self.task_dir / 'averaged_spec.dat'
        self.task_info.output['spectrum_file'] = self.task_dir.relative_to(self.project_dir) /Path(self.averaged_spec_file).name
        self.spectrum_files = []
        for task in self.dependent_tasks:
            spectra_file_path = self.project_dir / str(task.output['spectrum_file'])
            self.spectrum_files.append(spectra_file_path)

    def prepare_input(self):
        if not self.task_dir.exists():
            self.create_directory(self.task_dir)
        

    def copmute_average(self):
        spec_data = []
        time_data = []
        for i, file in enumerate(self.spectrum_files):
            data = np.loadtxt(file)
            time_data.append(data[:,0])
            spec_data.append(data[:,i+1])

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

    def plot(self, **kwargs):
        img = self.averaged_spec_file.with_suffix('.png')
        plot_spectrum(str(self.averaged_spec_file),
                        str(img),
                        0, 
                        1, 
                        "Energy (in eV)", 
                        "Strength(in /eV)",
                        xlimit=(self.user_input['e_min'], self.user_input['e_max']))