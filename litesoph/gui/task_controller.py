import tkinter as tk
from tkinter import messagebox
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list
import copy
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import InputError, Task, TaskFailed
from litesoph.common.task_data import TaskTypes as tt  
from litesoph.common.workflows_data import WorkflowTypes as wt                                
from litesoph.gui import views as v
from litesoph.common import models as m
from litesoph.gui.models.gs_model import choose_engine
from litesoph.common.decision_tree import EngineDecisionError
from litesoph.gui.models import inputs as inp


class TaskController:

    def __init__(self, workflow_controller, app) -> None:
        self.app = app
        self.workflow_controller = workflow_controller
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.status_engine = app.status_engine
        self.task_info = None
        self.task_view = None
        self.job_sub_page = None
        
    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.job_sub_page = v.JobSubPage(self.app.task_input_frame)
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)
        self.job_sub_page.back2task.config(command= self.show_task_view)

        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        
        self.task_view.set_sub_button_state('disable') 

        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    # def create_task_view(self, view_class, *args, **kwargs):
    #     self.task_view = view_class(self.app.task_input_frame, *args, **kwargs)
    #     self.task_view.grid(row=0, column=0, sticky ='NSEW')
    #     self.task_view.tkraise()

    def update_wf_view_defaults(self, get_default_func=None):
        """ Checks task mode bool.\n
        If task mode: passes the engine updated task defaults.\n
        If workflow mode: updates the engine updated task defaults in context of workflow"""

        default_param = copy.deepcopy(self.task_info.param)
        if not self.workflow_manager.workflow_info.task_mode: 
            if get_default_func is not None:
                default_param.update(get_default_func())
        return default_param

    def show_task_view(self):
        self.task_view.tkraise()

    def generate_input(self, *_):
        
        self.task_info.param.clear()
        inp_dict = self.task_view.get_parameters()
        if not inp_dict:
            return

        if tt.GROUND_STATE == self.task_name:
            engine = choose_engine(copy.deepcopy(inp_dict))   
            if engine is None:
                return
            try:
                self.workflow_manager.set_engine(engine)
            except EngineDecisionError as e:
                messagebox.showerror(title="Engine Error", message=e)
                return

        check = messagebox.askokcancel(title='Input parameters selected', message= dict2string(inp_dict))
        if not check:
            return
        
        self.task_info.param.update(inp_dict)
        self.task = self.workflow_manager.get_engine_task()
        self.task.create_input()
        txt = self.task.get_engine_input()
        self.view_panel.insert_text(text=txt, state='normal')
        self.bind_task_events()
    

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
        self.main_window.bind_all(f'<<SubLocal{self.task_name}>>', self._on_run_local_button)
        self.main_window.bind_all(f'<<SubNetwork{self.task_name}>>', self._on_run_network_button)
    
    def _on_save_button(self, task:Task, view, *_):
        template = self.view_panel.get_text()
        task.set_engine_input(template)
        task.save_input()
        if task.task_name == tt.GROUND_STATE:
            self.status_engine.set(self.engine)
            #TODO: disable/freeze the inputs
            #self.task_view.inp.freeze_widgets(state='disabled')
        view.set_sub_button_state('active')
        view.set_label_msg('saved')
    
    def _on_clear_button(self):
        pass

    def _on_run_network_button(self, *_):

        if not self._check_task_run_condition(self.task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return

        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        self.job_sub_page.view_output_button.config(command= self._on_out_remote_view_button)
        self.job_sub_page.show_run_network(self._on_create_remote_job_script,
                                            self._on_save_job_script,
                                            self._run_network)

        self.job_sub_page.runtime_query_remote(self._on_check_job_status_remote,
                                               self._on_check_file_status_remote,
                                               self._on_kill_job_remote,
                                               self._on_download_all_files,
                                               self._on_download_specific_file,
                                               self._on_view_specific_file_remote,
                                               self._on_plot_file_remote)
                        
        remote = get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.set_run_button_state('disable')
        self.job_sub_page.tkraise()

    def _on_run_local_button(self, *_):

        if not self._check_task_run_condition(self.task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
       
        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        self.job_sub_page.view_output_button.config(command= self._on_out_local_view_button)        
        self.job_sub_page.show_run_local(self._on_create_local_job_script,
                                        self._on_save_job_script,
                                        self._run_local)
        
        self.job_sub_page.runtime_query_local(self._on_check_job_status_local,
                                        self._on_check_file_status_local,
                                        self._on_view_specific_file_local,
                                        self._on_plot_file_local)

        self.job_sub_page.set_run_button_state('disable')        
        self.job_sub_page.tkraise()

    def _on_check_file_status_local(self):
        try:
            error,msg=self.task.submit_local.get_fileinfo_local()                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)
            return            
        # self.view_panel.insert_text(msg, 'disabled')
        self.task.submit_local.generate_list_of_files_local()
        
        choose_file= self.job_sub_page.combobox
        list_of_files=self.task.submit_local.get_list_of_files_local()
        self.dict_of_files_combobox=self.encode_decode_combobox_items(list_of_files)        
        list_of_files=list(self.dict_of_files_combobox.keys())

        choose_file['values'] = list_of_files
        choose_file.current()
        self.combobox_selected_file=choose_file.bind("<<ComboboxSelected>>",self.selection_changed)        
        self.job_sub_page.plot_file_button.config(state='active')
        self.job_sub_page.download_specific_file_button.config(state='active')
    
    def _on_view_specific_file_local(self):        
        try:
            error, message=self.task.submit_local.view_specific_file_local(self.selected_file)  
        except UnicodeDecodeError:
            messagebox.showinfo(title='Info', message="Unable to Read File")                    
            self.view_panel.insert_text(message, 'disabled')
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File") 
        self.view_panel.insert_text(message, 'disabled')

    def _on_plot_file_local(self):
        import os        
        try:
            if os.path.exists(self.selected_file)==True:
                cmd=f'xmgrace {self.selected_file}'
                # cmd=f'"/home/anandsahu/softwares/visit_visualization/bin/visit" {file}'
                os.system(cmd)
            else:
                messagebox.showinfo(title='Info', message="File not found")
        except ValueError:
            messagebox.showinfo(title='Info', message="Cannot plot selected File")   
        except FileNotFoundError:
            messagebox.showinfo(title='Info', message="File not found")  
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File")                    
            
    def _on_check_job_status_local(self):        
        if self.job_sub_page.submit_thread.is_alive(): 
            messagebox.showinfo(title='Info', message="Job is Running")
        else:
            messagebox.showinfo(title='Info', message="No Job Found")

    def selection_changed(self,event):
        selected_file = self.job_sub_page.combobox.get()
        self.selected_file=self.dict_of_files_combobox[selected_file]
        messagebox.showinfo(
        title="New Selection",
        message=f"Selected option: {self.selected_file}")
        
    def encode_decode_combobox_items(self,list_of_files):
        import pathlib
        from litesoph.common.lfm_database import coordinate_files,dipole_files,spectrum_files,script_output_files

        mapped_dict={}

        i = 0
        coordinate_count=0
        dipole_count=0
        spectrum_file_count=0
        script_output_count=0

        while i < len(list_of_files):
            
            file_path=pathlib.Path(list_of_files[i]).parent
            last_folder_name=pathlib.Path(list_of_files[i]).parent.name
            file_name=pathlib.Path(list_of_files[i]).name
            file_ext=pathlib.Path(list_of_files[i]).suffix
            
            if  file_ext in coordinate_files:                
                coordinate_file=f'coordinate_file_{coordinate_count+1}'
                mapped_dict[coordinate_file] = list_of_files[i]
                list_of_files[i] = coordinate_file            
                coordinate_count+=1    
        
            if  file_name in dipole_files:
                dipole_file=f'dipole-file-{dipole_count+1}'
                mapped_dict[dipole_file] = list_of_files[i]
                list_of_files[i] = dipole_files            
                dipole_count+=1    
            
            if  file_name in spectrum_files:
                spectrum_file=f'spectrum-file-{spectrum_file_count+1}'
                mapped_dict[spectrum_file] = list_of_files[i]
                list_of_files[i] = spectrum_files            
                spectrum_file_count+=1    
            
            if  file_name in script_output_files:
                file=f'script-output-{script_output_count+1}'
                mapped_dict[file] = list_of_files[i]
                list_of_files[i] = script_output_files            
                script_output_count+=1    
                                    
            i += 1
        return mapped_dict
            
    def _on_check_file_status_remote(self):    

        try:
            error, msg=self.task.submit_network.get_fileinfo_remote()            
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)            
        # self.view_panel.insert_text(msg, 'disabled')
        
        choose_file= self.job_sub_page.combobox
        list_of_files=self.task.submit_network.get_list_of_files_remote()
        self.dict_of_files_combobox=self.encode_decode_combobox_items(list_of_files)        
        list_of_files=list(self.dict_of_files_combobox.keys())
        
        choose_file['values'] =  list_of_files
        choose_file.current()
        self.combobox_selected_file=choose_file.bind("<<ComboboxSelected>>",self.selection_changed)
        
        self.job_sub_page.download_specific_file_button.config(state='active')
        self.job_sub_page.view_file_button.config(state='active')
        self.job_sub_page.plot_file_button.config(state='active')
        messagebox.showinfo(title='Info', message=f'Project Size: {self.task.submit_network.project_size_GB:.2f} GB')

    def _on_check_job_status_remote(self):
        try:
            job_status=self.task.submit_network.get_job_status_remote()    
            messagebox.showinfo(title='Info', message=job_status)   
        except TaskFailed:
            messagebox.showinfo(title='Info', message='error')   
        
    def _on_kill_job_remote(self):
    
        job_id=self.job_sub_page.job_id.get()            
        scheduler=self.job_sub_page.sub_command.get()
        scheduler_stat_cmd=self.job_sub_page.sub_stat_command.get()
        scheduler_kill_cmd=self.job_sub_page.sub_kill_command.get()

        if job_id == None:
            messagebox.showinfo(title='Info', message="Enter Job ID first")                  
        else:
            try:
                error, message=self.task.submit_network.kill_job_remote(job_id,scheduler,scheduler_stat_cmd,scheduler_kill_cmd)                
            except TaskFailed:
                messagebox.showinfo(title='Info', message=error)                    
            messagebox.showinfo(title='Info', message=message)   
            self.job_sub_page.progressbar.stop()
            label_progressbar = tk.Label(self.job_sub_page.Frame1, text="Job Killed ",font=('Helvetica', 14, 'bold'), bg='gray', fg='black')
            label_progressbar.grid(row=4, column=0,sticky='nsew')

    def _on_download_all_files(self):
        try:
            error, message=self.task.submit_network.download_all_files_remote()                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)                    
        return (error, message)
    
    def _on_download_specific_file(self):        
        try:
            priority1_files_dict={self.selected_file: {'file_relevance': 'very_impt', 'file_lifetime': '', 'transfer_method': {'method': 'direct_transfer', 'compress_method': 'zstd', 'split_size': ''}}}        
            error, message=self.task.submit_network.download_specific_file_remote(self.selected_file,priority1_files_dict)                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)                    
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the file")
        messagebox.showinfo(title='Info', message=message)   

    def _on_view_specific_file_remote(self):        
        try:
            error, message=self.task.submit_network.view_specific_file_remote(self.selected_file)  
        except UnicodeDecodeError:
            messagebox.showinfo(title='Info', message="Unable to Read File")                    
            self.view_panel.insert_text(message, 'disabled')
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File") 
        self.view_panel.insert_text(message, 'disabled')

    def _on_plot_file_remote(self):
        import os        
        try:
            file = str(self.selected_file).replace( str(self.task.submit_network.remote_path), str(self.task.submit_network.project_dir))
            if os.path.exists(file)==True:
                cmd=f'xmgrace {file}'
                # cmd=f'"/home/anandsahu/softwares/visit_visualization/bin/visit" {file}'
                os.system(cmd)
            else:
                messagebox.showinfo(title='Info', message="First download the file")
        except ValueError:
            messagebox.showinfo(title='Info', message="Cannot plot selected File")   
        except FileNotFoundError:
            messagebox.showinfo(title='Info', message="File not found")  
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File")                    
            
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

    def _run_local(self, np=None):

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

        self.task.set_submit_local(np)
        
        try:
            self.task.run_job_local(cmd)
        except FileNotFoundError as e:
            messagebox.showerror(title='yes',message=e)
            return
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            return
        else:
            if self.task.task_info.local['returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {self.task.task_info.local['error']}")
            else:
                self.label_progressbar = tk.Label(self.job_sub_page.Frame1, text="Job Done",font=('Helvetica', 14, 'bold'), bg='gray', fg='black')
                self.label_progressbar.grid(row=4, column=0,sticky='nsew')
                messagebox.showinfo(title= "Well done!", message='Job completed successfully!')
                
    def _on_out_local_view_button(self, *_):

        try:
            log_txt = self.task.get_engine_log()
        except TaskFailed:
            messagebox.showinfo(title='Info', message="Job not completed.")
            return
            
        self.view_panel.insert_text(log_txt, 'disabled')

    def _run_network(self):

        try:
            self.task.check_prerequisite()
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
            self.task.connect_to_network(hostname=login_dict['ip'],
                                    username=login_dict['username'],
                                    password=login_dict['password'],
                                    pkey_file=login_dict['pkey_file'],
                                    port=login_dict['port'],
                                    remote_path=login_dict['remote_path'],
                                    passwordless_ssh=login_dict['passwordless_ssh'])
        except Exception as e:
            messagebox.showerror(title = "Error", message = 'Unable to connect to the network', detail= e)
            self.job_sub_page.set_run_button_state('active')
            return
        try:
            self.task.submit_network.run_job(cmd)
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            self.job_sub_page.set_run_button_state('active')
            return
        else:
            if self.task.task_info.network['sub_returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {self.task.task_info.network['error']}")
            else:
                self.label_progressbar = tk.Label(self.job_sub_page.Frame1, text="Job Done",font=('Helvetica', 14, 'bold'), bg='gray', fg='black')
                self.label_progressbar.grid(row=4, column=0,sticky='nsew')
                output=self.task.task_info.network['output']
                self.view_panel.insert_text(output, 'disabled')
                messagebox.showinfo(title= "Well done!", message='Job Completed successfully!', detail = f"output:{self.task.task_info.network['output']}")
            
    def _get_remote_output(self):
        self.task.submit_network.download_output_files()

    def _on_create_local_job_script(self, *_):
        np = self.job_sub_page.processors.get()
        b_file =  self.task.create_job_script(np)
        self.view_panel.insert_text(b_file, 'normal')

    def _on_create_remote_job_script(self, *_):
        np = self.job_sub_page.processors.get()
        rpath = self.job_sub_page.rpath.get()
        if rpath:
            b_file = self.task.create_job_script(np, remote_path=rpath)
        else:
            messagebox.showerror(title="Error", message="Please enter remote path")
            return
        self.view_panel.insert_text(b_file, 'normal')
       
    def _on_save_job_script(self, *_):
        self.job_sub_page.set_run_button_state('active')
        txt = self.view_panel.get_text()
        self.task.write_job_script(txt)
        self.task_info.state.job_script = True

    def _on_out_remote_view_button(self, *_):
        
        check =  self.task.task_info.network.get('sub_returncode', None)
        if check is None:
            messagebox.showinfo(title= "Warning", message="The job is not submitted yet.")
            return

        if check != 0:
            messagebox.showinfo(title= "Warning", message="Error occured during job submission.", detail = f"output:{self.task.task_info.network['output']}")
            return

        print("Checking for job completion..")
        if self.task.submit_network.check_job_status():

            print('job Done.')
            self._get_remote_output()   
            log_txt = self.task.get_engine_log()
            self.view_panel.insert_text(log_txt, 'disabled')
            self.task_info.state.calculation = True
            self.task_info.network.update({'data_downloaded': True})
        else:
            get = messagebox.askyesno(title='Info', message="Job not commpleted.", detail= "Do you what to download engine log file?")

            if get:
                self.task.submit_network.get_output_log()
                log_txt = self.task.get_engine_log()
                self.view_panel.insert_text(log_txt, 'disabled')
            else:
                return

class MaskingPageController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        try:
            self.task = self.workflow_manager.get_engine_task()
        except TaskSetupError as e:
            messagebox.showerror("Error", str(e))
            return
            

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)
        
        self.task_view.energy_coupling_button.config(command = self._on_masking_page_compute)
        self.task_view.plot_button.config(command = self._on_plot_dm_file)
        self.task_view.back_button.config(command= self.workflow_controller.show_workmanager_page)


        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def _on_masking_page_compute(self, *_):
        inp_dict = self.task_view.get_parameters()
        try:
            txt = self.task.get_energy_coupling_constant(**inp_dict)
            self.view_panel.insert_text(text= txt, state= 'disabled')
        except Exception as e:
            messagebox.showerror(title='Error', message=e)

    def _on_plot_dm_file(self, *_):
        inp_dict = self.task_view.get_parameters()
        try:
            self.task.plot(**inp_dict)
        except Exception as e:
            messagebox.showerror(title='Error', message=e)

class TDPageController(TaskController):

    def __init__(self, workflow_controller, app) -> None:
        super().__init__(workflow_controller, app)
        self.get_laser_data()

    def get_laser_data(self, laser_exists:bool=False):
        """Creates and populates laser data for current calculation.
        Add condition for populating"""

        self.laser_defined = laser_exists
        self.laser_data = {}
        if laser_exists:
            pass

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = tt.RT_TDDFT
        self.task_view = task_view
        self.task = None
        self.current_delay_index = 0
        self.app.proceed_button.config(command=self._on_proceed)

        self.job_sub_page = v.JobSubPage(self.app.task_input_frame)
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")

        self.task_view = self.app.show_frame(task_view, self.task_name)
        self.job_sub_page.back2task.config(command= self.show_task_view)

        self.main_window.bind_all('<<BackonTDPage>>', self._on_back)
        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        self.main_window.bind_all('<<Design&EditLaser>>', self._on_design_edit_laser)    
        self.main_window.bind_all('<<ViewLaserSummary>>', self._on_view_lasers)    
        self.task_view.set_sub_button_state('disable')

        if hasattr(self.task_view, 'set_parameters'):
            default_param = self.update_wf_view_defaults(
                            get_default_func= self.get_td_wf_defaults
                            )
            self.task_view.set_parameters(default_param)

    def get_td_wf_defaults(self):
        if self.workflow_manager.workflow_info._name == wt.PUMP_PROBE:
            wf_dict = {
                "field_type": "Electric Field",
                "exp_type": "Pump-Probe",
            }
        elif self.workflow_manager.workflow_info._name == wt.MASKING:
            wf_dict = {
                "field_type": "Electric Field",
                "exp_type": "State Preparation",
            }
        return wf_dict
    
    def set_laser_design_bool(self, bool:bool):
        self.laser_design_bool = bool

    def _on_back(self, *_):
        """ Shows the WorkFlowManager Page"""
        self.workflow_controller.show_workmanager_page()

    def _on_design_edit_laser(self, *_):
        """ On Laser design button, decides on showing LaserDesignPage and binds the widgets"""
        
        # View specific parameters
        # TODO: Check this method
        self.task_view_param = self.task_view.get_td_gui_inp()
        
        # Delays attached as a list of delays before proceeding to laser-design 
        if self.task_view_param.get('delay_list', None) is not None:
            self.delay_list = self.task_view_param.get('delay_list')
        # Task specific parameters
        self.task_param = self.task_view.get_parameters()  

        laser_defined = False
        exp_type = self.task_view_param.get('exp_type') 
        laser_defined = validate_laser_defined(laser_data = self.laser_data, exp_type= exp_type) 

        if laser_defined:
            pass
        else:
            if len(self.laser_data) > 0:
                check = messagebox.askyesno(message="Previously designed laser will be removed. \nDo you want to continue?")
                if check:
                    self.laser_data ={}            

        # check = messagebox.askyesno(message= "Laser is already designed.\n Do you want to edit again?")
        # if not check:
        #     return   
        self._on_show_laser_page(show_stored= False)             

    def _on_show_laser_page(self, show_stored:bool, *_):
        """ Assigns LaserDesignController and shows the LaserDesignPage """

        self.laser_view = self.app.show_frame(v.LaserDesignPage)   
        self.view_panel.clear_text()
        self.laser_controller = LaserDesignController(app= self.app, view=self.laser_view, 
                                                    td_param= self.task_view_param,
                                                    laser_data= self.laser_data) 
        
        self.laser_controller.bind_events_and_update_default_view()  
        self.laser_controller.view.button_next.config(command=self.show_tdpage_and_update)
        self.laser_controller.view.button_back.config(command=self.show_task_view)

        self.laser_controller.update_labels_on_tree()

    def show_tdpage_and_update(self, *_):
        from litesoph.gui.models import inputs as inp

        exp_type = self.task_view_param.get('exp_type') 
        self.laser_defined = validate_laser_defined(self.laser_controller.laser_info.data, exp_type) 

        # Showing message before finalise the laser setup if laser defined is True
        if self.laser_defined:
            check = messagebox.askyesno(message= "Do you want to proceed with this laser setup?")
            if check:
                self.task_view.tkraise()
                self.task_view.set_sub_button_state('disable')
                self.task_view.label_msg.grid_remove()
                self.update_laser_on_td_page()
        else:
            if exp_type == 'Pump-Probe':
                pump_bool = self.laser_controller.laser_info.check_laser_exists(system_tag='pump')
                probe_bool = self.laser_controller.laser_info.check_laser_exists(system_tag='probe')
                if not pump_bool:
                    messagebox.showerror(message="Please add one pump laser.")
                    return
                if not probe_bool:
                    messagebox.showerror(message="Please add one probe laser.")
                    return 
            else:
                messagebox.showinfo(message= "Laser is not set. Please add lasers first.")       

    def update_laser_on_td_page(self):
        """ Checks condition for laser designed and updates TDPage view"""       
    
        # GUI entries from previous td view
        td_param_stored = self.task_view_param        
        if self.task_view.inp.variable['exp_type'].get() == "State Preparation":
            pass
        else:
            widget_dict = copy.deepcopy(inp.get_td_laser_w_delay())
            self.task_view.add_widgets(widget_dict)
            _gui_dict = {
                "field_type": td_param_stored.get("field_type"),
                "exp_type" : td_param_stored.get("exp_type")
            }
            _gui_dict.update(self.task_param)
            self.task_view.set_parameters(_gui_dict)

            # TODO: Remove this 
            if self.task_view_param.get('exp_type') == 'Pump-Probe':  
                if self.delay_list:
                    delays = copy.deepcopy(self.delay_list)
                else:
                    delays = [0]
                delays.insert(0, 'No Probe') 
                self.task_view.inp.widget["delay_values"].config(values= delays)
                self.task_view.inp.widget["delay_values"].config(state = 'readonly')
                self.task_view.inp.widget["delay_values"].current(0)                    
                self.task_view.label_delay_entry.grid_remove()
                self.add_task(delays)

        self.task_view.button_view.config(state='active')
        self.task_view.button_save.config(state='active')
        if self.task_view.label_delay_entry:
            self.task_view.label_delay_entry.grid_remove()

        #TODO: freeze required input entries
        # self.task_view.inp.freeze_widgets(state= 'disabled', input_keys = ["field_type","exp_type"])

    def get_laser_details(self):
        details = []
        for i,l_name in enumerate(self.laser_data.keys()):
            l_system = self.laser_data[l_name]
            tag = l_system.get('tag')
            details.append(f'\n{tag}')
            pulses = l_system.get('pulses')
            laser_sets = extract_lasers_from_pulses(pulses)
            laser_params = []

            for laser in laser_sets:
                laser_params.append(laser[1])            

            for laser_index,laser in enumerate(laser_params):
                details.append(f'\n#Laser {laser_index+1}:')
                for key, value in laser.items():                    
                    details.append(f"{key} =  {value}")

        txt =  '\n'.join(details)
        return(txt, details)           

    def add_task(self, delays):
        block_id = self.workflow_manager.current_container.block_id
        step_id = self.workflow_manager.current_container.id
        
        step = step_id+1
        for delay in delays:
            if delay == 'No Probe':
                continue
            self.workflow_manager.add_task(self.task_name,
                                            block_id,
                                            step_id=step,
                                            dependent_tasks_uuid= self.workflow_controller.get_task_dependencies(self.task_name))

            td_task_id = self.workflow_manager.containers[step].task_uuid
            dm_task_id = self.workflow_manager.containers[step+1].task_uuid
            self.workflow_manager.add_dependency(dm_task_id, td_task_id)
            step += 1

    def generate_input(self, *_):
        """ Checks experiment type and generate respective inputs"""
        
        self.task_info = self.workflow_manager.current_task_info
        self.task_info.param.clear()
        inp_dict = self.task_view.get_parameters()

        if self.task_view.inp.variable['exp_type'].get() == "State Preparation":
            lasers = copy.deepcopy(self.laser_data['State Preparation']['lasers'])
            pulses = copy.deepcopy(self.laser_data['State Preparation']['pulses'])
            laser_sets = extract_lasers_from_pulses(pulses)
            laser_data = []
            for i,laser in enumerate(laser_sets):
                laser_dict = laser[0]
                laser_dict.update({'mask': lasers[i].get('mask', None)})
                laser_data.append(laser_dict)  
            inp_dict.update({'laser': laser_data})

        # adding masking in pump-probe
        else:
            try:
                delay = self.task_view.inp.variable["delay_values"].get()
            except tk.TclError:
                # lasers
                lasers = copy.deepcopy(self.laser_data['Pump']['lasers'])
                pulses = copy.deepcopy(self.laser_data['Pump']['pulses'])
                laser_sets = extract_lasers_from_pulses(pulses)
                lasers_list = []
                for i,laser in enumerate(laser_sets):
                    laser_dict = laser[0]
                    laser_dict.update({'mask': lasers[i].get('mask', None)})
                    lasers_list.append(laser_dict)  
                delay = "no_probe"
            else:
                pump_lasers = copy.deepcopy(self.laser_data['Pump']['lasers'])
                probe_lasers = copy.deepcopy(self.laser_data['Probe']['lasers'])
                lasers = [] 
                lasers.extend(pump_lasers)
                lasers.extend(probe_lasers)
                pump_data = copy.deepcopy(self.laser_data['Pump'])
                probe_data = copy.deepcopy(self.laser_data['Probe'])
                laser_tuple = add_delay_to_lasers(pump_data, probe_data,float(delay))

                pump_sets = laser_tuple[0]
                probe_sets = laser_tuple[1]
                laser_sets = []
                laser_sets.extend(pump_sets)
                laser_sets.extend(probe_sets)
                
                lasers_list = []
                for i,laser in enumerate(laser_sets):
                    laser_dict = laser
                    laser_dict.update({'mask': lasers[i].get('mask', None)})
                    lasers_list.append(laser_dict)  

            inp_dict.update({'laser': lasers_list,
                            'delay': delay})       
       
        self.task_info.param.clear()
        self.task_info.param.update(inp_dict)
        check = False
        try:
            self.task = self.workflow_manager.get_engine_task()
        except InputError as error_msg:
            messagebox.showerror(message= error_msg)
            return
        check = messagebox.askokcancel(title='Input parameters selected',
                         message= dict2string(inp_dict))
        if not check:
            return
        self.task.create_input()
        txt = self.task.get_engine_input()
        self.view_panel.insert_text(text=txt, state='normal')
        self.bind_task_events()

    def _on_proceed(self, *_):
        if self.workflow_manager.task_mode:
           return            
        if self.task_view.inp.variable['exp_type'].get() == "Pump-Probe":            
            delays = self.delay_list
            if self.current_delay_index == len(delays):
                self.workflow_controller.next_task()
            else:
                self.workflow_manager.next()
                self.task_view.tkraise() 
                self.task_view.set_sub_button_state('disable')
                self.task_view.label_msg.grid_remove()               
                self.task_view.inp.widget["delay_values"].set(delays[self.current_delay_index])
                self.current_delay_index += 1
        else:            
            self.workflow_controller.next_task()   
        
    def _on_view_lasers(self, *_):
        if len(self.laser_data) >0:
            laser_txt = self.get_laser_details()[0]
            self.view_panel.insert_text(text=laser_txt, state='normal')
        else:
            messagebox.showinfo(message='No Laser is designed.')

class LaserDesignController:

    def __init__(self, app, view, 
                        td_param:dict, 
                        laser_data:dict):
        """ td_param: GUI view inputs"""

        # Data extracted from TD page
        self.td_data = td_param  # GUI inputs extracted
        self.laser_info = m.LaserInfo(laser_data)
        self.main_window = app.main_window
        self.view = view
        self.focus = None
        self.assign_laser_profile_time()

    def assign_laser_profile_time(self):
        """Sets td simulation time to laser profile time(in as)"""
        time_step = self.td_data.get('time_step')
        num_steps = self.td_data.get('number_of_steps')
        self.total_time = float(time_step)* num_steps

    def bind_events_and_update_default_view(self):
        # TODO: update these event bindings

        self.main_window.bind_all('<<AddLaser>>', self._on_add_laser)
        self.main_window.bind_all('<<EditLaser>>', self._on_edit_laser)
        self.main_window.bind_all('<<RemoveLaser>>', self._on_remove_laser)
        self.main_window.bind_all('<<PlotLaser>>', self._on_plottting)
        self.main_window.bind_all('<<SelectLaser&UpdateView>>', self._on_select_laser)

        # Collecting exp_type from td_data passed from TDPage
        # TODO: decide on to retain previous exp_type sets
        exp_type = self.td_data.get('exp_type')
        if exp_type == "State Preparation":
            self.view.inp.widget["pump-probe_tag"].configure(state = 'disabled')
            self.view.inp.fields["pump-probe_tag"]["visible"] = False
        
        # if hasattr(self.task_view, 'set_parameters'):
        #     self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def get_laser_design_model(self, laser_input:dict):
        """Collects inputs to compute laser parameters 
        and returns LaserDesignPlotModel object"""

        from litesoph.utilities.units import as_to_au, au_to_fs
        laser_total_time_fs = self.total_time*as_to_au*au_to_fs
        self.laser_design = m.LaserDesignPlotModel(laser_inputs = [laser_input],
                laser_profile_time= laser_total_time_fs)
        
        # TODO: Make this multiple laser input dictionaries consistent with LaserDesignPlotModel        
        self.pulse_info = self.laser_design.get_laser_param_pulse(laser_input= laser_input)
        # self.pulse_list = self.laser_design.get_laser_pulse_list()    
        return self.laser_design
   
    def _on_add_laser(self, *_):  
        """On add laser button:
        \n Checks the validation for time-origin for state-preparation/pump-probe laser inputss
        \n Proceeds to append the lasers
        """
        # GUI inputs for laser page
        laser_gui_inp = self.view.inp.get_values()

        # TODO: Filter out the dict to modify the message
        add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_gui_inp))
        if add_check:
            self.add_lasers_and_update_tree()
        else:
            pass              

    def add_lasers_and_update_tree(self, index=None):    
        # GUI inputs for laser page
        laser_gui_inp = self.view.get_parameters()
        # Laser design model
        laser_design_model = self.get_laser_design_model(laser_gui_inp)
        pulse = laser_design_model.pulse_info

        tag = laser_gui_inp.get('tag', None)
        if tag is None:
            _tag = 'State Preparation'
        else:
            _tag = tag
        self.laser_info.add_laser(system_key=_tag, laser_param= laser_gui_inp, index=index)
        self.laser_info.add_pulse(system_key=_tag, laser_pulse=pulse, index=index)
        self.update_labels_on_tree()  

    def _on_edit_laser(self, *_):
        """On Edit Button:
         Updates the laser info data"""

        if self.focus is not None:
            (parent, index) = self.focus
        else:
            messagebox.showerror(message="Select laser first.") 
            return

        # GUI inputs for laser page
        laser_gui_inp = self.view.inp.get_values()

        # TODO: Filter out the dict to modify the message
        add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_gui_inp))
        if add_check:
            self.add_lasers_and_update_tree(index)
            self.focus = None
        else:
            pass

    def populate_laser_details(self, tag:str, index:int):        
        lasers = self.laser_info.data[tag]['lasers']
        laser_selected = lasers[index]
        # TODO: replace set_parameters
        self.view.set_parameters(laser_selected)
        # self.view.inp.init_widgets(var_values=laser_selected)

    def _on_remove_laser(self, *_):
        """ Removes the laser info data"""

        if self.focus is not None:
            (parent, index) = self.focus
        else:
            messagebox.showerror(message="Select laser first.")
            return
        remove_check = messagebox.askyesno(message="This laser:{} will be removed. Click OK to continue?".format(index+1))
        if remove_check:
            self.laser_info.remove_info(system_key=parent, laser_index=index)
            self.update_labels_on_tree()
            self.focus = None
        else:
            pass     

    def _on_select_laser(self, *_):
        """ Populates the selected laser entries"""

        item = None
        if len(self.view.tree.selection())>0:
            item = self.view.tree.selection()[0]
        
        if item is not None:
            label = str(self.view.tree.item(item,"text"))
            parent = str(self.view.tree.parent(item))
            try:
                index = int(label[-1]) -1
                self.focus = (parent, index)
                self.populate_laser_details(tag=parent, index=index)
                return (parent,index)
            except ValueError:
                # Error when the label does not end with an index
                self.focus = None               

    def update_labels_on_tree(self):
        """Method to update treeview"""
        _parents_under_root = self.view.tree.get_children()

        # Clearing treeview for existing parents
        for i, system_name in enumerate(self.laser_info.data.keys()):
            if system_name in _parents_under_root:
                if self.view.tree.get_children(system_name):
                    for child in self.view.tree.get_children(system_name):
                        self.view.tree.delete(child) 
            else:
                # Add the parents if not already present
                self.view.tree.insert('', str(i), str(system_name), text=str(system_name))

        # Attaching child to parent
        for parent in self.view.tree.get_children():
            num_lasers = self.laser_info.get_number_lasers(system_tag= parent)
            laser_labels = get_laser_labels(laser_defined=True, num_lasers= num_lasers)

            if laser_labels is not None:
                for i, label in enumerate(laser_labels):
                    id = self.view.tree.insert('', 'end', text=str(label))
                    self.view.tree.move(id, str(parent), 'end')

    def show_and_update_plot_page(self, *_):
        self.laser_plot_view = v.LaserPlotPage(self.main_window)
        self.update_tree_and_view_on_plot()

    def update_tree_and_view_on_plot(self):
        """Method to update treeview on Plotting page"""
        _parents_under_root = self.laser_plot_view.tree.get_children()

        # Clearing treeview for existing parents
        for i, system_name in enumerate(self.laser_info.data.keys()):
            if len(self.laser_info.data[system_name]['lasers']) > 0:
                if system_name in _parents_under_root:
                    pass
                else:
                    # Add the parents if not already present
                    self.laser_plot_view.tree.insert('', str(i), str(system_name), text=str(system_name))

        if len(self.laser_plot_view.tree.get_children()) == 1:
            self.laser_plot_view.label_delay.grid_remove()
            self.laser_plot_view.entry_delay.grid_remove()

        else:
            self.laser_plot_view.label_delay.grid()
            self.laser_plot_view.entry_delay.grid()
            # self.laser_plot_view.widget_frame.grid()

    def _on_plottting(self, *_):
        """ On Plotting Button: Shows toplevel for plotting
        and updates the binding"""

        if len(self.laser_info.data) > 0:
            self.show_and_update_plot_page()
            self.laser_plot_view.bind('<<PlotLasers>>', self._on_plot_button)
            # self.laser_plot_view.button_plot_w_delay.configure(command=self._on_plot_w_delay_button)           
        else:
            messagebox.showerror(message="Please add lasers to plot.")
            return 

    def _on_plot_button(self, *_):
        """On Plot Button in PlotPage"""
        from litesoph.utilities.units import as_to_au, au_to_fs, fs_to_au

        # bool if Probe is present
        plot_probe = False

        # TODO: Validate number of system selected
        systems_selected = self.laser_plot_view.laser_selected() 
        
        if "Probe" in systems_selected:
            plot_probe = True
        
        if plot_probe is True:
            # TODO: Validate Pump is present or not
            delay_in_fs = self.laser_plot_view._var['delay'].get()
            delay_in_au = float(delay_in_fs)*fs_to_au 

            laser_data_1 = copy.deepcopy(self.laser_info.data['Pump'])
            laser_data_2 = copy.deepcopy(self.laser_info.data['Probe'])

            lasers_pump_probe = list(add_delay_to_lasers(system_1= laser_data_1, 
                                system_2= laser_data_2, delay=delay_in_au)) 

            if len(systems_selected)==1:
                lasers = [lasers_pump_probe[1]]
            else:
                lasers = lasers_pump_probe

        else:
            lasers = []
            for laser_system in systems_selected:
                _lasers = self.extract_laser_param_from_system(laser_system)
                # _lasers = self.extract_laser_param_from_system(laser_system)
                lasers.append(_lasers)

        lasers_to_plot = []
        for laser in lasers:
            lasers_to_plot.extend(laser)

        (time_arr, list_strength_arr) = m.get_time_strength(list_of_laser_params=lasers_to_plot,
                                                laser_profile_time= self.total_time*as_to_au*au_to_fs)
        # TODO: Modify plot method to add tag of laser
        # Add polarization as variable to filter out strengths
        m.plot_laser(time_arr, list_strength_arr)

    def extract_laser_param_from_system(self, laser_system:str):
        """ Specific to LaserPlotPage/ Returns list of laser 
        parameters to plot"""

        pulses = []    
        if laser_system in self.laser_info.data.keys():
            _pulses = self.laser_info.data[laser_system].get('pulses')
            pulses.extend(_pulses)
        laser_sets = extract_lasers_from_pulses(pulses)
        laser_params =[]
        for laser in laser_sets:
            laser_params.append(laser[0])
        return laser_params  

    # def _on_plot_w_delay_button(self, *_):
    #     from litesoph.utilities.units import fs_to_au, as_to_au, au_to_fs
    #     systems_selected = self.laser_plot_view.laser_selected()
    #     if len(systems_selected) == 0:
    #         systems_selected = self.laser_plot_view.tree.get_children()

    #     assert len(systems_selected) == 2

    #     name_1 = systems_selected[0]
    #     name_2 = systems_selected[1]

    #     laser_data_1 = copy.deepcopy(self.laser_info.data[name_1])
    #     laser_data_2 = copy.deepcopy(self.laser_info.data[name_2])

    #     delay_in_fs = self.laser_plot_view._var['delay'].get()
    #     delay_in_au = float(delay_in_fs)*fs_to_au        
    #     laser_list = list(add_delay_to_lasers(system_1= laser_data_1, 
    #                             system_2= laser_data_2, delay=delay_in_au))        

    #     lasers_to_plot = []
    #     for laser in laser_list:
    #         lasers_to_plot.extend(laser)

    #     (time_arr, list_strength_arr) = m.get_time_strength(lasers_to_plot,
    #                                         laser_profile_time= self.total_time*as_to_au*au_to_fs)
    #     m.plot_laser(time_arr, list_strength_arr) 


