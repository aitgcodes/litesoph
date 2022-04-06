from tkinter import *                    # importing tkinter, a standart python interface for gui.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox

import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess
from typing import OrderedDict                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk

import os
import platform
import pathlib 
import shutil
from configparser import ConfigParser, NoSectionError

from matplotlib.pyplot import show

#---LITESOPH modules
from litesoph.config import check_config, read_config, set_config
from litesoph.gui.menubar import get_main_menu_for_os
from litesoph.lsio.IO import read_file
from litesoph.simulations import models as m
from litesoph.gui import views as v
from litesoph.simulations.engine import EngineNwchem 
from litesoph.visualization.spec_plot import plot_spectra, plot_files
from litesoph.simulations.esmd import Task
from litesoph.simulations.filehandler import Status, file_check, show_message
from litesoph.gui.navigation import ProjectList
from litesoph.simulations.filehandler import Status
from litesoph.utilities.job_submit import SubmitLocal
from litesoph.gui.visual_parameter import myfont, label_design

home = pathlib.Path.home()

TITLE_FONT = ("Helvetica", 18, "bold")

class GUIAPP(tk.Tk):

    def __init__(self, lsconfig: ConfigParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings_model = m.SettingsModel
        self._load_settings()
        self.lsconfig = lsconfig
        self.lsroot = check_config(self.lsconfig, "lsroot")
        self.directory = pathlib.Path(self.lsconfig.get("project_path", "lsproject", fallback=str(home)))
    

        menu_class = get_main_menu_for_os('Linux')
        menu = menu_class(self, self.settings)
        self.config(menu=menu)

        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill = tk.BOTH,side=tk.BOTTOM)
        self.status_bar.config(relief= tk.RAISED)
        
        # self.navigation_frame = ttk.Frame(self)
        # self.navigation_frame.pack(fill = tk.BOTH,side=tk.RIGHT)

        self.navigation = ProjectList(self)
        self.navigation.pack(fill = tk.BOTH,side=tk.LEFT)
        
        self.status = None
        
        self.check = None
        self._window = Frame(self)
        self._window.pack(fill = tk.BOTH, side=tk.LEFT)
        
        self.engine = None
        self.status_engine = tk.StringVar()
        ttk.Label(self.status_bar, textvariable=self.status_engine).pack(side= tk.LEFT) 
        
        self.ground_state_view = None
        self.ground_state_task = None
        
        self.laser_design = None

        self._frames = OrderedDict()
        
        self._show_page_events()
        self._bind_event_callbacks()
        self._show_frame(v.StartPage, self.lsroot)
        self.after(1000, self.navigation.populate(self.directory))
    
    
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
        try:
            self.engine = self.status.get_status('engine')
        except KeyError:
            self.engine = None
            self.status_engine.set('')
        else:
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
            int_frame = frame(self._window, *args, **kwargs)
            self._frames[frame]= int_frame
            self._frames.move_to_end(frame, last=False)
            int_frame.grid(row=0, column=1, sticky ='NSEW')
            int_frame.tkraise()


    def _bind_event_callbacks(self):
        """binds events and specific callback functions"""
        event_callbacks = {
            '<<GetMolecule>>' : self._on_get_geometry_file,
            '<<VisualizeMolecule>>': self._on_visualize,
            '<<CreateNewProject>>' : self._on_create_project,
            '<<OpenExistingProject>>' : self._on_open_project,
            '<<SelectTask>>' : self._on_task_select,
            '<<ClickBackButton>>' : self._on_back_button,
            '<<RefreshConfig>>': self._refresh_config,
            # '<<SaveGroundStateScript>>' : self._on_gs_save_button,
            # '<<ViewGroundStateScript>>' : self._on_gs_view_button,
            # '<<SubGroundState>>' : self._on_gs_run_job_button,
        }

        for event, callback in event_callbacks.items():
            self.bind(event, callback)                
    
    def _show_page_events(self):
        
        event_show_page= {
            '<<ShowStartPage>>' : lambda _: self._show_frame(v.StartPage, self.lsroot),
            '<<ShowWorkManagerPage>>' : lambda _: self._show_frame(v.WorkManagerPage, self.lsroot, self.directory),
            '<<ShowGroundStatePage>>' : self. _on_ground_state_task,
            '<<ShowTimeDependentPage>>' : self._on_rt_tddft_delta_task,
            '<<ShowLaserDesignPage>>' : self._on_rt_tddft_laser_task,
            '<<ShowPlotSpectraPage>>' : self._on_spectra_task,
            '<<ShowDmLdPage>>' : lambda _: self._show_frame(DmLdPage, self),
            '<<ShowTcmPage>>' : self._on_tcm_task,
        }
        for event, callback in event_show_page.items():
            self.bind(event, callback)  

    def _on_back_button(self, *_):
        "generates a event to show the first frame in odered_dict"
        frame = list(self._frames)[1]
        self._show_frame(frame)

    def _change_directory(self, path):
        "changes current working directory"
        self.directory = pathlib.Path(path)
        os.chdir(self.directory) 

    def _init_project(self, path):
        
        self.engine = None
        path = pathlib.Path(path)
        if not self._status_init(path):       
            return
        self._change_directory(path)
        self.navigation.populate(self.directory)
        self._get_engine()

    def _on_open_project(self, *_):
        """creates dialog to get porject path and opens existing project"""
        
        project_path = filedialog.askdirectory(title= "Select the existing Litesoph Project")
        if not project_path:
            return
        #self._frames[v.WorkManagerPage].update_project_entry(project_path)
        self._init_project(project_path)
       
        
    def _on_create_project(self, *_):
        """Creates a new litesoph project"""
       
        project_name = self._frames[v.WorkManagerPage].get_project_name()
        
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
            messagebox.showerror(e)
        except FileExistsError as e:
            messagebox.showerror(e)
        else:
            #self._frames[v.WorkManagerPage].update_project_entry(project_path)
            self._init_project(project_path)
            messagebox.showinfo("Message", f"project:{project_path} is created successfully")
            
        
    def _on_get_geometry_file(self, *_):
        """creates dialog to get geometry file and copies the file to project directory as coordinate.xyz"""
        try:
            self.geometry_file = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=[(" Text Files", "*.xyz")])
        except Exception as e:
            #print(e)
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
            detail ="Command used to call visualization program '{}'. supply the appropriate command in ~/lsconfig.ini".format(cmd.split()[0])
            messagebox.showerror(title='Error', message=msg, detail=detail) 

    def _on_task_select(self, *_):
        
        sub_task = self._frames[v.WorkManagerPage].get_sub_task()

        if sub_task  == "Ground State":
            path = pathlib.Path(self.directory) / "coordinate.xyz"
            if path.exists() is True:
                self.event_generate('<<ShowGroundStatePage>>')
            else:
                messagebox.showerror(title = 'Error', message= "Upload geometry file")
        # elif sub_task == "Delta Kick":
        #     self.event_generate('<<ShowTimeDependentPage>>')   
        # elif sub_task == "Gaussian Pulse":    
        #     self.event_generate('<<ShowLaserDesignPage>>')   
        elif sub_task == "Compute Spectrum":
            self.event_generate('<<ShowPlotSpectraPage>>')   
        elif sub_task == "Dipole Moment and Laser Pulse":
            self.event_generate('<<ShowDmLdPage>>')
        elif sub_task == "Kohn Sham Decomposition":
               self.event_generate('<<ShowTcmPage>>')    

        self._frames[v.WorkManagerPage].refresh_var()
    # def _on_task_select(self, *_):
        
    #     sub_task = self._frames[v.WorkManagerPage].sub_task.get()

    #     if sub_task  == "Ground State":
    #         path = pathlib.Path(self.directory) / "coordinate.xyz"
    #         if path.exists() is True:
    #             self.event_generate('<<ShowGroundStatePage>>')
    #         else:
    #             messagebox.showerror(message= "Upload geometry file")
    #     elif sub_task == "Delta Kick":
    #         if self.status.check_status('gs_inp', 1) is True and self.status.check_status('gs_cal',1) is True:
    #             self.event_generate('<<ShowTimeDependentPage>>')
    #         else:
    #             messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")       
    #     elif sub_task == "Gaussian Pulse":
    #         if self.status.check_status('gs_inp', 1) is True and self.status.check_status('gs_cal',1) is True:
    #             self.event_generate('<<ShowLaserDesignPage>')
    #         else:
    #             messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")
    #     elif sub_task == "Spectrum":
    #         if self.status.check_status('gs_cal', 1) is True:
    #             if self.status.check_status('td_cal',1) is True or self.status.check_status('td_cal',2) is True:
    #                 self.event_generate('<<ShowPlotSpectraPage>>')
    #         else:
    #             messagebox.showerror(message=" Please complete Ground State and Delta kick calculation.")
    #     elif sub_task == "Dipole Moment and Laser Pulse":
    #         if self.status.check_status('gs_cal', 1) is True and self.status.check_status('td_cal',2) is True:
    #             self.event_generate('<<ShowDmLdPage>>')
    #         else:
    #             messagebox.showerror(message=" Please complete Ground State and Gaussian Pulse calculation.")
    #     elif sub_task.get() == "Kohn Sham Decomposition":
    #            self.event_generate('<<ShowTcmPage>>')    


    @staticmethod
    def _check_task_run_condition(task, network=False) -> bool:
        
        if not task.task:
            return False

        try:
           task.check_prerequisite(network)           
        except FileNotFoundError as e:
            return False
        else:
            return True
