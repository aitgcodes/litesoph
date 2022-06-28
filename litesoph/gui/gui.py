from tkinter import *                    # importing tkinter, a standart python interface for gui.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox

import subprocess
from typing import OrderedDict                        # importing subprocess to run command line jobs as in terminal.
import tkinter as tk
import pygubu

import os
import platform
import pathlib 
import shutil
from configparser import ConfigParser, NoSectionError

#---LITESOPH modules
from litesoph.config import check_config, read_config
from litesoph.gui.logpanel import LogPanelManager
from litesoph.gui.menubar import get_main_menu_for_os
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list
from litesoph.gui.viewpanel import ViewPanelManager
from litesoph.lsio.IO import read_file
from litesoph.simulations import check_task_pre_conditon, get_engine_task, models as m
from litesoph.gui import views as v

from litesoph.simulations.esmd import Task
from litesoph.gui.navigation import ProjectList, summary_of_current_project
from litesoph.simulations.project_status import Status

home = pathlib.Path.home()

TITLE_FONT = ("Helvetica", 18, "bold")

DESINGER_DIR = pathlib.Path(__file__).parent

class GUIAPP:

    def __init__(self, lsconfig: ConfigParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lsconfig = lsconfig
        self.directory = None 

        self.builder = pygubu.Builder()

        self.builder.add_from_file(str(DESINGER_DIR / "main_window.ui"))

        self.main_window = self.builder.get_object('mainwindow')

        menu_class = get_main_menu_for_os('Linux')
        menu = menu_class(self.main_window)
        self.main_window.config(menu=menu)

        self.treeview = self.builder.get_object('treeview1')

        self.input_frame = self.builder.get_object('inputframe')

        self.navigation = ProjectList(self)
        
        self.view_panel = ViewPanelManager(self)

        self.status = None
        
        self.check = None
        
        self.engine = None

        self.setup_bottom_panel()

        self.status_engine = self.builder.get_variable('cengine_var')
        
        self.builder.connect_callbacks(self)

        self.ground_state_view = None
        self.ground_state_task = None
        
        self.laser_design = None

        self._frames = OrderedDict()
        
        self._show_page_events()
        self._bind_event_callbacks()
        self._show_frame(v.WorkManagerPage)
        self.main_window.after(1000, self.update_project_dir_tree)

    def run(self):
        self.main_window.protocol("WM_DELETE_WINDOW", self.__on_window_close)
        self.main_window.mainloop()

    def __on_window_close(self):
        """Manage WM_DELETE_WINDOW protocol."""
        self.main_window.withdraw()
        self.main_window.destroy()

    def quit(self):
        """Exit the app if it is ready for quit."""
        self.__on_window_close()

    def setup_bottom_panel(self):

        self.log_panel = LogPanelManager(self)

    def update_project_dir_tree(self):
        if self.directory:
            self.navigation.populate(self.directory)
        self.main_window.after(1000, self.update_project_dir_tree)
        
    def on_bpanel_button_clicked(self):
        self.log_panel.on_bpanel_button_clicked()

    def set_title(self, newtitle):
        self.current_title = newtitle
        default_title = 'LITESOPH - {0}'
        title = default_title.format(newtitle)
        self.main_window.wm_title(title)


    def _status_init(self, path):
        """Initializes the status object."""
        try:
            self.status = Status(path)
        except Exception as e:
            messagebox.showerror(message=f'status.json file might be corrupted. Unable to open the open {path.name}. error {e}')
            return False
        else:
            return True

    def _get_engine(self):

        engine_list = list(self.status.status_dict.keys())
        if engine_list:
            self.engine = engine_list[0]
            self.status_engine.set(self.engine)

    def _refresh_config(self,*_):
        """reads and updates the lsconfig object from lsconfig.ini"""
        self.lsconfig = read_config()
    
    def _show_frame(self, frame,*args, **kwargs):
        
        if frame in self._frames.keys():
            frame_obj = self._frames[frame]
            self._frames.move_to_end(frame, last=False)
            frame_obj.tkraise()
        else:
            int_frame = frame(self.input_frame, *args, **kwargs)
            self._frames[frame]= int_frame
            self._frames.move_to_end(frame, last=False)
            int_frame.grid(row=0, column=0, sticky ='NSEW')
            int_frame.tkraise()


    def _bind_event_callbacks(self):
        """binds events and specific callback functions"""
        event_callbacks = {
            '<<GetMolecule>>' : self._on_get_geometry_file,
            '<<VisualizeMolecule>>': self._on_visualize,
            '<<CreateNewProject>>' : self._on_create_project,
            '<<OpenExistingProject>>' : self._on_open_project,
            '<<SelectProceed>>' : self._on_proceed,
            '<<ClickBackButton>>' : self._on_back_button,
            '<<RefreshConfig>>': self._refresh_config,
        }

        for event, callback in event_callbacks.items():
            self.main_window.bind_all(event, callback)                
    
    def _show_page_events(self):
        
        event_show_page= {
            '<<ShowStartPage>>' : lambda _: self._show_frame(v.StartPage),
            '<<ShowWorkManagerPage>>' : self._show_workmanager_page,
            '<<ShowGroundStatePage>>' : self. _on_ground_state_task,
            '<<ShowRT_TDDFT_DELTAPage>>' : self._on_rt_tddft_delta_task,
            '<<ShowRT_TDDFT_LASERPage>>' : self._on_rt_tddft_laser_task,
            '<<ShowPlotSpectraPage>>' : self._on_spectra_task,
            '<<ShowDmLdPage>>' : lambda _: self._show_frame(v.DmLdPage, self),
            '<<ShowTcmPage>>' : self._on_tcm_task,
        }
        for event, callback in event_show_page.items():
            self.main_window.bind_all(event, callback)  

    def _on_back_button(self, *_):
        "generates a event to show the first frame in odered_dict"
        frame = list(self._frames)[1]
        self._show_frame(frame)

    def _change_directory(self, path):
        "changes current working directory"
        self.directory = pathlib.Path(path)
        os.chdir(self.directory) 

    def _show_workmanager_page(self, *_):

        self._show_frame(v.WorkManagerPage)
        if self.engine:
            self._frames[v.WorkManagerPage].engine.set(self.engine)

        if self.status:
            self.update_summary_of_project()

    def _init_project(self, path):
        
        path = pathlib.Path(path)
        if not self._status_init(path):       
            return
        self._change_directory(path)
        self.set_title(path.name)
        self.update_summary_of_project()
        #self.navigation.populate(self.directory)
        #self._get_engine()
        update_proj_list(path)
        self._get_engine()
        return True

    def _on_open_project(self, *_):
        """creates dialog to get project path and opens existing project"""
        project_path = filedialog.askdirectory(title= "Select the existing Litesoph Project")
        if not project_path:
            return
        self._init_project(project_path)
        if self.engine:
            self._frames[v.WorkManagerPage].engine.set(self.engine)
        
       
        
    def _on_create_project(self, *_):
        """Creates a new litesoph project"""
       
        project_name = self._frames[v.WorkManagerPage].get_value('proj_name')
        
        if not project_name:
            messagebox.showerror(title='Error', message='Please set the project name.')
            return

        project_path = filedialog.askdirectory(title= "Select the directory to create Litesoph Project")
        
        if not project_path:
            return

        project_path = pathlib.Path(project_path) / project_name
        
        try:
            m.WorkManagerModel.create_dir(project_path)
        except PermissionError as e:
            messagebox.showerror(title='Error', message = 'Premission denied', detail = e)
        except FileExistsError as e:
            messagebox.showerror(title='Error', message = 'Project already exists', detail =e)
        else:
            self._init_project(project_path)
            self.engine = None
            messagebox.showinfo("Message", f"project:{project_path} is created successfully")
            
        
    def _on_get_geometry_file(self, *_):
        """creates dialog to get geometry file and copies the file to project directory as coordinate.xyz"""
        try:
            self.geometry_file = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=[(" Text Files", "*.xyz")])
        except Exception as e:
            return
        else:
            if self.geometry_file:
                proj_path = pathlib.Path(self.directory) / "coordinate.xyz"
                shutil.copy(self.geometry_file, proj_path)
                self._frames[v.WorkManagerPage].show_upload_label()

    def _on_visualize(self, *_):
        """ Calls an user specified visualization tool """
        cmd = check_config(self.lsconfig,"vis") + ' ' + "coordinate.xyz"
        try:
           subprocess.run(cmd.split(),capture_output=True, cwd=self.directory)
        except:
            msg = "Cannot visualize molecule."
            detail ="Command used to call visualization program '{}'. supply the appropriate command in ~/.litesoph/lsconfig.ini".format(cmd.split()[0])
            messagebox.showerror(title='Error', message=msg, detail=detail) 
    
    def update_summary_of_project(self):
        
        summary = summary_of_current_project(self.status)
        self.view_panel.insert_text(summary, state='disabled')

    def _on_proceed(self, *_):

        simulation_type = [('electrons', 'None', '<<event>>'),
                        ('electrons', 'Delta Pulse', '<<ShowRT_TDDFT_DELTAPage>>'),
                        ('electrons', 'Gaussian Pulse', '<<ShowRT_TDDFT_LASERPage>>'),
                        ('electrons', 'Customised Pulse', '<<event>>'),
                        ('electron+ion', 'None', '<<event>>'),
                        ('electron+ion', 'Delta Pulse', '<<event>>'),
                        ('electron+ion', 'Gaussian Pulse', '<<event>>'),
                        ('electron+ion', 'Customised Pulse', '<<event>>'),
                        ('ions', 'None', '<<event>>'),
                        ('ions', 'Delta Pulse', '<<event>>'),
                        ('ions', 'Gaussian Pulse', '<<event>>'),
                        ('ions', 'Customised Pulse', '<<event>>')]

        w = self._frames[v.WorkManagerPage]
        sub_task = w.get_value('sub_task')
        task = w.get_value('task')
        self.engine = w.engine.get()

        if not self.directory:
            messagebox.showerror(title='Error', message='Please create project directory')
            return
            
        if task == '--choose job task--':
            messagebox.showerror(title='Error', message="Please choose job type")
            return

        if self.engine == 'auto-mode' and sub_task != "Ground State":
            self._get_engine()
            if not self.engine:
                messagebox.showerror(title= "Error", message="Please perform ground state calculation with any of the engine." )
                return

        if sub_task  == "Ground State":
            path = pathlib.Path(self.directory) / "coordinate.xyz"
            if path.exists() is True:
                self.main_window.event_generate('<<ShowGroundStatePage>>')
            else:
                messagebox.showerror(title = 'Error', message= "Upload geometry file")
                return
            return

        if task == "Simulations":

            if w.get_value('dynamics') == '--dynamics type--' or w.get_value('laser') == '-- laser type--':
                messagebox.showerror(title= 'Error',message="Please select the Sub task options")
                return

            for dynamics, laser, event in simulation_type:
                if dynamics == w.get_value('dynamics') and laser == w.get_value('laser'):
                    if event == "<<event>>":
                        messagebox.showinfo(title="Info", message="Option not Implemented")
                        return
                    else:
                        self.main_window.event_generate(event)
            return

        if sub_task in ["Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]:
            messagebox.showinfo(title='Info', message="This option is not yet Implemented.")
            return
        
        elif sub_task == "Compute Spectrum":
            self.main_window.event_generate('<<ShowPlotSpectraPage>>')   
        elif sub_task == "Dipole Moment and Laser Pulse":
            self.main_window.event_generate('<<ShowDmLdPage>>')
        elif sub_task == "Kohn Sham Decomposition":
               self.main_window.event_generate('<<ShowTcmPage>>')    

        w.refresh_var()

    @staticmethod
    def _check_task_run_condition(task, network=False) -> bool:
        
        try:
           task.check_prerequisite(network)           
        except FileNotFoundError as e:
            return False
        else:
            return True
##----------------------Ground_State_task---------------------------------

    def _on_ground_state_task(self, *_):
        self._frames[v.WorkManagerPage].refresh_var()
        self._show_frame(v.GroundStatePage, self.engine)
        self.ground_state_view = self._frames[v.GroundStatePage]
        if self.ground_state_view.engine.get() != self.engine:
            self.ground_state_view.engine.set(self.engine)
        self.ground_state_view.set_sub_button_state('disabled')
        self.ground_state_view.refresh_var()
        self.ground_state_view.set_label_msg('')
        self.view_panel.insert_text('')
        self.main_window.bind_all('<<SaveGroundStateScript>>', lambda _ : self._on_gs_save_button())
        self.main_window.bind_all('<<GenerateGroundStateScript>>', lambda _ : self._generate_gs_input())
        self.main_window.bind_all('<<SubLocalGroundState>>',  self._on_gs_run_local_button)
        self.main_window.bind_all('<<SubNetworkGroundState>>', self._on_gs_run_network_button)

    def _on_gs_save_button(self, *_):
        template = self.view_panel.get_text()
        self.ground_state_task.write_input(template)
        self.status.set_new_task(self.engine, self.ground_state_task.task_name)
        self.status.update_status(f'{self.engine}.{self.ground_state_task.task_name}.script', 1)
        self.status.update_status(f'{self.engine}.{self.ground_state_task.task_name}.param',self.ground_state_task.user_input)
        self.status_engine.set(self.engine)
        self.ground_state_view.set_sub_button_state('active')
        self.ground_state_view.set_label_msg('saved')
            
    def _generate_gs_input(self):
        inp_dict = self.ground_state_view.get_parameters()
        if not inp_dict:
            return
        self.engine = inp_dict.pop('engine')
        self.ground_state_task = get_engine_task(self.engine, 'ground_state', self.status, self.directory, self.lsconfig, inp_dict)
        self.ground_state_task.create_template()
        self.view_panel.insert_text(text=self.ground_state_task.template, state='normal')
        

    def _on_gs_run_local_button(self, *_):
        if not self._check_task_run_condition(self.ground_state_task):
            messagebox.showerror(title = 'Error', message="Input not saved. Please save the input before job submission")
            return

        self.ground_state_view.refresh_var()
        self.job_sub_page = v.JobSubPage(self.input_frame, 'GroundState', 'Local')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        self.job_sub_page.bind('<<RunGroundStateLocal>>', lambda _: self._run_local(self.ground_state_task))
        self.job_sub_page.bind('<<ViewGroundStateLocalOutfile>>', lambda _: self._on_out_local_view_button(self.ground_state_task))
        self.job_sub_page.bind('<<SaveGroundStateLocal>>',lambda _: self._on_save_job_script(self.ground_state_task))
        self.job_sub_page.bind('<<CreateGroundStateLocalScript>>', lambda _: self._on_create_local_job_script(self.ground_state_task,'GroundStateLocal'))

    def _on_gs_run_network_button(self, *_):

        if not self._check_task_run_condition(self.ground_state_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return

        self.ground_state_view.refresh_var()
        self.job_sub_page = v.JobSubPage(self.input_frame, 'GroundState', 'Network')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        remote = get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.bind('<<RunGroundStateNetwork>>', lambda _: self._run_network(self.ground_state_task))
        self.job_sub_page.bind('<<ViewGroundStateNetworkOutfile>>', lambda _: self. _on_out_remote_view_button(self.ground_state_task))
        self.job_sub_page.bind('<<SaveGroundStateNetwork>>',lambda _: self._on_save_job_script(self.ground_state_task))
        self.job_sub_page.bind('<<CreateGroundStateNetworkScript>>', lambda _: self._on_create_remote_job_script(self.ground_state_task,'GroundStateNetwork'))

##----------------------Time_dependent_task_delta---------------------------------

    def _on_rt_tddft_delta_task(self, *_):
        
        check = check_task_pre_conditon(self.engine, 'rt_tddft_delta', self.status)
        
        if check[0]:
            self.status_engine.set(self.engine)    
        else:
            messagebox.showinfo(title= "Info", message=check[1])
            return
        self._show_frame(v.TimeDependentPage, self.engine)
        self.rt_tddft_delta_view = self._frames[v.TimeDependentPage]
        self.rt_tddft_delta_view.add_job_frame('RT_TDDFT_DELTA')
        self.rt_tddft_delta_view.set_sub_button_state('disabled')
        self.rt_tddft_delta_view.update_engine_default(self.engine) 

        self.main_window.bind_all('<<SaveRT_TDDFT_DELTAScript>>', lambda _ : self._on_td_save_button())
        self.main_window.bind_all('<<GenerateRT_TDDFT_DELTAScript>>', lambda _ : self._generate_td_input())
        self.main_window.bind_all('<<SubLocalRT_TDDFT_DELTA>>',  self._on_td_run_local_button)
        self.main_window.bind_all('<<SubNetworkRT_TDDFT_DELTA>>',  self._on_td_run_network_button)

    def _on_td_save_button(self, *_):
        template = self.view_panel.get_text()
        self.rt_tddft_delta_task.write_input(template)
        self.status.set_new_task(self.engine, self.rt_tddft_delta_task.task_name)
        self.status.update_status(f'{self.engine}.{self.rt_tddft_delta_task.task_name}.script', 1)
        self.status.update_status(f'{self.engine}.{self.rt_tddft_delta_task.task_name}.param',self.rt_tddft_delta_task.user_input)
        self.rt_tddft_delta_view.set_sub_button_state('active')
        self.rt_tddft_delta_view.set_label_msg('saved')

    def _generate_td_input(self):
        inp_dict = self.rt_tddft_delta_view.get_parameters()
        self.rt_tddft_delta_task = get_engine_task(self.engine, 'rt_tddft_delta', self.status, self.directory, self.lsconfig, inp_dict)
        self.rt_tddft_delta_task.create_template()
        self.view_panel.insert_text(text=self.rt_tddft_delta_task.template, state='normal')
        self.rt_tddft_delta_view.set_label_msg('saved')

    def _on_td_run_local_button(self, *_):

        if not self._check_task_run_condition(self.rt_tddft_delta_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self.input_frame, 'RT_TDDFT_DELTA', 'Local')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        
        self.job_sub_page.bind('<<RunRT_TDDFT_DELTALocal>>', lambda _: self._run_local(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<ViewRT_TDDFT_DELTALocalOutfile>>', lambda _: self._on_out_local_view_button(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<SaveRT_TDDFT_DELTALocal>>',lambda _: self._on_save_job_script(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<CreateRT_TDDFT_DELTALocalScript>>', lambda _: self._on_create_local_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTALocal'))

    def _on_td_run_network_button(self, *_):

        if not self._check_task_run_condition(self.rt_tddft_delta_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self.input_frame, 'RT_TDDFT_DELTA', 'Network')
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
        remote = get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.activate_run_button()
        self.job_sub_page.bind('<<RunRT_TDDFT_DELTANetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<ViewRT_TDDFT_DELTANetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<SaveRT_TDDFT_DELTANetwork>>',lambda _: self._on_save_job_script(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<CreateRT_TDDFT_DELTANetworkScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

##----------------------Time_dependent_task_laser---------------------------------

    def _on_rt_tddft_laser_task(self, *_):

        check = check_task_pre_conditon(self.engine, 'rt_tddft_laser', self.status)
        
        if check[0]:
            self.status_engine.set(self.engine)    
        else:
            messagebox.showinfo(title= "Info", message=check[1])
            return
        self._show_frame(v.LaserDesignPage, self.engine)
        self.rt_tddft_laser_view = self._frames[v.LaserDesignPage]
        self.rt_tddft_laser_view.engine = self.engine

        self.main_window.bind_all('<<SaveRT_TDDFT_LASERScript>>', self._on_td_laser_save_button)
        self.main_window.bind_all('<<ViewRT_TDDFT_LASERScript>>',  self._on_td_laser_view_button)
        self.main_window.bind_all('<<SubRT_TDDFT_LASER>>',  self._on_td_laser_run_job_button)
        self.main_window.bind_all('<<DesignLaser>>', self._on_desgin_laser)
        self.main_window.bind_all('<<ChooseLaser>>', self._on_choose_laser)

    def _on_td_laser_save_button(self, *_):
        self._validate_td_laser_input()
        self._td_laser_create_input()
    
    def _on_desgin_laser(self, *_):
        laser_desgin_inp = self.rt_tddft_laser_view.get_laser_pulse()
        self.laser_design = m.LaserDesignModel(laser_desgin_inp)
        self.laser_design.create_pulse()
        self.rt_tddft_laser_view.show_laser_plot(self.laser_design.plot_time_strength())

    def _on_choose_laser(self, *_):
        if not self.laser_design:
            messagebox.showerror(message="Laser is not set. Please choose the laser")
            return
        check = messagebox.askokcancel(message= "Do you want to proceed with this laser set up?")
        if check is True:
            self.rt_tddft_laser_view.destroy_plot()
            self.rt_tddft_laser_view.activate_td_frame()
        else:
            self.laser_design = None 
            self._on_rt_tddft_laser_task()

    def _on_td_laser_view_button(self, *_):
        template = self._validate_td_laser_input()
        text_view = self._init_text_viewer('RT_TDDFT_LASER', template)
        text_view.bind('<<SaveRT_TDDFT_LASER>>', lambda _: self._td_laser_create_input(text_view.save_txt))
        text_view.bind('<<ViewRT_TDDFT_LASERPage>>', lambda _: self._show_frame(v.LaserDesignPage))

    def _validate_td_laser_input(self):
        self.rt_tddft_laser_view.set_laser_design_dict(self.laser_design.l_design)
        inp_dict = self.rt_tddft_laser_view.get_parameters()
        inp_dict['laser'] = self.laser_design.pulse.dict
        self.rt_tddft_laser_task = get_engine_task(self.engine, 'rt_tddft_laser', self.status, self.directory, self.lsconfig, inp_dict)
        self.rt_tddft_laser_task.create_template()
        return self.rt_tddft_laser_task.template

    def _td_laser_create_input(self, template=None):     
        self.rt_tddft_laser_task.write_input(template)
        self.status.set_new_task(self.engine, self.rt_tddft_laser_task.task_name)
        self.status.update_status(f'{self.engine}.{self.rt_tddft_laser_task.task_name}.script', 1)
        self.status.update_status(f'{self.engine}.{self.rt_tddft_laser_task.task_name}.param',self.rt_tddft_laser_task.user_input)
        self.rt_tddft_laser_view.set_label_msg('saved')
        self.check = False

    def _on_td_laser_run_job_button(self, *_):
        try:
            getattr(self.rt_tddft_laser_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(title = 'Error', message="Input not saved. Please save the input before job submission")
            return
        else:
            self.job_sub_page = v.JobSubPage(self.input_frame, 'RT_TDDFT_LASER')
            self.job_sub_page.grid(row=0, column=0, sticky ="nsew")
            self.job_sub_page.activate_run_button()
            self.job_sub_page.show_output_button('View Output','RT_TDDFT_LASER')
            self.job_sub_page.bind('<<RunRT_TDDFT_LASERLocal>>', lambda _: self._run_local(self.rt_tddft_laser_task))
            self.job_sub_page.bind('<<RunRT_TDDFT_LASERNetwork>>', lambda _: self._run_network(self.rt_tddft_laser_task))
        
##----------------------plot_delta_spec_task---------------------------------
    
    def _on_spectra_task(self, *_):

        check = check_task_pre_conditon(self.engine, 'spectrum', self.status)
        
        if check[0]:
            self.status_engine.set(self.engine)    
        else:
            messagebox.showinfo(title= "Info", message=check[1])
            return
        self._show_frame(v.PlotSpectraPage, self.engine)
        self.spectra_view = self._frames[v.PlotSpectraPage]
        self.spectra_view.engine = self.engine
        self.spectra_view.Frame1_Button2.config(state='active')
        self.spectra_view.Frame1_Button3.config(state='active')
        self.main_window.bind_all('<<SubLocalSpectrum>>', lambda _: self._on_spectra_run_local_button())
        self.main_window.bind_all('<<RunNetworkSpectrum>>', lambda _: self._on_spectra_run_network_button())
        self.main_window.bind_all('<<ShowSpectrumPlot>>', lambda _:self._on_spectra_plot_button())

    def _validate_spectra_input(self):
        inp_dict = self.spectra_view.get_parameters()
        self.spectra_task = get_engine_task(self.engine, 'spectrum', self.status, self.directory, self.lsconfig, inp_dict)

    def _spectra_create_input(self, template=None):     
        self.status.set_new_task(self.engine, self.spectra_task.task_name)
        self.status.update_status(f'{self.engine}.{self.spectra_task.task_name}.script', 1)
        self.status.update_status(f'{self.engine}.{self.spectra_task.task_name}.param',self.spectra_task.user_input)

    def _on_spectra_run_local_button(self, *_):
        
        self._validate_spectra_input()
        self._spectra_create_input()
        self.spectra_task.prepare_input()
        self._run_local(self.spectra_task, np=1)
        

    def _on_spectra_run_network_button(self, *_):
        
        return
        try:
            getattr(self.spectra_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self.input_frame, 'Spectrum', 'Network')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
            self.job_sub_page.bind('<<RunSpectrumNetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<ViewSpectrumNetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
            self.job_sub_page.text_view.bind('<<SaveSpectrumNetwork>>',lambda _: self._on_save_job_script(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<CreateSpectrumRemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

    def _on_spectra_plot_button(self, *_):
        """ Selects engine specific plot function"""
        self.spectra_task.plot()
    
        
##----------------------compute---tcm---------------------------------

    def _on_tcm_task(self, *_):

        check = check_task_pre_conditon(self.engine, 'tcm', self.status)
        
        if check[0]:
            self.status_engine.set(self.engine)    
        else:
            messagebox.showinfo(title= "Info", message=check[1])
            return

        self._show_frame(v.TcmPage, self.input_frame)
        self.tcm_view = self._frames[v.TcmPage]
        self.tcm_view.engine_name.set(self.engine)
        
        self.main_window.bind_all('<<SubLocalTCM>>', lambda _: self._on_tcm_run_local_button())
        self.main_window.bind_all('<<RunNetworkTCM>>', lambda _: self._on_tcm_run_network_button())
        self.main_window.bind_all('<<ShowTCMPlot>>', lambda _:self._on_tcm_plot_button())

    def _validate_tcm_input(self):
        inp_dict = self.tcm_view.get_parameters()
        self.tcm_task = get_engine_task(self.engine, 'tcm', self.status, self.directory, self.lsconfig, inp_dict)
        self.tcm_task.create_template()


    def _tcm_create_input(self, template=None):     
        self.tcm_task.write_input(template)
        self.status.set_new_task(self.engine,self.tcm_task.task_name)
        self.status.update_status(f'{self.engine}.{self.tcm_task.task_name}.script', 1)
        self.status.update_status(f'{self.engine}.{self.tcm_task.task_name}.param',self.tcm_task.user_input)
        #self.rt_tddft_laser_view.set_label_msg('saved')
        self.check = False

    def _on_tcm_run_local_button(self, *_):
        
        self._validate_tcm_input()
        self._tcm_create_input()

        self._run_local(self.tcm_task,np=1 )
        

    def _on_tcm_run_network_button(self, *_):

        return
        try:
            getattr(self.spectra_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self.input_frame, 'TCM', 'Network')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
            self.job_sub_page.bind('<<RunTCMNetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<ViewTCMNetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
            self.job_sub_page.text_view.bind('<<SaveTCMNetwork>>',lambda _: self._on_save_job_script(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<CreateTCMRemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

    def _on_tcm_plot_button(self, *_):
        """ Selects engine specific plot function"""
        try:
            self.tcm_task.plot()
        except Exception as e:
            messagebox.showerror(title='Error', message="Error occured during plotting", detail= e)

##-----------------------------------------------------------------------------------------------------------##

    def view_input_file(self, task:Task):
        self.view_panel.insert_text(task.template)


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
                self.job_sub_page.activate_run_button()
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.activate_run_button()
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
                self.status.update_status(f'{self.engine}.{task.task_name}.sub_local.returncode', task.local_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {task.local_cmd_out[2].decode(encoding='utf-8')}")
            else:
                self.status.update_status(f'{self.engine}.{task.task_name}.sub_local.returncode', 0)
                self.status.update_status(f'{self.engine}.{task.task_name}.sub_local.n_proc', np)
                self.status.update_status(f'{self.engine}.{task.task_name}.done', True)
                messagebox.showinfo(title= "Well done!", message='Job completed successfully!')
                

    def _on_out_local_view_button(self,task: Task, *_):

        log_file = self.directory.parent / task.output_log_file

        try:
            exist_status, stdout, stderr = task.local_cmd_out
        except AttributeError:
            messagebox.showinfo(title='Info', message="Job not completed.")
            return

        log_txt = read_file(log_file)
        self.view_panel.insert_text(log_txt, 'disabled')


    def _run_network(self, task):

        self.job_sub_page.disable_run_button()

        try:
            task.check_prerequisite(network = True)
        except FileNotFoundError as e:
            messagebox.showerror(title = "Error", message = e)
            self.job_sub_page.activate_run_button()
            return

        sub_job_type = self.job_sub_page.sub_job_type.get()

        cmd = self.job_sub_page.sub_command.get()
        if sub_job_type == 1:
            
            if not cmd:
                messagebox.showerror(title="Error", message=" Please provide submit command for queue submission")
                self.job_sub_page.activate_run_button()
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.activate_run_button()
                return

        
        login_dict = self.job_sub_page.get_network_dict()
        update_remote_profile_list(login_dict)
        
        from litesoph.utilities.job_submit import SubmitNetwork

        try:
            self.submit_network = SubmitNetwork(task, 
                                        hostname=login_dict['ip'],
                                        username=login_dict['username'],
                                        password=login_dict['password'],
                                        port=login_dict['port'],
                                        remote_path=login_dict['remote_path'],
                                        )
        except Exception as e:
            messagebox.showerror(title = "Error", message = e)
            self.job_sub_page.activate_run_button()
            return
        try:
            self.submit_network.run_job(cmd)
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            self.job_sub_page.activate_run_button()
            return
        else:
            if task.net_cmd_out[0] != 0:
                self.status.update_status(f'{self.engine}.{task.task_name}.sub_network.returncode', task.net_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {task.net_cmd_out[2].decode(encoding='utf-8')}")
            else:
                self.status.update_status(f'{self.engine}.{task.task_name}.sub_network.returncode', 0)
                messagebox.showinfo(title= "Well done!", message='Job submitted successfully!')


    def _get_remote_output(self):
        self.submit_network.download_output_files()
        self.status.update_status(f'{self.engine}.{self.submit_network.task.task_name}.done', True)

    def _on_create_local_job_script(self, task: Task, event: str, *_):
        np = self.job_sub_page.processors.get()
        b_file =  task.create_job_script(np)
        self.view_panel.insert_text(b_file, 'normal')

    def _on_create_remote_job_script(self, task: Task, event: str, *_):
        np = self.job_sub_page.processors.get()
        rpath = self.job_sub_page.rpath.get()
        if rpath:
            b_file =  task.create_job_script(np, remote_path=rpath, remote=True)
        else:
            messagebox.showerror(title="Error", message="Please enter remote path")
            return
        self.view_panel.insert_text(b_file, 'normal')
       
    def _on_save_job_script(self,task :Task, *_):
        txt = self.view_panel.get_text()
        task.write_job_script(txt)

    def _on_out_remote_view_button(self,task, *_):
        
        log_file = self.directory.parent / task.output_log_file

        try:
            exist_status, stdout, stderr = task.net_cmd_out
        except AttributeError:
            return

        # if exist_status != 0:
        #     return
        print("Checking for job completion..")
        if self.submit_network.check_job_status():

            # if self.network_type == 0:
            #     messagebox.showinfo(title='Info', message="Job commpleted.")
            print('job Done.')
            self._get_remote_output()   
            log_txt = read_file(log_file)
            #self.job_sub_page.text_view.clear_text()
            self.view_panel.insert_text(log_txt, 'disabled')

        else:
            get = messagebox.askyesno(title='Info', message="Job not commpleted.", detail= "Do you what to download engine log file?")

            if get:
                self.submit_network.get_output_log()
                log_txt = read_file(log_file)
                self.view_panel.insert_text(log_txt, 'disabled')
            else:
                return                

#--------------------------------------------------------------------------------        
if __name__ == '__main__':

    from litesoph.config import read_config
    
    app = GUIAPP(lsconfig=read_config())
    app.run()