def validate_laser_defined(laser_data:dict, exp_type:str):
    """ Validates laser_defined wrt exp_type and returns the bool"""

    check = False
    assert exp_type in ["Pump-Probe", "State Preparation"]
    laser_info = m.LaserInfo(laser_data)

    if exp_type == "Pump-Probe":
        pump_defined = laser_info.check_laser_exists('Pump')
        probe_defined = laser_info.check_laser_exists('Probe')
        if all([pump_defined, probe_defined]):
            check = True
    if exp_type == "State Preparation":
        check = laser_info.check_laser_exists('State Preparation')

    return check    

def extract_lasers_from_pulses(list_of_pulses:list):
    """ Gets (laser_design,input parameters)
    \n from pulse objects as list of tuples"""
    lasers = []
    if len(list_of_pulses)> 0:
        for pulse in list_of_pulses:
            _laser_design = pulse.laser_design
            _laser_input = pulse.laser_input
            lasers.append((_laser_design, _laser_input))  
    return lasers

def add_delay_to_lasers(system_1:dict, system_2:dict, delay:float):
    """Adds delay between the laser systems and returns the updated ones,\n
    delay(in au) defined between last laser pulse centre of system 1 and\n
    first laser pulse centre of system 2"""

    sys1 = system_1
    sys2 = system_2

    pulses_sys1 = sys1['pulses']
    pulses_sys2 = sys2['pulses']

    set_sys1 = extract_lasers_from_pulses(pulses_sys1)
    set_sys2 = extract_lasers_from_pulses(pulses_sys2)

    lasers_sys1 = []
    lasers_sys2 = []

    for laser_set in set_sys1:
        lasers_sys1.append(laser_set[0])

    for laser_set in set_sys2:
        lasers_sys2.append(laser_set[0])

    last_params_sys1 = lasers_sys1[-1]
    first_params_sys2 = lasers_sys2[0]
    # Peak centre of last laser in system 1 (in au)
    time0_ref_1 = last_params_sys1.get('time0')
    # Peak centre of first laser in system 2 (in au)
    time0_ref_2 = first_params_sys2.get('time0')

    # Delay added for Probe system(in au)
    delay_to_add = float(time0_ref_1) + float(delay)- float(time0_ref_2)

    for i,laser_param in enumerate(lasers_sys2):
        _time0 = float(laser_param.get('time0'))
        laser_param['time0'] = _time0 + delay_to_add
    return (lasers_sys1, lasers_sys2)