##----------------------Ground_State_task---------------------------------

    def _on_ground_state_task(self, *_):
        self._show_frame(v.GroundStatePage, self)
        self.ground_state_view = self._frames[v.GroundStatePage]
        self.ground_state_view.set_sub_button_state('disabled')
        self.ground_state_view.refresh_var()
        self.ground_state_view.set_label_msg('')
        self.ground_state_task = Task(self.status, self.directory, self.lsconfig)

        self.bind('<<SaveGroundStateScript>>', lambda _ : self._on_gs_save_button())
        self.bind('<<ViewGroundStateScript>>', lambda _ : self._on_gs_view_button())
        self.bind('<<SubLocalGroundState>>',  self._on_gs_run_local_button)
        self.bind('<<SubNetworkGroundState>>', self._on_gs_run_network_button)

    def _on_gs_save_button(self, *_):
        if self._validate_gs_input():
            self._gs_create_input()
            self.ground_state_view.set_sub_button_state('active')

    def _on_gs_view_button(self, *_):
        template = self._validate_gs_input()
        if template:
            text_view = self._init_text_viewer('GroundState', template)
            text_view.bind('<<SaveGroundState>>', lambda _: self._gs_create_input(text_view.save_txt))
            text_view.bind('<<ViewGroundStatePage>>', lambda _: self._show_frame(v.GroundStatePage, self))

    def _validate_gs_input(self):
        inp_dict = self.ground_state_view.get_parameters()
        engine = inp_dict['engine']
        if self.engine:
            if self.engine != engine:
                messagebox.showerror(message = f'This {self.directory.name} project was started with {self.engine} engine. \n If you want to use different engine. Please create new project with that engine')
                return
        self.ground_state_task.set_engine(engine)
        self.ground_state_task.set_task('ground_state', inp_dict)
        self.ground_state_task.create_template()
        return self.ground_state_task.template

    def _gs_create_input(self, template=None):     
        confirm_engine = messagebox.askokcancel(message= "You have chosen {} engine. Rest of the calculations will use this engine.".format(self.ground_state_task.engine_name))
        if confirm_engine is True:
            self.engine = self.ground_state_task.engine_name
            try:
                self.ground_state_task.engine.create_restart_dir()
            except AttributeError:
                pass
            self.ground_state_task.write_input(template)
            self.status.update_status('engine', self.engine)
            self.status.set_new_task(self.ground_state_task.task_name)
            self.status.update_status(f'{self.ground_state_task.task_name}.script', 1)
            self.status.update_status(f'{self.ground_state_task.task_name}.param',self.ground_state_task.user_input)
            self.status_engine.set(self.engine)
            self.ground_state_view.set_label_msg('saved')
        else:
            pass  
        self.check = False

    def _on_gs_run_local_button(self, *_):
        
        if not self._check_task_run_condition(self.ground_state_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return

        self.ground_state_view.refresh_var()
        self.job_sub_page = v.JobSubPage(self._window, 'GroundState', 'Local')
        self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        self.job_sub_page.bind('<<RunGroundStateLocal>>', lambda _: self._run_local(self.ground_state_task))
        self.job_sub_page.bind('<<ViewGroundStateLocalOutfile>>', lambda _: self._on_out_local_view_button(self.ground_state_task))
        #self.job_sub_page.bind('<<Back2GroundState>>', lambda _: self._run_network(self.ground_state_task))

    def _on_gs_run_network_button(self, *_):

        if not self._check_task_run_condition(self.ground_state_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return

        self.ground_state_view.refresh_var()
        self.job_sub_page = v.JobSubPage(self._window, 'GroundState', 'Network')
        self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        remote = self._get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.bind('<<RunGroundStateNetwork>>', lambda _: self._run_network(self.ground_state_task))
        self.job_sub_page.bind('<<ViewGroundStateNetworkOutfile>>', lambda _: self. _on_out_remote_view_button(self.ground_state_task))
        self.job_sub_page.text_view.bind('<<SaveGroundStateNetwork>>',lambda _: self._on_save_remote_job_script(self.ground_state_task))
        self.job_sub_page.bind('<<CreateGroundStateRemoteScript>>', lambda _: self._on_create_remote_job_script(self.ground_state_task,'GroundStateNetwork'))

##----------------------Time_dependent_task_delta---------------------------------

    def _on_rt_tddft_delta_task(self, *_):
        self._show_frame(v.TimeDependentPage, self, self.engine)
        self.rt_tddft_delta_view = self._frames[v.TimeDependentPage]
        self.rt_tddft_delta_view.add_job_frame('RT_TDDFT_DELTA')
        self.rt_tddft_delta_view.set_sub_button_state('disabled')
        self.rt_tddft_delta_view.update_engine_default(self.engine) 
        self.rt_tddft_delta_task = Task(self.status, self.directory, self.lsconfig)

        self.bind('<<SaveRT_TDDFT_DELTAScript>>', lambda _ : self._on_td_save_button())
        self.bind('<<ViewRT_TDDFT_DELTAScript>>', lambda _ : self._on_td_view_button())
        self.bind('<<SubLocalRT_TDDFT_DELTA>>',  self._on_td_run_local_button)
        self.bind('<<SubNetworkRT_TDDFT_DELTA>>',  self._on_td_run_network_button)

    def _on_td_save_button(self, *_):
        self._validate_td_input()
        self._td_create_input()
        self.rt_tddft_delta_view.set_sub_button_state('active')

    def _on_td_view_button(self, *_):
        template = self._validate_td_input()
        text_view = self._init_text_viewer('RT_TDDFT_DELTA', template)
        text_view.bind('<<SaveRT_TDDFT_DELTA>>', lambda _: self._td_create_input(text_view.save_txt))
        text_view.bind('<<ViewRT_TDDFT_DELTAPage>>', lambda _: self._show_frame(v.TimeDependentPage))

    def _validate_td_input(self):
        inp_dict = self.rt_tddft_delta_view.get_parameters()
        self.rt_tddft_delta_task.set_engine(self.engine)
        self.rt_tddft_delta_task.set_task('rt_tddft_delta', inp_dict)
        self.rt_tddft_delta_task.create_template()
        return self.rt_tddft_delta_task.template

    def _td_create_input(self, template=None):     
        self.rt_tddft_delta_task.write_input(template)
        self.status.set_new_task(self.rt_tddft_delta_task.task_name)
        self.status.update_status(f'{self.rt_tddft_delta_task.task_name}.script', 1)
        self.status.update_status(f'{self.rt_tddft_delta_task.task_name}.param',self.rt_tddft_delta_task.user_input)
        self.rt_tddft_delta_view.set_label_msg('saved')
        self.check = False

    def _on_td_run_local_button(self, *_):

        if not self._check_task_run_condition(self.rt_tddft_delta_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self._window, 'RT_TDDFT_DELTA', 'Local')
        self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
        self.job_sub_page.activate_run_button()
        
        self.job_sub_page.bind('<<RunRT_TDDFT_DELTALocal>>', lambda _: self._run_local(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<ViewRT_TDDFT_DELTALocalOutfile>>', lambda _: self._on_out_local_view_button(self.rt_tddft_delta_task))
        

    def _on_td_run_network_button(self, *_):

        if not self._check_task_run_condition(self.rt_tddft_delta_task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
        self.job_sub_page = v.JobSubPage(self._window, 'RT_TDDFT_DELTA', 'Network')
        self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
        remote = self._get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.activate_run_button()
        self.job_sub_page.bind('<<RunRT_TDDFT_DELTANetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<ViewRT_TDDFT_DELTANetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
        self.job_sub_page.text_view.bind('<<SaveRT_TDDFT_DELTANetwork>>',lambda _: self._on_save_remote_job_script(self.rt_tddft_delta_task))
        self.job_sub_page.bind('<<CreateRT_TDDFT_DELTARemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

##----------------------Time_dependent_task_laser---------------------------------

    def _on_rt_tddft_laser_task(self, *_):
        self._show_frame(v.LaserDesignPage, self, self.engine)
        self.rt_tddft_laser_view = self._frames[v.LaserDesignPage]
        self.rt_tddft_laser_view.engine = self.engine
        self.rt_tddft_laser_task = Task(self.status, self.directory, self.lsconfig)

        self.bind('<<SaveRT_TDDFT_LASERScript>>', self._on_td_laser_save_button)
        self.bind('<<ViewRT_TDDFT_LASERScript>>',  self._on_td_laser_view_button)
        self.bind('<<SubRT_TDDFT_LASER>>',  self._on_td_laser_run_job_button)
        self.bind('<<DesignLaser>>', self._on_desgin_laser)
        self.bind('<<ChooseLaser>>', self._on_choose_laser)

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
        self.rt_tddft_laser_task.set_engine(self.engine)
        self.rt_tddft_laser_task.set_task('rt_tddft_laser', inp_dict)
        self.rt_tddft_laser_task.create_template()
        return self.rt_tddft_laser_task.template

    def _td_laser_create_input(self, template=None):     
        self.rt_tddft_laser_task.write_input(template)
        self.status.set_new_task(self.rt_tddft_laser_task.task_name)
        self.status.update_status(f'{self.rt_tddft_laser_task.task_name}.script', 1)
        self.status.update_status(f'{self.rt_tddft_laser_task.task_name}.param',self.rt_tddft_laser_task.user_input)
        self.rt_tddft_laser_view.set_label_msg('saved')
        self.check = False

    def _on_td_laser_run_job_button(self, *_):
        try:
            getattr(self.rt_tddft_laser_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(title = 'Error', message="Input not saved. Please save the input before job submission")
            return
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'RT_TDDFT_LASER')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
            self.job_sub_page.activate_run_button()
            self.job_sub_page.show_output_button('View Output','RT_TDDFT_LASER')
            self.job_sub_page.bind('<<RunRT_TDDFT_LASERLocal>>', lambda _: self._run_local(self.rt_tddft_laser_task))
            self.job_sub_page.bind('<<RunRT_TDDFT_LASERNetwork>>', lambda _: self._run_network(self.rt_tddft_laser_task))
        
##----------------------plot_delta_spec_task---------------------------------
    
    def _on_spectra_task(self, *_):
        self._show_frame(v.PlotSpectraPage, self, self.engine)
        self.spectra_view = self._frames[v.PlotSpectraPage]
        self.spectra_view.engine = self.engine
        self.spectra_task = Task(self.status, self.directory, self.lsconfig)
        print('_on_spectra_task')
        self.spectra_view.Frame1_Button2.config(state='disabled')
        self.spectra_view.Frame1_Button3.config(state='disabled')
        self.bind('<<CreateSpectraScript>>', self._on_create_spectra_button)
        self.bind('<<SubLocalSpectrum>>', lambda _: self._on_spectra_run_local_button())
        self.bind('<<RunNetworkSpectrum>>', lambda _: self._on_spectra_run_network_button())
        # self.job_sub_page.bind('<<ShowSpectrumPlot>>', lambda _:plot_spectra(1,str(self.directory)+'/Spectrum/spec.dat',str(self.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None))
        self.bind('<<ShowSpectrumPlot>>', lambda _:self._on_spectra_plot_button())

    def _validate_spectra_input(self):
        self.status.get_status('rt_tddft_delta.param.pol_dir')
        inp_dict = self.spectra_view.get_parameters()
        self.spectra_task.set_engine(self.engine)
        self.spectra_task.set_task('spectrum',inp_dict)
        self.spectra_task.create_template()
        return self.spectra_task.template    

    def _on_create_spectra_button(self, *_):

        if self.engine == 'nwchem':
            return
        self._validate_spectra_input()
        self._spectra_create_input()

    def _spectra_create_input(self, template=None):     
        self.spectra_task.write_input(template)
        self.status.set_new_task(self.spectra_task.task_name)
        self.status.update_status(f'{self.spectra_task.task_name}.script', 1)
        self.status.update_status(f'{self.spectra_task.task_name}.param',self.spectra_task.user_input)
        #self.rt_tddft_laser_view.set_label_msg('saved')
        messagebox.showinfo(title='Info', message="Input Saved.")
        self.spectra_view.Frame1_Button2.config(state='active')
        self.spectra_view.Frame1_Button3.config(state='active')
        self.check = False

    def _on_spectra_run_local_button(self, *_):
        from litesoph.simulations.nwchem.nwchem_template import nwchem_compute_spec

        if self.engine == 'nwchem':
            pol =  self.status.get_status('rt_tddft_delta.param.pol_dir')
            if pol == 0:
                pol = 'x'
            elif pol == 1:
                pol = 'y'
            elif pol == 2:
                pol = 'z'
            try:
                nwchem_compute_spec(self.directory, pol)
            except Exception as e:
                messagebox.showerror(title = 'Error', message="Error occured.", detail = f"{e}")
            else:
                messagebox.showinfo(title= "Info", message=" Job Done! \nSpectrum calculated." )
            return

        if not self._check_task_run_condition(self.spectra_task):
            messagebox.showerror(message="Input not saved.", detail = "Please save the input before job submission")
            return

        
        self._run_local(self.spectra_task, np=1)
        

    def _on_spectra_run_network_button(self, *_):
        try:
            getattr(self.spectra_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'Spectrum', 'Network')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
            #self.job_sub_page.show_output_button('Plot','SpectrumPlot')
            self.job_sub_page.bind('<<ShowSpectrumPlot>>', lambda _:plot_spectra(1,str(self.directory)+'/Spectrum/spec.dat',str(self.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None))
            self.job_sub_page.bind('<<RunSpectrumNetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<ViewSpectrumNetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
            self.job_sub_page.text_view.bind('<<SaveSpectrumNetwork>>',lambda _: self._on_save_remote_job_script(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<CreateSpectrumRemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

    def _on_spectra_plot_button(self, *_):
        """ Selects engine specific plot function"""
        
        pol =  self.status.get_status('rt_tddft_delta.param.pol_dir')
        img = pathlib.Path(self.directory) / f"spec_{pol[1]}.png"

        if self.engine == "gpaw":
            spec_file = self.spectra_task.engine.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            self.show_plot(file,img,0, pol[0]+1, "Energy (in eV)", "Strength(in /eV)")
            # ax.plot(data_ej[:, 0], data_ej[:, column], 'k')

        elif self.engine == "octopus":
            spec_file = self.spectra_task.engine.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            self.show_plot(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")

        elif self.engine == "nwchem":
            spec_file = EngineNwchem.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            self.show_plot(file,img,0, 2, "Energy","Strength")
            # ax.plot(data_ej[:, 0], data_ej[:, 2], 'k') 

    def show_plot(self, filename,imgfile,row:int, column:int, x:str, y:str):  
        """ Shows the plot"""
             
        import numpy as np
        import matplotlib.pyplot as plt
        data_ej = np.loadtxt(filename) 
        plt.figure(figsize=(8, 6))
        ax = plt.subplot(1, 1, 1) 
        ax.plot(data_ej[:, row], data_ej[:, column], 'k')                  
        # if conversion is not None:
        #     ax.plot(data_ej[:, 0]*conversion, data_ej[:, axis], 'k')
        # else:
        #     ax.plot(data_ej[:, 0], data_ej[:, axis], 'k')          
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.xlabel(x)
        plt.ylabel(y)
        # plt.xlabel('Energy (eV)')
        # plt.ylabel('Photoabsorption (eV$^{-1}$)')
        #plt.xlim(0, 4)
        #plt.ylim(ymin=0)
        plt.tight_layout()
        plt.savefig(imgfile)
        plt.show()                   
##----------------------compute---tcm---------------------------------

    def _on_tcm_task(self, *_):

        if self.engine != 'gpaw':
            messagebox.showinfo(title='Info', message='Curretly this option is only implemented for Gpaw. ')
            return
        self._show_frame(TcmPage, self._window)
        self.tcm_view = self._frames[TcmPage]
        
        self.tcm_task = Task(self.status, self.directory, self.lsconfig)
        self.bind('<<CreateTCMScript>>', self._on_create_tcm_button)
        self.bind('<<SubLocalTCM>>', lambda _: self._on_tcm_run_local_button())
        self.bind('<<RunNetworkTCM>>', lambda _: self._on_tcm_run_network_button())
        # self.job_sub_page.bind('<<ShowSpectrumPlot>>', lambda _:plot_spectra(1,str(self.directory)+'/Spectrum/spec.dat',str(self.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None))
        self.bind('<<ShowTCMPlot>>', lambda _:self._on_tcm_plot_button())

    def _validate_tcm_input(self):
        inp_dict = self.tcm_view.get_parameters()
        self.tcm_task.set_engine(self.engine)
        self.tcm_task.set_task('tcm',inp_dict)
        self.tcm_task.create_template()
        return self.tcm_task.template    

    def _on_create_tcm_button(self, *_):

        self._validate_tcm_input()
        self._tcm_create_input()

    def _tcm_create_input(self, template=None):     
        self.tcm_task.write_input(template)
        self.status.set_new_task(self.tcm_task.task_name)
        #self.rt_tddft_laser_view.set_label_msg('saved')
        self.check = False

    def _on_tcm_run_local_button(self, *_):
        
        if not self._check_task_run_condition(self.tcm_task):
            messagebox.showerror(message="Input not saved.", detail = "Please save the input before job submission")
            return

        
        self._run_local(self.tcm_task,np=1 )
        

    def _on_tcm_run_network_button(self, *_):
        try:
            getattr(self.spectra_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'TCM', 'Network')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")
            #self.job_sub_page.show_output_button('Plot','SpectrumPlot')
            #self.job_sub_page.bind('<<ShowSpectrumPlot>>', lambda _:plot_spectra(1,str(self.directory)+'/Spectrum/spec.dat',str(self.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None))
            self.job_sub_page.bind('<<RunTCMNetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<ViewTCMNetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
            self.job_sub_page.text_view.bind('<<SaveTCMNetwork>>',lambda _: self._on_save_remote_job_script(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<CreateTCMRemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

    def _on_tcm_plot_button(self, *_):
        """ Selects engine specific plot function"""
        from PIL import Image
       
        for item in self.tcm_task.user_input['frequency_list']:
            img_file = pathlib.Path(self.directory) / 'TCM' / f'tcm_{item:.2f}.png'
            
            image = Image.open(img_file)
            image.show()
            # img = mpimg.imread(img_file)
            # plt.imshow(img)
            # plt.show()


    def _init_text_viewer(self,name, template, *_):
        #self._show_frame(v.TextViewerPage, self)
        text_view = v.TextViewerPage(self._window)
        text_view.grid(row=0, column=1, sticky ="nsew")
        text_view.set_task_name(name)
        text_view.insert_text(template)
        return text_view

    def _get_remote_profile(self):
        try:
            remote = self.lsconfig.items('remote_profile')
        except NoSectionError:
            return
        
        return remote

    

    def _run_local(self, task, np=None):
        if np:
            submitlocal = SubmitLocal(task, np)
        else:
            np = self.job_sub_page.get_processors()
            self.job_sub_page.disable_run_button()
            #task.prepare_input(self.directory, task.file_path)
            submitlocal = SubmitLocal(task, np)
        try:
            submitlocal.prepare_input(self.directory)
        except FileNotFoundError as e:
            messagebox.showerror(title='yes',message=e)
            return
        try:
            submitlocal.run_job()
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            return
        else:
            if task.local_cmd_out[0] != 0:
                self.status.update_status(f'{task.task_name}.sub_local.returncode', task.local_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {task.local_cmd_out[2].decode(encoding='utf-8')}")
            else:
                self.status.update_status(f'{task.task_name}.sub_local.returncode', 0)
                self.status.update_status(f'{task.task_name}.sub_local.n_proc', np)
                messagebox.showinfo(title= "Well done!", message='Job completed successfully!')
                

    def _on_out_local_view_button(self,task: Task, *_):

        self.job_sub_page.text_view.clear_text()
        log_file = self.directory.parent / task.output_log_file

        try:
            exist_status, stdout, stderr = task.local_cmd_out
        except AttributeError:
            messagebox.showinfo(title='Info', message="Job not completed.")
            return

        log_txt = read_file(log_file)
        self.job_sub_page.text_view.insert_text(log_txt, 'disabled')


    def _run_network(self, task):

        self.job_sub_page.disable_run_button()

        try:
            task.check_prerequisite(network = True)
        except FileNotFoundError as e:
            messagebox.showerror(title = "Error", message = e)
            return

        self.network_type = self.job_sub_page.network_job_type.get()
        
        login_dict = self.job_sub_page.get_network_dict()
        set_config(self.lsconfig,'remote_profile','ip',login_dict['ip'])
        set_config(self.lsconfig,'remote_profile','username',login_dict['username'])
        set_config(self.lsconfig,'remote_profile','remote_path',login_dict['remote_path'])

        
        from litesoph.utilities.job_submit import SubmitNetwork

        try:
            self.submit_network = SubmitNetwork(task, 
                                        hostname=login_dict['ip'],
                                        username=login_dict['username'],
                                        password=login_dict['password'],
                                        remote_path=login_dict['remote_path'],
                                        )
        except Exception as e:
            messagebox.showerror(title = "Error", message = e)
            self.job_sub_page.activate_run_button()
            return
        try:
            if self.network_type== 0:
                self.submit_network.run_job('qsub')
            elif self.network_type == 1:
                self.submit_network.run_job('bash')
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            self.job_sub_page.activate_run_button()
            return
        else:
            if task.net_cmd_out[0] != 0:
                self.status.update_status(f'{task.task_name}.sub_network.returncode', task.net_cmd_out[0])
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {task.net_cmd_out[2].decode(encoding='utf-8')}")
            else:
                self.status.update_status(f'{task.task_name}.sub_network.returncode', 0)
                messagebox.showinfo(title= "Well done!", message='Job submitted successfully!')


    def _get_remote_output(self):
        self.submit_network.download_output_files()

    def _on_create_remote_job_script(self, task: Task, event: str, *_):
        np = self.job_sub_page.processors.get()
        b_file =  task.create_remote_job_script(np)
        self.job_sub_page.text_view.set_event_name( event)
        self.job_sub_page.text_view.insert_text(b_file, 'normal')
       
    def _on_save_remote_job_script(self,task :Task, *_):
        txt = self.job_sub_page.text_view.get_text()
        task.write_remote_job_script(txt)

    def _on_out_remote_view_button(self,task, *_):
        
        self.job_sub_page.text_view.clear_text()
        log_file = self.directory.parent / task.output_log_file

        try:
            exist_status, stdout, stderr = task.net_cmd_out
        except AttributeError:
            return

        # if exist_status != 0:
        #     return

        if self.submit_network.check_job_status():

            if self.network_type == 0:
                messagebox.showinfo(title='Info', message="Job commpleted.")

            self._get_remote_output()   
            log_txt = read_file(log_file)
            self.job_sub_page.text_view.clear_text()
            self.job_sub_page.text_view.insert_text(log_txt, 'disabled')

        else:
            get = messagebox.askokcancel(title='Info', message="Job not commpleted.", detail= "Do you what to download engine log file?")

            if get:
                self.submit_network.get_output_log()
                log_txt = read_file(log_file)
                self.job_sub_page.text_view.insert_text(log_txt, 'disabled')
            else:
                return                
        
        

    def _load_settings(self):
        """Load settings into our self.settings dict"""

        vartypes = {
            'bool' : tk.BooleanVar,
            'str' : tk.StringVar,
            'int' : tk.IntVar,
            'float' : tk.DoubleVar
        }

        self.settings = dict()
        for key, data in self.settings_model.options.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])
            
        for var in self.settings.values():
            var.trace_add('write', self._save_settings)

    def _save_settings(self, *_):
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()


# class PlotSpectraPage(Frame):

#     def __init__(self, parent, controller, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.controller = controller
        

#         self.axis = StringVar()

#         myFont = font.Font(family='Helvetica', size=10, weight='bold')

#         j=font.Font(family ='Courier', size=20,weight='bold')
#         k=font.Font(family ='Courier', size=40,weight='bold')
#         l=font.Font(family ='Courier', size=15,weight='bold')
        
#         self.Frame = tk.Frame(self) 
        
#         self.Frame.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.978)
#         self.Frame.configure(relief='groove')
#         self.Frame.configure(borderwidth="2")
#         self.Frame.configure(relief="groove")
#         self.Frame.configure(cursor="fleur")
        
#         self.heading = Label(self.Frame,text="LITESOPH Spectrum Calculations and Plots", fg='blue')
#         self.heading['font'] = myFont
#         self.heading.place(x=350,y=10)
        
#         self.label_pol = Label(self.Frame, text= "Calculation of absorption spectrum:",bg= "grey",fg="black")
#         self.label_pol['font'] = myFont
#         self.label_pol.place(x=10,y=60)

#         self.Frame2_Button_1 = tk.Button(self.Frame,text="Create input",activebackground="#78d6ff",command=lambda:[self.createspec()])
#         self.Frame2_Button_1['font'] = myFont
#         self.Frame2_Button_1.place(x=290,y=60)

#         self.label_msg = Label(self.Frame, text= "",fg="black")
#         self.label_msg['font'] = myFont
#         self.label_msg.place(x=420,y=60)

#         self.Frame2_Run = tk.Button(self.Frame,text="Run Job", state= 'disabled',activebackground="#78d6ff",command=lambda:[self.event_generate('<<ShowJobSubmissionPage>>')])
#         self.Frame2_Run['font'] = myFont
#         self.Frame2_Run.place(x=320,y=380)
    
#         Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
#         Frame_Button1['font'] = myFont
#         Frame_Button1.place(x=10,y=380)

#         self.show_plot()

#     def show_plot(self):
#         check = self.controller.status.check_status('spectra', 2)
#         if check is True:
#             self.create_plot()  
#         else:
#             pass        
    
#     def create_plot(self):
#         myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
#         self.label_pol = Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
#         self.label_pol['font'] = myFont
#         self.label_pol.place(x=10,y=130)

#         ax_pol = ["x","y","z"]
#         self.entry_pol_x = ttk.Combobox(self.Frame, textvariable= self.axis, value = ax_pol, width= 15)
#         self.entry_pol_x['font'] = myFont
#         self.entry_pol_x.insert(0,"x")
#         self.entry_pol_x.place(x=160,y=130)
#         self.entry_pol_x['state'] = 'readonly'
        
#         self.Frame2_Plot = tk.Button(self.Frame,text="Plot",activebackground="#78d6ff",command=lambda:[plot_spectra(self.returnaxis(),str(self.controller.directory)+'/Spectrum/spec.dat',str(self.controller.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None)])
#         self.Frame2_Plot['font'] = myFont
#         self.Frame2_Plot.place(x=320,y= 130)
    
#     def returnaxis(self):
#         if self.axis.get() == "x":
#             axis = 1
#         if self.axis.get() == "y":
#             axis = 2
#         if self.axis.get() == "z":
#             axis = 3
#         return axis

#     def createspec(self):
#         spec_dict = {}
#         spec_dict['moment_file'] = pathlib.Path(self.controller.directory) / "TD_Delta" / "dm.dat"
        # spec_dict['spectrum_file'] = pathlib.Path(self.controller.directory) / "Spectrum"/ specfile
        # job = Spectrum(spec_dict,  engine.EngineGpaw(), str(self.controller.directory),'spec') 
        # job.write_input()
        # self.controller.task = job
        # self.controller.check = True
        # self.controller.status.update_status('spectra', 1)
        # show_message(self.label_msg, "Saved")
        # self.Frame2_Run.config(state='active')
      

class DmLdPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        from litesoph.utilities.units import au_to_fs
        self.plot_task = StringVar()
        self.compo = StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame = tk.Frame(self) 
        
        self.Frame.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.978)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
        
        self.heading = Label(self.Frame,text="LITESOPH Dipole Moment and laser Design", fg='blue')
        self.heading['font'] = myFont
        self.heading.place(x=350,y=10)
        
        self.label_pol = Label(self.Frame, text= "Plot:",bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=60)

        plot_list = ["Dipole Moment", "Dipole Moment and Laser"]
        self.entry_pol_x = ttk.Combobox(self.Frame,textvariable=self.plot_task, value = plot_list, width = 25)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"Dipole Moment")
        self.entry_pol_x.place(x=280,y=60)
        self.entry_pol_x['state'] = 'readonly'

        #self.label_pol = Label(self.Frame, text= "Axis of Electric polarization:",fg="black")
        #self.label_pol['font'] = myFont
        #self.label_pol.place(x=10,y=110)

        self.label_pol = Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=110)

        com_pol = ["x component","y component","z component"]
        self.entry_pol_x = ttk.Combobox(self.Frame, textvariable= self.compo, value = com_pol, width= 25)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"x component")
        self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_Button_1 = tk.Button(self.Frame,text="Plot",activebackground="#78d6ff", command=lambda:[self.plot_button()])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=250,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)
        
    def returnaxis(self):
        if self.compo.get() == "x component":
            axis = 2
        if self.compo.get() == "y component":
            axis = 3
        if self.compo.get() == "z component":
            axis = 4
        return axis

    def plot_button(self):
        from litesoph.utilities.units import au_to_fs
        if self.plot_task.get() == "Dipole Moment":
            plot_spectra(self.returnaxis(),str(self.controller.directory)+'/TD_Laser/dmlaser.dat',str(self.controller.directory)+'/TD_Laser/dmlaser.png',"Time (fs)","Dipole moment (au)", au_to_fs)
        if self.plot_task.get() == "Dipole Moment and Laser":
            plot_files(str(self.controller.directory)+'/laser.dat',str(self.controller.directory)+'/TD_Laser/dmlaser.dat',1, self.returnaxis())
   

def spectrum_show(directory,filename, suffix, axis, x, y):
        imgfile = "spec_{}_{}.png".format(suffix, axis)
        imgpath = str(directory) +"/" +imgfile
        filepath = str(directory)+"/"+filename
        plot_spectra(int(axis),filepath, imgpath, x, y)
        path = pathlib.Path(imgpath)
        img =Image.open(path)
        img.show()         

class TcmPage(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #self.controller = controller
        self.parent = parent
        self.job = None

        self.min = tk.DoubleVar()
        self.max = tk.DoubleVar()
        self.step = tk.DoubleVar()
        self.freq = tk.DoubleVar()
        self.frequency = tk.StringVar()

        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.Frame1 = tk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button = tk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button.grid(row=2, column=0, sticky='nsew')
        self.Frame1.grid(row=1,column=0, sticky='nsew')

        self.grid_rowconfigure(1, weight=5)
        self.grid_rowconfigure(2, weight=1)

        self.heading = tk.Label(self,text="LITESOPH Kohn Sham Decomposition", fg='blue')
        self.heading['font'] = myfont()
        self.heading.grid(row=0, column=0)
        
        self.FrameTcm2_label_path = tk.Label(self.Frame1,text="Frequency space density matrix",fg="blue")
        self.FrameTcm2_label_path['font'] = myfont()
        self.FrameTcm2_label_path.grid(row=0, column=0)

        self.Label_freqs = tk.Label(self.Frame1,text="List of the Frequencies obtained from the photoabsorption \nspectrum (in eV) at which Fourier transform of density matrix is sought.\n(Entries should be separated by space,eg: 2.1  4)",fg="black", justify='left')
        self.Label_freqs['font'] = myfont()
        self.Label_freqs.grid(row=1, column=0)        
        
        self.entry_freq = tk.Entry(self.Frame1, textvariable= self.frequency, width=30)
        self.entry_freq['font'] = myfont()
        # self.tin.set(0)
        self.entry_freq.grid(row=2, column=0, columnspan=3)

        # self.TextBox_freqs = tk.Entry(self.Frame1)
        # self.TextBox_freqs['font'] = myfont()
        # self.TextBox_freqs.grid(row=2, column=0, columnspan=3)

        #self.Label_freqs = Label(self.Frame,text="Or provide a range as <min value>-<max value>-<step size> respectively",fg="black")
        #self.Label_freqs['font'] = myFont
        #self.Label_freqs.place(x=10,y=240)
 
        #self.Tcm_entry_ns = Entry(self.Frame, textvariable=self.min)
        #self.Tcm_entry_ns['font'] = myFont
        #self.Tcm_entry_ns.place(x=10,y=280)
       
        #self.Tcm_entry_ns = Entry(self.Frame, textvariable= self.max)
        #self.Tcm_entry_ns['font'] = myFont
        #self.Tcm_entry_ns.place(x=200,y=280)
      
        #self.Tcm_entry_ns = Entry(self.Frame, textvariable=self.step, width= 10)
        #self.Tcm_entry_ns['font'] = myFont
        #self.Tcm_entry_ns.place(x=390,y=280)

        Frame_Button1 = tk.Button(self.frame_button, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myfont()
        Frame_Button1.grid(row=0, column=0)

        # self.buttonRetrieve = Button(self.Frame1, text="Retrieve Freq",activebackground="#78d6ff",command=lambda:[self.retrieve_input(),self.freq_listbox(), self.tcm_button()])
        # #self.buttonRetrieve = tk.Button(self.Frame1, text="Create input",activebackground="#78d6ff",command=lambda:self.create_tcm())
        # self.buttonRetrieve['font'] = myfont()
        # self.buttonRetrieve.grid(row=3, column=0)        

        #self.create_button = Button(self.Frame1, text="Retrieve Freq",activebackground="#78d6ff",command=lambda:[self.retrieve_input(),self.freq_listbox(), self.tcm_button()])
        self.create_button = tk.Button(self.Frame1, text="Create input",activebackground="#78d6ff",command=lambda:self.event_generate('<<CreateTCMScript>>'))
        self.create_button['font'] = myfont()
        self.create_button.grid(row=2, column=1)

        # self.Frame_run = tk.Button(self.Frame1,text="Run Job", state= 'disabled',activebackground="#78d6ff", command=lambda:[self.event_generate('<<ShowJobSubmissionPage>>')])
        # self.Frame_run['font'] = myfont()
        # self.Frame_run.grid(row=3, column=2)

        self.add_job_frame("TCM")

    def add_job_frame(self, task_name):  
        """  Adds submit job buttons"""

        self.Frame3 = tk.Frame(self, borderwidth=2, relief='groove')
        self.Frame3.grid(row=1, column=1, sticky='nswe')
        # View_Button1 = tk.Button(self.Frame3, text="View Output", activebackground="#78d6ff", command=lambda: [self.view_button()])
        # View_Button1['font'] = self.myFont
        # View_Button1.grid(row=2, column=1, sticky='nsew')

        self.Frame1_Button2 = tk.Button(self.Frame3, text="Submit Local", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubLocal'+task_name+'>>'))
        self.Frame1_Button2['font'] =myfont()
        self.Frame1_Button2.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
        
        self.Frame1_Button3 = tk.Button(self.Frame3, text="Submit Network", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubNetwork'+task_name+'>>'))
        self.Frame1_Button3['font'] = myfont()
        self.Frame1_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')    

        self.plot_button = tk.Button(self.Frame3, text="Plot", activebackground="#78d6ff", command=lambda: self.event_generate("<<ShowTCMPlot>>"))
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=3, column=2,padx=3, pady=15, sticky='nsew')

    def set_sub_button_state(self,state):
        self.Frame1_Button2.config(state=state)
        self.Frame1_Button3.config(state=state)

    def retrieve_input(self):
        inputValues = self.frequency.get()  #TextBox_freqs.get("1.0", "end-1c")
        freqs = inputValues.split()

        self.freq_list = []
        for freq in freqs[0:]:
            self.freq_list.append(float(freq))
        return(self.freq_list)   
    
    def get_parameters(self):
        self.retrieve_input()
        #gs = pathlib.Path(self.controller.directory) / "GS" / "gs.gpw"
        #f = pathlib.Path(self.controller.directory) / "TD_Delta" / "wf.ulm"
        tcm_dict = {
                'frequency_list' : self.freq_list,
                 }     
        return tcm_dict    
        # self.job = TCM(tcm_dict, engine.EngineGpaw(), self.controller.directory,  'tcm')
        # self.job.write_input()
        # self.controller.task = self.job 
        # self.controller.check = False
        # self.Frame_run.config(state= 'active')      

    def freq_listbox(self):
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.plot_label= Label(self.Frame,text="Select the frequency and Plot",fg="black", bg="gray")
        self.plot_label['font'] = myFont
        self.plot_label.place(x=560,y=70)

        self.listbox = Listbox(self, font=myFont)
        self.listbox.place(x = 580, y=100)        
        for item in self.freq_list:
            self.listbox.insert(END, item)
        self.plot_button = tk.Button(self.Frame, text="Plot",activebackground="#78d6ff",command=lambda:self.freq_plot())
        self.plot_button['font'] = myFont
        self.plot_button.place(x=740,y=200)   

    def freq_plot(self):
        for i in self.listbox.curselection():
            self.tcm.plot(self.tcm_dict, i)        
#--------------------------------------------------------------------------------        


if __name__ == '__main__':
   
    
    app = GUIAPP()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
