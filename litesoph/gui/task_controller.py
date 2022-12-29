import tkinter as tk
from tkinter import messagebox
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list
import copy
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import Task, TaskFailed
from litesoph.common.task_data import TaskTypes as tt                                  
from litesoph.gui import views as v
from litesoph.common import models as m
from litesoph.gui.models.gs_model import choose_engine
from litesoph.common.decision_tree import EngineDecisionError

class TaskController:

    def __init__(self, workflow_controller, app) -> None:
        self.app = app
        self.workflow_controller = workflow_controller
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.status_engine = app.status_engine
        self.task_info = None
        self.task_view = None
        

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)
        
        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        
        self.task_view.set_sub_button_state('disable') 

        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    # def create_task_view(self, view_class, *args, **kwargs):
    #     self.task_view = view_class(self.app.task_input_frame, *args, **kwargs)
    #     self.task_view.grid(row=0, column=0, sticky ='NSEW')
    #     self.task_view.tkraise()

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
        self.main_window.bind_all(f'<<SubLocal{self.task_name}>>', lambda _ : self._on_run_local_button(self.task))
        self.main_window.bind_all(f'<<SubNetwork{self.task_name}>>', lambda _ : self._on_run_network_button(self.task))
    
    def _on_save_button(self, task:Task, view, *_):
        template = self.view_panel.get_text()
        task.set_engine_input(template)
        task.save_input()
        if task.task_name == tt.GROUND_STATE:
            self.status_engine.set(self.engine)
            #TODO: disable/freeze the inputs
            self.task_view.inp.freeze_widgets(state='disabled')
        view.set_sub_button_state('active')
        view.set_label_msg('saved')
    
    def _on_clear_button(self):
        pass

    def _on_run_network_button(self, task:Task, *_):

        if not self._check_task_run_condition(task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self.app.task_input_frame, task.task_name , 'Network')
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
        self.job_sub_page = v.JobSubPage(self.app.task_input_frame, task.task_name, 'Local')
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
            if task.task_info.local['returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {task.task_info.local['error']}")
            else:
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
            task.check_prerequisite()
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
            if task.task_info.network['sub_returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {task.task_info.network['error']}")
            else:
                 messagebox.showinfo(title= "Well done!", message='Job submitted successfully!', detail = f"output:{task.task_info.network['output']}")


    def _get_remote_output(self, task: Task):
        task.submit_network.download_output_files()

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

    def _on_out_remote_view_button(self,task: Task, *_):
        
        check =  task.task_info.network.get('sub_returncode', None)
        if check is None:
            messagebox.showinfo(title= "Warning", message="The job is not submitted yet.")
            return

        if check != 0:
            messagebox.showinfo(title= "Warning", message="Error occured during job submission.", detail = f"output:{task.task_info.network['output']}")
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
        txt = self.task.get_energy_coupling_constant(**inp_dict)
        self.view_panel.insert_text(text= txt, state= 'disabled')

    def _on_plot_dm_file(self, *_):
        inp_dict = self.task_view.get_parameters()
        self.task.plot(**inp_dict)

# class LaserPageController(TaskController):
class TDPageController(TaskController):

    def __init__(self, workflow_controller, app) -> None:
        super().__init__(workflow_controller, app)
        self.laser_design_bool = False
        self.pump_probe = False

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame, widget_dict:dict=None):
        
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name,
                                             input_widget_dict=widget_dict)
        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        self.main_window.bind_all('<<Design&EditLaser>>', self._on_design_edit_laser)         
        self.task_view.set_sub_button_state('disable')
        self.task_param = self.task_view.get_parameters()  

        # TODO: set initial parameters
        # if hasattr(self.task_view, 'set_parameters'):
        #     self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def set_laser_design_bool(self, bool:bool):
        self.laser_design_bool = bool

    def update_laser_on_td_page(self):
        """ Checks condition for laser designed/present"""

        if not self.laser_design_bool:
            #TODO: Resets the page
            pass 
        else:            
            #TODO: disable delay entry if pump-probe is chosen and delays are present
            # Choose one delay to generate and save input
            input_stored = self.workflow_manager.current_task_info.input
            if self.pump_probe:          
                self.task_view.inp.widget["delay_values"].config(values= input_stored.get('delay'))
                self.task_view.inp.widget["delay_values"].config(state = 'readonly')
                self.task_view.inp.widget["delay_values"].current(0)

                self.task_view.label_delay_entry.grid_remove()

            default_gui_dict = {
                "field_type": input_stored.get("field_type"),
                "exp_type" : input_stored.get("exp_type")
            }

            self.task_view.inp.init_widgets(fields=self.task_view.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)

            self.task_view.button_view.config(state='active')
            self.task_view.button_save.config(state='active')
            if self.task_view.label_delay_entry:
                self.task_view.label_delay_entry.grid_remove()

            #TODO: freeze required input entries
            # self.task_view.inp.freeze_widgets(state= 'disabled', input_keys = ["field_type","exp_type"])
              
    def _on_design_edit_laser(self, *_):
        """ On Laser design button, decides on showing LaserDesignPage and binds the widgets"""
        
        # TODO: Same LaserDesignPage to be compatible with handling edit/update/add/remove 

        field_type = self.task_param.get('field_type')
        exp_type = self.task_param.get('exp_type')
        self.pump_probe = bool(exp_type == "Pump-Probe")
        self.state_prepare = bool(exp_type == "State Preparation")

        if self.laser_design_bool:  
            # TODO:Remove this method/Toplevel for these options         
            self.laser_edit_view = v.LaserEditPage(self.main_window)
            self.main_window.bind_all('<<Add&ShowLaserPage>>', self._on_show_and_add_laser)
            self.main_window.bind_all('<<Choose&EditLaser>>', self._on_edit_laser)
            self.main_window.bind_all('<<Choose&RemoveLaser>>', self._on_remove_laser)
            return

            # TODO:Add the msg on whether to modify existing laser sets
            # check = messagebox.askyesno(message= "Laser is already designed.\n Do you want to edit again?")
            # if not check:
            #     return

        self._on_show_laser_page(show_stored= False)

    def _on_show_laser_page(self, show_stored:bool, *_):
        """ Assigns LaserDesignController and shows the LaserDesignPage """
        self.task_controller = LaserDesignController(self.workflow_controller, self.app)        
        
        # Collects TD input parameters from task_view and updates to current_task_info database
        task_view_param = self.task_view.get_parameters()
        self.workflow_manager.current_task_info.input.update(task_view_param)

        # Initiates LaserDesignPage and add existing laser attributes 
        # to task_controller(LaserDesignController)
        self.task_controller.set_task( self.workflow_manager, v.LaserDesignPage)
        self.task_controller.add_existing_lasers(stored_check=show_stored)
        self.workflow_manager.current_task_info = self.task_info

    def _on_edit_laser(self, *_):
        # TODO: Remove this method once LaserDesignPage is updated

        self.laser_info_view = v.LaserInfoPage(self.main_window)
        self.laser_info_view.show_edit_widgets()
        currrent_lasers = self.workflow_manager.current_task_info.input['current_lasers']
        self.laser_labels = get_laser_labels(laser_defined = True, 
                                            num_lasers = len(currrent_lasers))
        
        self.laser_info_view.cb_lasers.config(values=self.laser_labels)
        self.laser_info_view.cb_lasers.current(0)

        self.main_window.bind_all('<<Choose&EditLaser>>', self.choose_and_update_laser)   
        self.main_window.bind_all('<<Choose&RemoveLaser>>', self.choose_and_remove_laser)

    def _on_remove_laser(self, *_):        
        pass

    # def choose_and_update_laser(self):
    #     laser_index = str(self.laser_info_view.cb_lasers.get())
    #     pass

    # def choose_and_remove_laser(self):
    #     pass

    def _on_show_and_add_laser(self, *_):
        """ shows the laser Design Page with updated"""    
        self._on_show_laser_page(show_stored= True)  
        # self.task_controller.add_existing_lasers()
        
    def generate_input(self, *_):
        """ Checks experiment type and generate respective inputs"""
        #TODO: Condition for State preparation/pump-probe input 
        # Introduce delay when required

        self.task_info.param.clear()
        self.task_view.set_laser_design_dict(self.workflow_manager.current_task_info.input['current_lasers'])

        inp_dict = self.task_view.get_parameters()
        current_lasers = copy.deepcopy(self.workflow_manager.current_task_info.input['current_lasers'])       

        for i,laser in enumerate(current_lasers):        
            laser_tag = laser.get('tag')

            # TODO: alternatively, use respective list of pumps/probes
            if laser_tag is not None:
                assert laser_tag in ["Pump", "Probe"]
                # if laser_tag == "Pump":
                #     pump_id = i                  
                    
                if laser_tag == "Probe":
                    probe_id = i
                    break

        if inp_dict.get('pump_probe'):
            delay = self.task_view.inp.variable["delay_values"].get()
            pumps = self.workflow_manager.current_task_info.input['pump_lasers']
            copy_pumps = copy.deepcopy(pumps)
            probes = self.workflow_manager.current_task_info.input['probe_lasers']
            copy_probes = copy.deepcopy(probes)

            pump_param_on_delay = copy_pumps.pop()
            probe_param_on_delay = copy_probes[0]
            pump_on_delay_t0 = float(pump_param_on_delay.get('time0'))
            probe_on_delay_t0 = float(probe_param_on_delay.get('time0'))

            probe_t0_with_delay = pump_on_delay_t0 + delay + probe_on_delay_t0
            current_lasers[probe_id].update({'time0': probe_t0_with_delay})

            inp_dict.update({'laser': current_lasers})
        else:
            inp_dict.update({'laser': current_lasers})

        if not inp_dict:
            return
        check = messagebox.askokcancel(title='Input parameters selected', message= dict2string(inp_dict))
        if not check:
            return
        self.task_info.param.clear()
        self.task_info.param.update(inp_dict)
        self.task = self.workflow_manager.get_engine_task()
        self.task.create_input()
        txt = self.task.get_engine_input()
        self.view_panel.insert_text(text=txt, state='normal')
        self.bind_task_events()