class PostProcessTaskController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)        
        self.task_view.submit_button.config(command = self._run_task_serial)
        self.task_view.plot_button.config(command = self._on_plot_button)
        self.task_view.back_button.config(command= self.workflow_controller.show_workmanager_page)
           
        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def _run_task_serial(self, *_):
        
        inp_dict = self.task_view.get_parameters()
        self.task_info.param.update(inp_dict)
        self.task = self.workflow_manager.get_engine_task()
        self.task.prepare_input()
        self.task_info.state.input = 'done'
        self.task_info.engine_param.update(self.task.user_input)
        self._run_local(np=1)

class PumpProbePostProcessController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        try:
            self.task = self.workflow_manager.get_engine_task()
        except TaskSetupError as e:
            messagebox.showerror("Error", str(e))
            return
            
        self.task_view = self.app.show_frame(task_view)
        
        self.task_view.button_compute.config(command = self._on_compute_tas)
        self.task_view.button_plot.config(command = self._on_plot_tas)
        # self.task_view.back_button.config()


        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def _on_compute_tas(self, *_):
        inp_dict = self.task_view.get_parameters()
        try:
            self.task.generate_spectrums(**inp_dict)
            self.task.generate_tas_data()
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')
        else:
            messagebox.showinfo(message='Spectrums generated successfully.')


    def _on_plot_tas(self, *_):
        inp_dict = self.task_view.get_plot_parameters()
        try:
            self.task.plot(**inp_dict)
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')


def input_param_report(engine, input_param):
    pass            

def dict2string(inp_dict):

    txt = []
    for key, value in inp_dict.items():
        txt.append(f"{key} =  {value}")

    return '\n'.join(txt)

def get_laser_labels(laser_defined = False, num_lasers:int= 0):
    if not laser_defined:
        return None
    else:
        if num_lasers > 0:
            laser_label_list = list("laser"+ str(i+1) for i in range(num_lasers))
            return laser_label_list
        else:
            return None
        # else:
        #     raise ValueError("number of Lasers not found.")

def get_laser_tag():
    pass