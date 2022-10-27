import tkinter as tk
from tkinter import messagebox
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.common.workflow_manager import WorkflowManager
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import (Task, TaskFailed,
                                GROUND_STATE,RT_TDDFT_DELTA,
                                RT_TDDFT_LASER, SPECTRUM,
                                TCM, MO_POPULATION,
                                MASKING)
from litesoph.gui import views as v
from litesoph.gui import actions
from litesoph.common import models as m

serial_tasks = [SPECTRUM, TCM, MO_POPULATION]

class TaskController:

    def __init__(self, workflow_controller, app) -> None:
        self.app = app
        self.workflow_controller = workflow_controller
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.task_input_frame = app.task_input_frame
        self.status_engine = app.status_engine
        self.task_info = None
        self.task_view = None

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.status = workflow_manager.status
        self.task_view = task_view
        self.task = None
        self.create_task_view(task_view, self.task_info.engine, self.task_info.name)
        
        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        self.main_window.bind_all('<<DesignLaser>>', self._on_design_laser)
        
        if self.task_name in serial_tasks:
            self.task_view.submit_button.config(command = self._run_task_serial)
            self.task_view.plot_button.config(command = self._on_plot_button)
            self.task_view.back_button.config(command= self.workflow_controller.show_workmanager_page)
        if self.task_name == MASKING:
            self.task = self.workflow_manager.start_task(user_input={})
            self.task_view.submit_button.config(command = self._run_task_serial)
            self.task_view.plot_button.config(command = self._run_task_serial)
        
        if self.task_name == RT_TDDFT_DELTA:
            self.task_view.update_engine_default(self.engine)

    def create_task_view(self, view_class, *args, **kwargs):
        self.task_view = view_class(self.task_input_frame, *args, **kwargs)
        self.task_view.grid(row=0, column=0, sticky ='NSEW')
        self.task_view.tkraise()

    def generate_input(self, *_):
        
        if RT_TDDFT_LASER == self.task_name:
            if not self._on_choose_laser():
                return
            self.task_view.set_laser_design_dict(self.laser_design.l_design)
        
        inp_dict = self.task_view.get_parameters()
        if not inp_dict:
            return

        engine = inp_dict.pop('engine', None)
        if GROUND_STATE == self.task_name and (not self.engine):   
            self.task_info.engine = engine

        self.task_info.ui_param.update(inp_dict)
        self.task = self.workflow_manager.start_task(inp_dict)
        self.task.create_template()
        self.view_panel.insert_text(text=self.task.template, state='normal')
        self.bind_task_events()
    
####-------------------------------------------------------------------------------------------
    # Laser Design should be seprated from other dependencies and make it as a 
    # stand alone module. Below function needs to be rewritten to achieve the above objective.
    def _on_design_laser(self, *_):
        laser_desgin_inp = self.task_view.get_laser_pulse()
        self.laser_design = m.LaserDesignModel(laser_desgin_inp)
        self.laser_design.create_pulse()
        self.laser_design.plot_time_strength()

    def _on_choose_laser(self, *_):
        if not self.laser_design:
            messagebox.showerror(message="Laser is not set. Please choose the laser")
            return
        check = messagebox.askokcancel(message= "Do you want to proceed with this laser set up?")
        if check is True:
            self.laser_design.write_laser("laser.dat")
            return True
        else:
            self.laser_design = None 
    
####-----------------------------------------------------------------------------------------------
    
    def _run_task_serial(self, *_):
        
        inp_dict = self.task_view.get_parameters()
        self.task = self.workflow_manager.start_task(inp_dict)
        self.status.set_new_task(self.engine, self.task.task_name)
        self.status.update(f'{self.engine}.{self.task.task_name}.script', 1)
        self.status.update(f'{self.engine}.{self.task.task_name}.param',self.task.user_input)

        self.task.prepare_input()
        self.task_info.state.input = 'done'
        self.task_info.param.update(self.task.user_input)
        self._run_local(self.task, np=1)
        
##-------------------------------masking task-------------------------------------------------------------

    def _on_masking_page_compute(self, *_):
        inp_dict = self.task_view.get_parameters()
        txt = self.task.get_energy_coupling_constant(**inp_dict)
        self.view_panel.insert_text(text= txt, state= 'disabled')

    def _on_plot_dm_file(self, *_):
        inp_dict = self.task_view.get_parameters()
        self.task.plot(**inp_dict)