class LaserDesignController(TaskController):

    def __init__(self, workflow_controller, app) -> None:
        super().__init__(workflow_controller, app)
        # self.laser_design_bool = False
        # self.laser_defined = False
        # self.pump_defined = False
        # self.probe_defined = False
        # self.list_of_pulses = []
        # self.list_of_laser_params = []
        # self.pump_lasers = []
        # self.probe_lasers = []
        # self.workflow_manager.current_task_info.input["gui_input"] = {}

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        # super().set_task(workflow_manager, task_view)

        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None
        
        self.task_param = self.workflow_manager.current_task_info.input
        self.time_step = self.workflow_manager.current_task_info.input.get('time_step')
        self.num_steps = self.workflow_manager.current_task_info.input.get('number_of_steps')
        self.total_time = self.time_step* self.num_steps

        if "gui_input" not in self.workflow_manager.current_task_info.input.keys():
            self.workflow_manager.current_task_info.input["gui_input"] = {}

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)

        self.main_window.bind_all('<<AddLaser>>', self._on_add_laser)
        # self.main_window.bind_all('<<EditLaser>>', self._on_edit_laser)
        self.main_window.bind_all('<<SaveLaser>>', self._on_save_laser)
        self.main_window.bind_all('<<PlotLaser>>', self._on_plot_laser)

        field_type = self.task_param.get('field_type')
        exp_type = self.task_param.get('exp_type')
        self.pump_probe = bool(exp_type == "Pump-Probe")

        if exp_type == "State Preparation":
            self.task_view.inp.widget["pump-probe_tag"].configure(state = 'disabled')
            self.task_view.inp.label["time_origin:pump"].grid_remove()
            self.task_view.inp.widget["time_origin:pump"].grid_remove()
            
        if self.pump_probe:
            self.task_view.inp.widget["pump-probe_tag"].configure(values = ["Pump"])
            self.task_view.inp.label["time_origin"].grid_remove()
            self.task_view.inp.widget["time_origin"].grid_remove() 
        
        # if hasattr(self.task_view, 'set_parameters'):
        #     self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def add_existing_lasers(self, stored_check:bool = False ):
        """ Store the existing laser details : exp_type, list_of_lasers
        to the current LaserDesignPage"""

        if not stored_check:
            self.laser_design_bool = False
            self.laser_defined = False
            self.pump_defined = False
            self.probe_defined = False
            self.list_of_pulses = []
            self.list_of_laser_params = []
            self.pump_lasers = []
            self.probe_lasers = []
            next_laser_label = "laser1"

            # Modified laser data structures
            self.current_lasers = {}
            self.pump_ref = []
            self.probe_ref = []

        else:
            print("adding existing lasers")
            print(self.workflow_manager.current_task_info.input)

            self.list_of_laser_params = self.workflow_manager.current_task_info.input["current_lasers"]
            # self.list_of_pulses = self.workflow_manager.current_task_info.input["current_pulses"]
            num_lasers = len(self.list_of_laser_params)
            next_laser_label = "laser"+str(num_lasers + 1)

        self.task_view.inp.variable["laser_label"].set(next_laser_label)

    def _on_add_laser(self, *_):  
        """On add laser button:
        \n Checks the validation for  time-origin forstate-preparation/pump-probe laser inputss
        \n Proceeds to append the lasers
        """
        laser_gui_inp = self.task_view.get_parameters()
        if not self.pump_probe:
            if len(self.list_of_laser_params) == 0:
                tin = laser_gui_inp.get('tin')
                zero_tin = bool(float(tin) < 1e-06)
                if zero_tin:
                    self.append_lasers()
                else:
                    messagebox.showerror(message="The first laser should have zero time origin")
                    return
            else:
                self.append_lasers()
        else:
            # check first pump and first probe
            tin = laser_gui_inp.get('tin')
            tag = laser_gui_inp.get('tag')

            assert tag in ["Pump", "Probe"]
            self.pump_tag = pump_tag = bool(tag == "Pump")
            self.probe_tag = probe_tag =bool(tag == "Probe")
            zero_tin = bool(float(tin) < 1e-06)

            if pump_tag:
                if len(self.pump_ref) == 0:                               
                    if zero_tin:
                        self.append_lasers(tag)
                    else:
                        messagebox.showerror(message="The first pump laser should have zero time origin")
                        return
                else:
                    self.append_lasers(tag)
            elif probe_tag:
                if len(self.probe_ref) == 0:                              
                    if zero_tin:
                        self.append_lasers(tag)
                    else:
                        messagebox.showerror(message="The first probe laser should have zero time origin")
                        return
                else:
                    self.append_lasers(tag)

    def append_lasers(self, tag= None):
        """ Appends and stores lasers to existing copies"""

        laser_model = self._on_design_laser()
        laser_info = laser_model.pulse_info
        laser_pulse = laser_info[0]
        laser_param = laser_info[1]
        # laser_param = laser_model.list_of_laser_param
               
        add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_param))
        if add_check:
            # TODO: update this list_of_laser_params
            laser_key = "laser_on_"+str(len(self.current_lasers))
            print(laser_key)           

            self.current_lasers.update({laser_key: laser_param})
            print(self.current_lasers)
            self.list_of_pulses.append(laser_pulse)
            tag = laser_param.get('tag')

            if tag is not None:
                if tag == "Pump":
                    self.pump_ref.append(laser_key)
                elif tag == "Probe":
                    self.probe_ref.append(laser_key)

            self.workflow_manager.current_task_info.input["gui_input"].update({
                laser_key: self.task_view.inp.get_values()
            })

            # current_laser_label = "laser"+str(len(self.list_of_laser_params))
            # next_laser_label = "laser"+str(len(self.list_of_laser_params)+1)
            # if tag is not None:
            #     if tag == "Pump":
            #         self.pump_lasers.extend(laser_model.list_of_laser_param)
            #         # label = "laser"+str(len(self.pump_lasers)+1)
            #         # self.task_view.inp.variable["laser_label"].set(label)
            #     elif tag == "Probe":
            #         self.probe_lasers.extend(laser_model.list_of_laser_param) 
            #         # label = "laser"+str(len(self.probe_lasers)+1)
            #         # self.task_view.inp.variable["laser_label"].set(label)
            # # else:
            # self.task_view.inp.variable["laser_label"].set(next_laser_label)

            # self.workflow_manager.current_task_info.input["gui_input"].update({
            #     current_laser_label: self.task_view.inp.get_values()
            # })
            # return


    # def append_lasers(self, tag= None):
    #     """ Appends and stores lasers to existing copies"""
    #     laser_model = self._on_design_laser()
    #     laser_param = laser_model.list_of_laser_param
               
    #     add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_param[0]))
    #     if add_check:
    #         # TODO: update this list_of_laser_params
    #         self.list_of_laser_params.extend(laser_model.list_of_laser_param)
    #         self.list_of_pulses.extend(laser_model.list_of_pulse)
    #         current_laser_label = "laser"+str(len(self.list_of_laser_params))
    #         next_laser_label = "laser"+str(len(self.list_of_laser_params)+1)
    #         if tag is not None:
    #             if tag == "Pump":
    #                 self.pump_lasers.extend(laser_model.list_of_laser_param)
    #                 # label = "laser"+str(len(self.pump_lasers)+1)
    #                 # self.task_view.inp.variable["laser_label"].set(label)
    #             elif tag == "Probe":
    #                 self.probe_lasers.extend(laser_model.list_of_laser_param) 
    #                 # label = "laser"+str(len(self.probe_lasers)+1)
    #                 # self.task_view.inp.variable["laser_label"].set(label)
    #         # else:
    #         self.task_view.inp.variable["laser_label"].set(next_laser_label)

    #         self.workflow_manager.current_task_info.input["gui_input"].update({
    #             current_laser_label: self.task_view.inp.get_values()
    #         })
    #         return

    # def _on_edit_laser(self, *_):
    #     # Remove this method at this level
    #     # TODO: Validation on available lasers
    #     self.laser_info_view = v.LaserInfoPage(self.main_window)
    #     self.laser_info_view.show_edit_widgets()
    #     self.laser_labels = get_laser_labels(laser_defined = True, 
    #                                             num_lasers = len(self.workflow_manager.current_task_info.input['current_lasers']))
        
    #     self.laser_info_view.cb_lasers.config(values=self.laser_labels)
    #     self.laser_info_view.cb_lasers.current(0)

    #     self.main_window.bind_all('<<Choose&EditLaser>>', self.choose_and_update_laser)   
    #     self.main_window.bind_all('<<Choose&RemoveLaser>>', self.choose_and_remove_laser)

    
    def _on_save_laser(self, *_):   
        """ The Save Laser Button:Checks laser bools 
        and finalises laser sets if laser is defined"""  

        self.check_laser_defined()        
        #TODO: add message if laser not defined
        if self.laser_defined:
            self._on_choose_laser()

            # if self.pump_probe:
            #     # TODO: Validate for atleast one pump, probe if pump-probe chosen
            #     if self.pump_defined is True and self.probe_defined is True:
            #         pass
            #     else:
            #         # if not self.pump_defined:
            #         #     messagebox.showerror(message="Please add one pump laser.")
            #         #     return 
            #         # if not self.probe_defined:
            #         #     messagebox.showerror(message="Please add one probe laser.")
            #         #     return 
            #         # else:
            #         messagebox.showerror(message="Please add lasers to save.")
            #         return 
            
          

    def check_laser_defined(self):
        """ Checks the conditions for laser defined"""
        if len(self.current_lasers) > 0:
            self.laser_defined = True
        if len(self.pump_ref) > 0:
            self.pump_defined = True
        if len(self.pump_ref) > 0:
            self.probe_defined = True 
        # if len(self.list_of_laser_params) > 0:
        #     self.laser_defined = True
        # if len(self.pump_lasers) > 0:
        #     self.pump_defined = True
        # if len(self.probe_lasers) > 0:
        #     self.probe_defined = True   

    def _on_choose_laser(self, *_):
        from litesoph.gui.models import inputs as inp
        check =False
        if not self.laser_defined:
            messagebox.showerror(message="Laser is not set. Please add lasers to save.")
            return

        if self.pump_probe:
            if self.pump_tag:
                check = messagebox.askokcancel(message= "Do you want to proceed with this pump laser set up?")
            elif self.probe_tag:
                check = messagebox.askokcancel(message= "Do you want to proceed with this probe laser set up?")
        else:
            check = messagebox.askokcancel(message= "Do you want to proceed with this laser set up?")
        
        if self.pump_probe:
            if self.pump_tag and self.pump_defined:
                if check is True:
                    # self.task_view.inp.widget["pump-probe_tag"].current(1)   
                    self.task_view.inp.widget["pump-probe_tag"].configure(values = ["Probe"])
                    self.task_view.inp.widget["pump-probe_tag"].current(0) 
                else:
                    pass
            if self.probe_tag and self.probe_defined:
                self.save_lasers_and_proceed(check=check)
        if not self.pump_probe:
            self.save_lasers_and_proceed(check=check)

    def save_lasers_and_proceed(self, check:bool=False):
        """ Finalise Lasers at currsent step and proceed"""

        from litesoph.gui.models import inputs as inp
        if check is True:
            self.task_controller = TDPageController(self.workflow_controller, self.app) 
            if self.pump_probe:
                # self.task_controller = TDPageController(self.workflow_controller, self.app) 
                self.task_controller.pump_probe = True
                # self.workflow_manager.current_task_info.input['pump_lasers'] = self.pump_lasers
                # self.workflow_manager.current_task_info.input['probe_lasers'] = self.probe_lasers

            # self.workflow_manager.current_task_info.input['current_lasers'] = self.list_of_laser_params
            self.workflow_manager.current_task_info.input['current_lasers'] = self.current_lasers
            self.laser_design_bool = self.task_controller.laser_design_bool = True

            #TODO: write the lasers to file     
            # self.laser_design.write(self.task_info.path /'laser.dat',self.laser_design.time, 
            #                               self.laser_design.strengths)       
            # self.workflow_manager.current_task_info.input["current_pulses"] = self.list_of_pulses

            copy_widget_dict = copy.deepcopy(inp.get_td_laser_w_delay())
            laser_labels = get_laser_labels(laser_defined = True, 
                                                num_lasers = len(self.list_of_laser_params))
            if laser_labels:
                copy_widget_dict.update(inp.update_widget_laser_details(laser_labels= laser_labels))
            self.task_controller.set_task(self.workflow_manager, v.TDPage, 
                                        widget_dict=copy_widget_dict) 
            self.task_controller.update_laser_on_td_page()
        else:
            print("Laser Sets needs review")
            self.laser_design_bool = False            

    def show_laser_delay(self, *_):
        self.laser_info_view = v.LaserInfoPage(self.main_window)
        self.laser_info_view.show_plot_widgets()
        self.laser_info_view.cb_delay.config(values=self.task_param.get('delay'))
        self.laser_info_view.cb_delay.current(0)

        self.main_window.bind_all('<<PlotwithDelay>>', self._plot_laser_w_delay)        

    def _plot_laser_w_delay(self,*_):
        delay = self.laser_info_view.get_value('delay')
        updated_laser_params = self.update_pump_probe_delay(self.list_of_laser_params, delay= delay)
        (time_arr, list_strength_arr) = self.laser_design.get_time_strength(updated_laser_params)
        self.laser_design.plot_laser()

    def _on_plot_laser(self, *_):
        if len(self.list_of_laser_params) > 0:
            self.laser_defined = True
        else:
            messagebox.showerror(message="Please add lasers to plot.")
            return

        if self.pump_probe:
            #TODO: Validate for atleast one pump and probe
            self.show_laser_delay()            
        else:
            (time_arr, list_strength_arr) = self.laser_design.get_time_strength(self.list_of_laser_params)
            self.laser_design.plot_laser()

    def update_pump_probe_delay(self, list_of_laser_params:list, delay:float):
        for i,laser in enumerate(list_of_laser_params):        
            laser_tag = laser.get('tag')

            # TODO: alternatively, use respective list of pumps/probes
            if laser_tag is not None:
                assert laser_tag in ["Pump", "Probe"]
                if laser_tag == "Pump":
                    pump_id = i                   
                    
                if laser_tag == "Probe":
                    probe_id = i
                    break

        pump_param_on_delay = list_of_laser_params[pump_id]
        probe_param_on_delay = list_of_laser_params[probe_id]
        pump_on_delay_t0 = float(pump_param_on_delay.get('time0'))
        probe_on_delay_t0 = float(probe_param_on_delay.get('time0'))

        probe_t0_with_delay = pump_on_delay_t0 + delay + probe_on_delay_t0
        list_of_laser_params[probe_id].update({'time0': probe_t0_with_delay})

        return list_of_laser_params

    def _on_design_laser(self, *_):
        """Collects inputs to compute laser parameters 
        and returns LaserDesignPlotModel object"""

        from litesoph.utilities.units import as_to_au, au_to_fs

        laser_design_inp = self.task_view.get_laser_details()  

        laser_total_time_fs = self.total_time*as_to_au*au_to_fs

        self.laser_design = m.LaserDesignPlotModel(laser_inputs =laser_design_inp,
                laser_profile_time= laser_total_time_fs)
        # self.pulse_list = self.laser_design.get_laser_pulse_list()
        # Make this multiple laser input dictionaries consistent with LaserDesignPlotModel
        self.pulse_info = self.laser_design.get_laser_param_pulse(laser_input= laser_design_inp)
    
        return self.laser_design

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
        self._run_local(self.task, np=1)


def input_param_report(engine, input_param):
    pass            

def dict2string(inp_dict):

    txt = []
    for key, value in inp_dict.items():
        txt.append(f"{key} =  {value}")

    return '\n'.join(txt)

def get_laser_labels(laser_defined = False, num_lasers:int= None):
    if not laser_defined:
        return None
    else:
        if num_lasers is not None:
            laser_label_list = list("laser"+ str(i+1) for i in range(num_lasers))
            return laser_label_list
        else:
            raise ValueError("number of Lasers not found.")

def get_laser_tag():
    pass