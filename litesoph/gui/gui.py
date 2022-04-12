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
from litesoph.utilities.plot_spectrum import plot_spectrum 
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
            '<<ShowDmLdPage>>' : lambda _: self._show_frame(v.DmLdPage, self),
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
            detail ="Command used to call visualization program '{}'. supply the appropriate command in ~/.litesoph/lsconfig.ini".format(cmd.split()[0])
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
            messagebox.showerror(title = 'Error', message="Input not saved. Please save the input before job submission")
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
            self.spectra_view.Frame1_Button2.config(state='active')
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
            try:
                nwchem_compute_spec(self.directory, pol[1])
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
            self.job_sub_page.bind('<<ShowSpectrumPlot>>', lambda _:plot_spectra(1,str(self.directory)+'/Spectrum/spec.dat',str(self.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None))
            self.job_sub_page.bind('<<RunSpectrumNetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<ViewSpectrumNetworkOutfile>>', lambda _: self._on_out_remote_view_button(self.rt_tddft_delta_task))
            self.job_sub_page.text_view.bind('<<SaveSpectrumNetwork>>',lambda _: self._on_save_remote_job_script(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<CreateSpectrumRemoteScript>>', lambda _: self._on_create_remote_job_script(self.rt_tddft_delta_task,'RT_TDDFT_DELTANetwork'))

    def _on_spectra_plot_button(self, *_):
        """ Selects engine specific plot function"""
        
        pol =  self.status.get_status('rt_tddft_delta.param.pol_dir')
        

        if self.engine == "gpaw":
            spec_file = self.spectra_task.engine.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            img = file.parent / f"spec_{pol[1]}.png"
            plot_spectrum(file,img,0, pol[0]+1, "Energy (in eV)", "Strength(in /eV)")

        elif self.engine == "octopus":
            spec_file = self.spectra_task.engine.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            img = file.parent / f"spec_{pol[1]}.png"
            plot_spectrum(file,img,0, 4, "Energy (in eV)", "Strength(in /eV)")

        elif self.engine == "nwchem":
            spec_file = EngineNwchem.spectrum['spectra_file'][pol[0]]
            file = pathlib.Path(self.directory) / spec_file
            img = file.parent / f"spec_{pol[1]}.png"
            plot_spectrum(file,img,0, 2, "Energy","Strength")
    
        
##----------------------compute---tcm---------------------------------

    def _on_tcm_task(self, *_):

        if self.engine != 'gpaw':
            messagebox.showinfo(title='Info', message='Curretly this option is only implemented for Gpaw. ')
            return
        self._show_frame(v.TcmPage, self._window)
        self.tcm_view = self._frames[v.TcmPage]
        
        self.tcm_task = Task(self.status, self.directory, self.lsconfig)
        self.bind('<<CreateTCMScript>>', self._on_create_tcm_button)
        self.bind('<<SubLocalTCM>>', lambda _: self._on_tcm_run_local_button())
        self.bind('<<RunNetworkTCM>>', lambda _: self._on_tcm_run_network_button())
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
            img_file = pathlib.Path(self.directory) / 'gpaw' / 'TCM' / f'tcm_{item:.2f}.png'
            
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

#--------------------------------------------------------------------------------        


if __name__ == '__main__':
   
    
    app = GUIAPP()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