####---------------------------------------------------------------------------------------

    @staticmethod
    def _check_task_run_condition(task, network=False) -> bool:
        
        try:
           task.check_prerequisite(network)           
        except FileNotFoundError as e:
            return False
        else:
            return True
            
    def view_input_file(self, task:Task):
        self.view_panel.insert_text(task.template)
    
    def bind_task_events(self):
        self.main_window.bind_all(f'<<Save{self.task_name}Script>>', lambda _ : self._on_save_button(self.task, self.task_view))
        self.main_window.bind_all(f'<<SubLocal{self.task_name}>>', lambda _ : self._on_run_local_button(self.task))
        self.main_window.bind_all(f'<<SubNetwork{self.task_name}>>', lambda _ : self._on_run_network_button(self.task))
    
    def _on_save_button(self, task:Task, view, *_):
        template = self.view_panel.get_text()
        task.write_input(template)
        self.task_info.state.input = 'done'
        self.task_info.param.update(task.user_input)
        self.status.set_new_task(self.engine, task.task_name)
        self.status.update(f'{self.engine}.{task.task_name}.script', 1)
        self.status.update(f'{self.engine}.{task.task_name}.param',task.user_input)
        if task.task_name == 'ground_state':
            self.status_engine.set(self.engine)
        view.set_sub_button_state('active')
        view.set_label_msg('saved')
    
    def _on_run_network_button(self, task:Task, *_):

        if not self._check_task_run_condition(task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self.task_input_frame, task.task_name , 'Network')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        remote = get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.set_run_button_state('disable')
        self.job_sub_page.bind(f'<<Run{task.task_name}Network>>', lambda _: self._run_network(task))
        self.job_sub_page.bind(f'<<View{task.task_name}NetworkOutfile>>', lambda _: self._on_out_remote_view_button(task))
        self.job_sub_page.bind(f'<<Save{task.task_name}Network>>',lambda _: self._on_save_job_script(task, self.job_sub_page))
        self.job_sub_page.bind(f'<<Create{task.task_name}NetworkScript>>', lambda _: self._on_create_remote_job_script(task, task.task_name))
    
    def _on_run_local_button(self, task:Task, *_):

        if not self._check_task_run_condition(task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self.task_input_frame, task.task_name, 'Local')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        self.job_sub_page.set_run_button_state('disable')
        
        self.job_sub_page.bind(f'<<Run{task.task_name}Local>>', lambda _: self._run_local(task))
        self.job_sub_page.bind(f'<<View{task.task_name}LocalOutfile>>', lambda _: self._on_out_local_view_button(task))
        self.job_sub_page.bind(f'<<Save{task.task_name}Local>>',lambda _: self._on_save_job_script(task, self.job_sub_page))
        self.job_sub_page.bind(f'<<Create{task.task_name}LocalScript>>', lambda _: self._on_create_local_job_script(task, task.task_name))
    
    def _on_plot_button(self, *_):
        
        param = {}
        try:
            get_param_func = getattr(self.task_view, 'get_plot_parameters')
        except AttributeError:
            pass
        else:
            param = get_param_func()
        
        try:
            self.task.plot(**param)
        except Exception as e:
            messagebox.showerror(title='Error', message="Error occured during plotting", detail= e)

    def _run_local(self, task: Task, np=None):

        if np:
            sub_job_type = 0
            cmd = 'bash'
        else:
            np = self.job_sub_page.get_processors()
            sub_job_type = self.job_sub_page.sub_job_type.get()

            cmd = self.job_sub_page.sub_command.get()
            
        if sub_job_type == 1:
            
            if not cmd:
                messagebox.showerror(title="Error", message=" Please provide submit command for queue submission")
                self.job_sub_page.set_run_button_state('active')
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.set_run_button_state('active')
                return

        task.set_submit_local(np)
    

        try:
            task.run_job_local(cmd)
        except FileNotFoundError as e:
            messagebox.showerror(title='yes',message=e)
            return
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            return
        else:
            if task.local_cmd_out[0] != 0:
                self.task_info.local.update({'returncode': task.local_cmd_out[0],
                                            'error':task.local_cmd_out[2]})
                self.status.update(f'{self.engine}.{task.task_name}.sub_local.returncode', task.local_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {task.local_cmd_out[2]}")
            else:
                self.task_info.local.update({'returncode': task.local_cmd_out[0],
                                            'n_proc': np,
                                            'error':None})
                self.task_info.state.calculation = True
                self.status.update(f'{self.engine}.{task.task_name}.sub_local.returncode', 0)
                self.status.update(f'{self.engine}.{task.task_name}.sub_local.n_proc', np)
                self.status.update(f'{self.engine}.{task.task_name}.done', True)
                messagebox.showinfo(title= "Well done!", message='Job completed successfully!')
                

    def _on_out_local_view_button(self,task: Task, *_):

        try:
            log_txt = task.get_engine_log()
        except TaskFailed:
            messagebox.showinfo(title='Info', message="Job not completed.")
            return
            
        self.view_panel.insert_text(log_txt, 'disabled')


    def _run_network(self, task: Task):

        try:
            task.check_prerequisite(network = True)
        except FileNotFoundError as e:
            messagebox.showerror(title = "Error", message = e)
            self.job_sub_page.set_run_button_state('active')
            return

        sub_job_type = self.job_sub_page.sub_job_type.get()

        cmd = self.job_sub_page.sub_command.get()
        if sub_job_type == 1:
            
            if not cmd:
                messagebox.showerror(title="Error", message=" Please provide submit command for queue submission")
                self.job_sub_page.set_run_button_state('active')
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.set_run_button_state('active')
                return

        
        login_dict = self.job_sub_page.get_network_dict()
        update_remote_profile_list(login_dict)
        
        try:
            task.connect_to_network(hostname=login_dict['ip'],
                                    username=login_dict['username'],
                                    password=login_dict['password'],
                                    port=login_dict['port'],
                                    remote_path=login_dict['remote_path'])
        except Exception as e:
            messagebox.showerror(title = "Error", message = 'Unable to connect to the network', detail= e)
            self.job_sub_page.set_run_button_state('active')
            return
        try:
            task.submit_network.run_job(cmd)
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            self.job_sub_page.set_run_button_state('active')
            return
        else:
            if task.net_cmd_out[0] != 0:
                self.task_info.network.update({'sub_returncode': task.local_cmd_out[0],
                                            'n_proc': self.job_sub_page.processors.get(),
                                            'error':task.net_cmd_out[2],
                                            'output': task.net_cmd_out[1]})
                self.status.update(f'{self.engine}.{task.task_name}.sub_network.returncode', task.net_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {task.net_cmd_out[2]}")
            else:
                self.task_info.network.update({'sub_returncode': task.local_cmd_out[0],
                                            'n_proc': self.job_sub_page.processors.get(),
                                            'error':task.net_cmd_out[2],
                                            'output':task.net_cmd_out[1]})
                self.status.update(f'{self.engine}.{task.task_name}.sub_network.returncode', 0)
                messagebox.showinfo(title= "Well done!", message='Job submitted successfully!')


    def _get_remote_output(self, task: Task):
        task.submit_network.download_output_files()
        self.status.update(f'{self.engine}.{task.task_name}.done', True)

    def _on_create_local_job_script(self, task: Task, *_):
        np = self.job_sub_page.processors.get()
        b_file =  task.create_job_script(np)
        self.view_panel.insert_text(b_file, 'normal')

    def _on_create_remote_job_script(self, task: Task, *_):
        np = self.job_sub_page.processors.get()
        rpath = self.job_sub_page.rpath.get()
        if rpath:
            b_file = task.create_job_script(np, remote_path=rpath)
        else:
            messagebox.showerror(title="Error", message="Please enter remote path")
            return
        self.view_panel.insert_text(b_file, 'normal')
       
    def _on_save_job_script(self,task :Task,view, *_):
        view.set_run_button_state('active')
        txt = self.view_panel.get_text()
        task.write_job_script(txt)
        self.task_info.state.job_script = True

    def _on_out_remote_view_button(self,task, *_):
        
        try:
            exist_status, stdout, stderr = task.net_cmd_out
        except AttributeError:
            return

        print("Checking for job completion..")
        if task.submit_network.check_job_status():

            print('job Done.')
            self._get_remote_output(task)   
            log_txt = task.get_engine_log()
            self.view_panel.insert_text(log_txt, 'disabled')
            self.task_info.state.calculation = True
            self.task_info.network.update({'data_downloaded': True})
        else:
            get = messagebox.askyesno(title='Info', message="Job not commpleted.", detail= "Do you what to download engine log file?")

            if get:
                task.submit_network.get_output_log()
                log_txt = task.get_engine_log()
                self.view_panel.insert_text(log_txt, 'disabled')
            else:
                return