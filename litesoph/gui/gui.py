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
import pathlib 
import shutil
from configparser import ConfigParser

from matplotlib.pyplot import show

#---LITESOPH modules
from litesoph import check_config
from litesoph.gui.menubar import MainMenu
from litesoph.gui import models as m
from litesoph.gui import views as v 
from litesoph.gui.spec_plot import plot_spectra, plot_files
from litesoph.simulations.esmd import Task,TCM, Spectrum
from litesoph.simulations import engine
from litesoph.gui.filehandler import Status, file_check, show_message
from litesoph.gui.navigation import Nav
from litesoph.gui.filehandler import Status
from litesoph.simulations.choose_engine import choose_engine
from litesoph.simulations.gpaw.gpaw_template import write_laser
from litesoph.utilities.job_submit import SubmitLocal


home = pathlib.Path.home()

TITLE_FONT = ("Helvetica", 18, "bold")

class AITG(tk.Tk):

    def __init__(self, lsconfig: ConfigParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings_model = m.SettingsModel
        self.mainmenu = MainMenu(self)
        self.lsconfig = lsconfig
        self.lsroot = check_config(self.lsconfig, "lsroot")
        self.directory = pathlib.Path(self.lsconfig.get("project_path", "lsproject", fallback=str(home)))
    
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=6)
       
        self.nav = None
        self.refresh_nav(self.directory)
        
        self.check = None
        self._window = Frame(self)
        self._window.grid(row=0, column=1)
        
        self._window.grid_rowconfigure(700,weight=700)
        self._window.grid_columnconfigure(800,weight=400)  

        self.engine = None
        self.status_bar = tk.StringVar()
        ttk.Label(self, textvariable=self.status_bar).grid(sticky=(tk.W + tk.E), row=2, padx=10)
        self.ground_state_view = None
        self.ground_state_task = None
        
        self._frames = OrderedDict()
        
        self._show_page_events()
        self._bind_event_callbacks()
        self._show_frame(v.StartPage, self.lsroot)
    
    
    def _status_init(self):
        """Initializes the status object."""
        self.status = Status(self.directory)

    def _get_engine(self):
        self.engine = self.status.get_status('engine')
        self.status_bar.set(self.engine)
    
    def _show_frame(self, frame,*args, **kwargs):
        
        if frame in self._frames.keys():
            frame_obj = self._frames[frame]
            self._frames.move_to_end(frame, last=False)
            frame_obj.tkraise()
        else:
            int_frame = frame(self._window, *args, **kwargs)
            self._frames[frame]= int_frame
            self._frames.move_to_end(frame, last=False)
            int_frame.grid(row=0, column=1, sticky ="nsew")
            int_frame.tkraise()


    def refresh_nav(self, path):

        if isinstance(self.nav, Nav):
            self.nav.destroy()
            self.nav = Nav(self, path)
            self.nav.grid(row=0, column=0, sticky='nw')
        else:
            self.nav = Nav(self, path)
            self.nav.grid(row=0, column=0, sticky='nw')

    def _bind_event_callbacks(self):
        """binds events and specific callback functions"""
        event_callbacks = {
            '<<GetMolecule>>' : self._on_get_geometry_file,
            '<<VisualizeMolecule>>': self._on_visualize,
            '<<CreateNewProject>>' : self._on_create_project,
            '<<OpenExistingProject>>' : self._on_open_project,
            '<<SelectTask>>' : self._on_task_select,
            '<<ClickBackButton>>' : self._on_back_button,
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
            #'<<ShowJobSubmissionPage>>' : lambda _: self._show_frame(v.JobSubPage, self),
            '<<ShowGroundStatePage>>' : self. _on_ground_state_task,
            '<<ShowTimeDependentPage>>' : self._on_rt_tddft_delta_task,
            '<<ShowLaserDesignPage>>' : self._on_rt_tddft_laser_task,
            '<<ShowPlotSpectraPage>>' : lambda _: self._show_frame(PlotSpectraPage, self),
            '<<ShowDmLdPage>>' : lambda _: self._show_frame(DmLdPage, self),
            '<<ShowTcmPage>>' : lambda _: self._show_frame(TcmPage, self)
        }
        for event, callback in event_show_page.items():
            self.bind(event, callback)  

    def _on_back_button(self, *_):
        "generates a event to show the first frame in odered_dict"
        frame = list(self._frames)[1]
        self._show_frame(frame)
        # frame = frame.__name__
        # frame = '<<'+'Show'+frame+'>>'
        # self.event_generate(f'{frame}')

    def _change_directory(self, path):
        "changes current working directory"
        self.directory = pathlib.Path(path)
        os.chdir(self.directory) 

    def _on_open_project(self, event):
        """creates dialog to get porject path and opens existing project"""
        print(event)
        project_name = filedialog.askdirectory(title= "Select the existing Litesoph Project")
        self._change_directory(project_name)
        self.refresh_nav(self.directory)
        self._status_init()
        self._get_engine()
        
    def _on_create_project(self, *_):
        """Creates a new litesoph project"""
        create_dir = None
        project_path = self._frames[v.WorkManagerPage].get_project_path()
        
        dir_exists = m.WorkManagerModel.check_dir_exists(project_path)

        if dir_exists:
            create_dir = messagebox.askokcancel('directory exists', f"The directory {project_path} already exists \n do you want to open the project?")
        
            if create_dir:
                self._change_directory(project_path)
                self.refresh_nav(self.directory)
                self._status_init()
            return
        
        try:
            m.WorkManagerModel.create_dir(project_path)
        except PermissionError as e:
            messagebox.showerror(e)
        except FileExistsError as e:
            messagebox.showerror(e)
        else:
            messagebox.showinfo("Message", f"project:{project_path} is created successfully")
            self._frames[v.WorkManagerPage].update_project_entry(project_path)
            self._change_directory(project_path)
            self.refresh_nav(self.directory)
            self._status_init()
        
    def _on_get_geometry_file(self, *_):
        """creates dialog to get geometry file and copies the file to project directory as coordinate.xyz"""
        self.geometry_file = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=[(" Text Files", "*.xyz")])
        proj_path = pathlib.Path(self.directory) / "coordinate.xyz"
        shutil.copy(self.geometry_file, proj_path)
        
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
        
        sub_task = self._frames[v.WorkManagerPage].sub_task.get()

        if sub_task  == "Ground State":
            path = pathlib.Path(self.directory) / "coordinate.xyz"
            if path.exists() is True:
                self.event_generate('<<ShowGroundStatePage>>')
            else:
                messagebox.showerror(message= "Upload geometry file")
        elif sub_task == "Delta Kick":
            self.event_generate('<<ShowTimeDependentPage>>')   
        elif sub_task == "Gaussian Pulse":    
            self.event_generate('<<ShowLaserDesignPage>')   
        elif sub_task == "Spectrum":
            self.event_generate('<<ShowPlotSpectraPage>>')   
        elif sub_task == "Dipole Moment and Laser Pulse":
            self.event_generate('<<ShowDmLdPage>>')
        elif sub_task.get() == "Kohn Sham Decomposition":
               self.event_generate('<<ShowTcmPage>>')    

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

##----------------------Ground_State_task---------------------------------

    def _on_ground_state_task(self, *_):
        self._show_frame(v.GroundStatePage, self)
        self.ground_state_view = self._frames[v.GroundStatePage]
        self.ground_state_task = Task(self.status, self.directory)

        self.bind('<<SaveGroundStateScript>>', lambda _ : self._on_gs_save_button())
        self.bind('<<ViewGroundStateScript>>', lambda _ : self._on_gs_view_button())
        self.bind('<<SubGroundState>>',  self._on_gs_run_job_button)

    def _on_gs_save_button(self, *_):
        self._validate_gs_input()
        self._gs_create_input()

    def _on_gs_view_button(self, *_):
        template = self._validate_gs_input()
        text_veiw = self._init_text_veiwer('GroundState', template)
        text_veiw.bind('<<SaveGroundState>>', lambda _: self._gs_create_input(text_veiw.save_txt))
        text_veiw.bind('<<ViewGroundStatePage>>', lambda _: self._show_frame(v.GroundStatePage, self))


    def _validate_gs_input(self):
        inp_dict = self.ground_state_view.get_parameters()
        engine = inp_dict['engine']
        if self.engine:
            if self.engine != engine:
                messagebox.showerror(message = f'This project {self.directory.name} was started with {self.engine} engine. \n If you want to do use different engine. Please create new project with that engine')
        #filename = m.GroundStateModel.filename
        self.ground_state_task.set_engine(engine)
        self.ground_state_task.set_task('ground_state', inp_dict)
        self.ground_state_task.create_template()
        self.engine = engine
        return self.ground_state_task.template

    def _gs_create_input(self, template=None):     
        confirm_engine = messagebox.askokcancel(message= "You have chosen {} engine. Rest of the calculations will use this engine.".format(self.engine))
        if confirm_engine is True:
            self.ground_state_task.write_input(template)
            self.status.update_status('engine', self.engine)
            self.status.update_status(f'{self.engine}.ground_state.inp', 1)
            self.status.update_status(f'{self.engine}.ground_state.inp',self.ground_state_task.user_input)
            self.status_bar.set(self.engine)
            self.ground_state_view.set_label_msg('saved')
        else:
            pass  
        self.check = False

    def _on_gs_run_job_button(self, *_):
        try:
            getattr(self.ground_state_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'GroundState')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")

            self.job_sub_page.bind('<<RunGroundStateLocal>>', lambda _: self._run_local(self.ground_state_task))
            self.job_sub_page.bind('<<RunGroundStateNetwork>>', lambda _: self._run_network(self.ground_state_task))

##----------------------Time_dependent_task_delta---------------------------------

    def _on_rt_tddft_delta_task(self, *_):
        self._show_frame(v.TimeDependentPage, self, self.engine)
        self.rt_tddft_delta_view = self._frames[v.TimeDependentPage]
        self.rt_tddft_delta_task = Task(self.status, self.directory)

        self.bind('<<SaveRT_TDDFT_DELTAScript>>', lambda _ : self._on_td_save_button())
        self.bind('<<ViewRT_TDDFT_DELTAScript>>', lambda _ : self._on_td_view_button())
        self.bind('<<SubRT_TDDFT_DELTA>>',  self._on_td_run_job_button)

    def _on_td_save_button(self, *_):
        self._validate_td_input()
        self._td_create_input()

    def _on_td_view_button(self, *_):
        template = self._validate_td_input()
        text_veiw = self._init_text_veiwer('RT_TDDFT_DELTA', template)
        text_veiw.bind('<<SaveRT_TDDFT_DELTA>>', lambda _: self._td_create_input(text_veiw.save_txt))
        text_veiw.bind('<<ViewRT_TDDFT_DELTAPage>>', lambda _: self._show_frame(v.TimeDependentPage))

    def _validate_td_input(self):
        inp_dict = self.rt_tddft_delta_view.get_parameters()
        self.rt_tddft_delta_task.set_engine(self.engine)
        self.rt_tddft_delta_task.set_task('rt_tddft_delta', inp_dict)
        self.rt_tddft_delta_task.create_template()
        return self.rt_tddft_delta_task.template

    def _td_create_input(self, template=None):     
        self.rt_tddft_delta_task.write_input(template)
        self.rt_tddft_delta_view.set_label_msg('saved')
        self.check = False

    def _on_td_run_job_button(self, *_):
        try:
            getattr(self.rt_tddft_delta_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'RT_TDDFT_DELTA')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")

            self.job_sub_page.bind('<<RunRT_TDDFT_DELTALocal>>', lambda _: self._run_local(self.rt_tddft_delta_task))
            self.job_sub_page.bind('<<RunRT_TDDFT_DELTANetwork>>', lambda _: self._run_network(self.rt_tddft_delta_task))

##----------------------Time_dependent_task_laser---------------------------------

    def _on_rt_tddft_laser_task(self, *_):
        self._show_frame(v.LaserDesignPage, self, self.engine)
        self.rt_tddft_laser_view = self._frames[v.LaserDesignPage]
        self.rt_tddft_laser_task = Task(self.status, self.directory)

        self.bind('<<SaveRT_TDDFT_LASERScript>>', lambda _ : self._on_td_laser_save_button())
        self.bind('<<ViewRT_TDDFT_LASERScript>>', lambda _ : self._on_td_laser_view_button())
        self.bind('<<SubRT_TDDFT_LASER>>',  self._on_td_laser_run_job_button)

    def laser_button(self):
        dir = pathlib.Path(self.directory)/ "TD_Laser"
        write_laser(self.laser_pulse(), 'laser', self.directory )
        self.plot_canvas(str(self.directory)+"/laser.dat", 1, 'time(in fs)','Laser strength(in au)')
        
    def _on_td_laser_save_button(self, *_):
        self._validate_td_laser_input()
        self._td_create_input()

    def _on_td_laser_view_button(self, *_):
        template = self._validate_td_laser_input()
        text_veiw = self._init_text_veiwer('RT_TDDFT_LASER', template)
        text_veiw.bind('<<SaveRT_TDDFT_LASER>>', lambda _: self._td_laser_create_input(text_veiw.save_txt))
        text_veiw.bind('<<ViewRT_TDDFT_LASERPage>>', lambda _: self._show_frame(v.LaserDesignPage))

    def _validate_td_laser_input(self):
        inp_dict = self.rt_tddft_laser_view.get_parameters()
        self.rt_tddft_laser_task.set_engine(self.engine)
        self.rt_tddft_laser_task.set_task('rt_tddft_laser', inp_dict)
        self.rt_tddft_laser_task.create_template()
        return self.rt_tddft_laser_task.template

    def _td_laser_create_input(self, template=None):     
        self.rt_tddft_laser_task.write_input(template)
        self.rt_tddft_laser_view.set_label_msg('saved')
        self.check = False

    def _on_td_laser_run_job_button(self, *_):
        try:
            getattr(self.rt_tddft_laser_task.engine,'directory')           
        except AttributeError:
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
        else:
            self.job_sub_page = v.JobSubPage(self._window, 'RT_TDDFT')
            self.job_sub_page.grid(row=0, column=1, sticky ="nsew")

            self.job_sub_page.bind('<<RunRT_TDDFT_LASERLocal>>', lambda _: self._run_local(self.rt_tddft_laser_task))
            self.job_sub_page.bind('<<RunRT_TDDFT_LASERNetwork>>', lambda _: self._run_network(self.rt_tddft_laser_task))

##----------------------Time_dependent_task---------------------------------

    def _init_text_veiwer(self,name, template, *_):
        #self._show_frame(v.TextViewerPage, self)
        text_veiw = v.TextViewerPage(self._window)
        text_veiw.grid(row=0, column=1, sticky ="nsew")
        text_veiw.set_task_name(name)
        text_veiw.insert_text(template)
        return text_veiw

    def _run_local(self, task):
        np = self.job_sub_page.get_processors()
        submitlocal = SubmitLocal(task.engine, self.lsconfig, np)
        task.run(submitlocal)
        
    def _run_network(self, task):
        run_script_path = self.job_sub_page.run_script_path

        if not run_script_path:
            messagebox.showerror(message = "Please upload job script")
        login_dict = self.job_sub_page.get_network_dict()
        net_inp = dict(run_script = run_script_path,
                        inp = [task.file_path],
                        geometry = str(pathlib.Path(self.directory) / "coordinate.xyz"))

        from litesoph.utilities.job_submit import SubmitNetwork

        submit_network = SubmitNetwork(engine, 
                                        self.lsconfig,
                                        hostname=login_dict['ip'],
                                        username=login_dict['username'],
                                        password=login_dict['password'],
                                        remote_path=login_dict['remote_path'],
                                        upload_files=net_inp)

        submit_network.run_job()

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

# class LaserDesignPage(Frame):

#     def __init__(self, parent, controller, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.controller = controller
        
#         self.job = None
#         self.tdpulse_dict = {}
#         myFont = font.Font(family='Helvetica', size=10, weight='bold')

#         j=font.Font(family ='Courier', size=20,weight='bold')
#         k=font.Font(family ='Courier', size=40,weight='bold')
#         l=font.Font(family ='Courier', size=15,weight='bold')
        
#         self.Frame1 = tk.Frame(self)
#         #self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
#         self.Frame1.configure(relief='groove')
#         self.Frame1.configure(borderwidth="2")
#         self.Frame1.configure(relief="groove")
#         self.Frame1.configure(cursor="fleur")
#         self.Frame1 = tk.Frame(self)
        
#         self.strength = StringVar()
#         self.inval = DoubleVar()
#         self.pol_x = StringVar()
#         self.pol_y = StringVar()
#         self.pol_z = StringVar()
#         self.fwhm = StringVar()
#         self.freq = StringVar()
#         self.ts = StringVar()
#         self.ns = StringVar()
#         self.tin = StringVar()

#         self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
#         self.Frame1.configure(relief='groove')
#         self.Frame1.configure(borderwidth="2")
#         self.Frame1.configure(relief="groove")
#         self.Frame1.configure(cursor="fleur")
        
#         self.Frame1_label_path = Label(self.Frame1,text="LITESOPH Input for Laser Design", fg='blue')
#         self.Frame1_label_path['font'] = myFont
#         self.Frame1_label_path.place(x=125,y=10)

#         self.label_proj = Label(self.Frame1,text="Time Origin (tin)",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=60)

#         self.entry_proj = Entry(self.Frame1,textvariable= self.tin)
#         self.entry_proj['font'] = myFont
#         self.entry_proj.insert(0,"0")
#         self.entry_proj.place(x=280,y=60)
        
#         self.label_inval = Label(self.Frame1,text="-log((E at tin)/Eo),(value>=6)",bg="gray",fg="black")
#         self.label_inval['font'] = myFont
#         self.label_inval.place(x=10,y=100)
 
#         # inval_list = ["1e-8", "1e-9"]
#         # self.entry_pol_z = ttk.Combobox(self.Frame1,textvariable= self.inval, value = inval_list)
#         # self.entry_pol_z['font'] = myFont
#         # self.entry_pol_z.insert(0,"1e-8")
#         self.entry_inval = Entry(self.Frame1,textvariable= self.inval)
#         self.entry_inval['font'] = myFont
#         self.inval.set(6)
#         self.entry_inval.place(x=280,y=100)

#         self.label_proj = Label(self.Frame1,text="Laser Strength in a.u (Eo)",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=140)
    
#         instr = ["1e-5","1e-3"]
#         self.entry_proj = ttk.Combobox(self.Frame1,textvariable= self.strength, value = instr)
#         self.entry_proj['font'] = myFont
#         self.entry_proj.current(0)
#         self.entry_proj.place(x=280,y=140)
#         self.entry_proj['state'] = 'readonly'

#         self.label_proj = Label(self.Frame1,text="Full Width Half Max (FWHM in eV)",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=180)

#         self.entry_proj = Entry(self.Frame1,textvariable= self.fwhm)
#         self.fwhm.set("0.2")
#         self.entry_proj['font'] = myFont
#         self.entry_proj.place(x=280,y=180)

#         self.label_proj = Label(self.Frame1,text="Frequency in eV",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=220)

#         self.entry_proj = Entry(self.Frame1,textvariable= self.freq)
#         self.entry_proj['font'] = myFont
#         self.entry_proj.place(x=280,y=220)

#         self.label_proj = Label(self.Frame1,text="Time step in attosecond ",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=260)

#         self.entry_proj = Entry(self.Frame1,textvariable= self.ts)
#         self.entry_proj['font'] = myFont
#         self.entry_proj.insert(0,"10")
#         self.entry_proj.place(x=280,y=260)
        
#         self.label_proj = Label(self.Frame1,text="Number of Steps",bg="gray",fg="black")
#         self.label_proj['font'] = myFont
#         self.label_proj.place(x=10,y=300)

#         self.entry_proj = Entry(self.Frame1,textvariable= self.ns)
#         self.entry_proj['font'] = myFont
#         self.entry_proj.insert(0,"2000")
#         self.entry_proj.place(x=280,y=300)
 
#         Frame1_Button1 = tk.Button(self.Frame1, text="Back",activebackground="#78d6ff",command=lambda:self.back_button())
#         Frame1_Button1['font'] = myFont
#         Frame1_Button1.place(x=10,y=380)
        
#         self.button_project = Button(self.Frame1,text="Next",activebackground="#78d6ff",command=lambda:[self.choose_laser()])
#         self.button_project['font'] = myFont
#         self.button_project.place(x=350,y=380)

#         self.button_project = Button(self.Frame1,text="Laser Design",activebackground="#78d6ff",command=lambda:[self.laser_button()])
#         self.button_project['font'] = myFont
#         self.button_project.place(x=170,y=380)

#         self.Frame2 = tk.Frame(self)
#         self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

#         self.Frame2.configure(relief='groove')
#         self.Frame2.configure(borderwidth="2")
#         self.Frame2.configure(relief="groove")
#         self.Frame2.configure(cursor="fleur")

#         self.label_pol_x = Label(self.Frame2, text="Electric Polarisation in x axis", bg= "grey",fg="black")
#         self.label_pol_x['font'] = myFont
#         self.label_pol_x.place(x=10,y=60)
        
#         pol_list = ["0","1"]
#         self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.pol_x, value = pol_list)
#         self.entry_pol_x['font'] = myFont
#         self.entry_pol_x.insert(0,"0")
#         self.entry_pol_x.place(x=280,y=60)
#         self.entry_pol_x['state'] = 'readonly'

#         self.label_pol_y = Label(self.Frame2, text="Electric Polarisation in y axis", bg= "grey",fg="black")
#         self.label_pol_y['font'] = myFont
#         self.label_pol_y.place(x=10,y=110)
    
#         self.entry_pol_y = ttk.Combobox(self.Frame2,textvariable= self.pol_y, value = pol_list)
#         self.entry_pol_y['font'] = myFont
#         self.entry_pol_y.insert(0,"0")
#         self.entry_pol_y.place(x=280,y=110)
#         self.entry_pol_y['state'] = 'readonly'

#         self.label_pol_z = Label(self.Frame2, text="Electric Polarisation in z axis", bg= "grey",fg="black")
#         self.label_pol_z['font'] = myFont
#         self.label_pol_z.place(x=10,y=160)
 
#         self.entry_pol_z = ttk.Combobox(self.Frame2,textvariable= self.pol_z, value = pol_list)
#         self.entry_pol_z['font'] = myFont
#         self.entry_pol_z.insert(0,"0")
#         self.entry_pol_z.place(x=280,y=160) 
#         self.entry_pol_z['state'] = 'readonly'

#         self.Frame2_Button1 = tk.Button(self.Frame2, state='disabled', text="Save Input",activebackground="#78d6ff", command=lambda:[self.save_button()])
#         self.Frame2_Button1['font'] = myFont
#         self.Frame2_Button1.place(x=10,y=380)

#         self.label_msg = Label(self.Frame2,text="")
#         self.label_msg['font'] = myFont
#         self.label_msg.place(x=10,y=350)
 
#         self.Frame2_Button2 = tk.Button(self.Frame2, state='disabled', text="View Input",activebackground="#78d6ff", command=lambda:[self.view_button()])
#         self.Frame2_Button2['font'] = myFont
#         self.Frame2_Button2.place(x=170,y=380)
        
#         self.Frame2_Button3 = tk.Button(self.Frame2, state='disabled', text="Run Job",activebackground="#78d6ff",command=lambda:self.run_job_button())
#         self.Frame2_Button3['font'] = myFont
#         self.Frame2_Button3.place(x=350,y=380)
#         self.Frame3 = None
#         self.button_refresh()

#     def view_button(self):
#         self.tdpulse_inp2dict('td_pulse')
#         self.controller._show_frame(TextViewerPage, LaserDesignPage, None, task=self.job)

#     def create_frame3(self):
#         self.Frame3 = tk.Frame(self)
#         self.Frame3.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

#         self.Frame3.configure(relief='groove')
#         self.Frame3.configure(borderwidth="2")
#         self.Frame3.configure(relief="groove")
#         self.Frame3.configure(cursor="fleur")
    
#     def laser_button(self):
#         dir = pathlib.Path(self.controller.directory)/ "TD_Laser"
#         write_laser(self.laser_pulse(), 'laser', self.controller.directory )
#         self.plot_canvas(str(self.controller.directory)+"/laser.dat", 1, 'time(in fs)','Laser strength(in au)')
       

#     def plot_canvas(self,filename, axis, x,y):
#         from litesoph.utilities.units import au_to_fs
#         import numpy as np
#         from matplotlib.figure import Figure
#         from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
#         figure = Figure(figsize=(5, 3), dpi=100)
#         data_ej = np.loadtxt(filename) 
#         #plt.figure(figsize=(5, 3), dpi=100)

#         if self.Frame3 is not None:
#             self.Frame3.destroy()
            
#         self.create_frame3()
#         self.ax = figure.add_subplot(1, 1, 1)
#         self.ax.plot(data_ej[:, 0]*au_to_fs, data_ej[:, axis], 'k')
#         self.ax.spines['right'].set_visible(False)
#         self.ax.spines['top'].set_visible(False)
#         self.ax.yaxis.set_ticks_position('left')
#         self.ax.xaxis.set_ticks_position('bottom')
#         self.ax.set_xlabel(x)
#         self.ax.set_ylabel(y)

#         self.Frame3.canvas = FigureCanvasTkAgg(figure, master=self.Frame3)
#         self.Frame3.canvas.draw()
#         self.Frame3.canvas.get_tk_widget().pack(side =LEFT,fill='both', expand=True)
#         self.Frame3.toolbar = NavigationToolbar2Tk(self.Frame3.canvas, self.Frame3)
#         self.Frame3.toolbar.update()
#         self.Frame3.canvas._tkcanvas.pack(side= tk.TOP,fill ='both')
#         #plt.savefig('pulse.png')

#     def button_refresh(self):
#         self.st_var = self.controller.status 
#         if self.st_var.check_status('td_inp', 2):
#             self.Frame2.tkraise() 
#             self.Frame2_Button1.config(state='active') 
#             self.Frame2_Button2.config(state='active') 
#             self.Frame2_Button3.config(state='active') 
               

#     def choose_laser(self):
#         check = messagebox.askyesno(message= "Do you want to proceed with this laser set up?")
#         if check is True:
#             self.Frame2.tkraise()
#             self.Frame2_Button1.config(state='active') 
#             self.Frame2_Button2.config(state='active') 
#             self.Frame2_Button3.config(state='active') 
#         else:
#             messagebox.showinfo(message="Please enter the laser design inputs.") 
#             self.controller._show_frame(LaserDesignPage)

#     def laser_pulse(self):
#         l_dict = self.laser_calc()
#         l_dict['frequency'] = self.freq.get()
#         l_dict['time0'] ="{}e3".format(l_dict['time0'])
#         range = int(self.ns.get())* float(self.ts.get())
#         l_dict['range'] = range
#         l_dict['sincos'] = 'sin'
#         return(l_dict)              
      
#     def laser_calc(self):
#         from litesoph.pre_processing.laser_design import laser_design
#         l_dict = laser_design(self.strength.get(), self.inval.get(),self.tin.get(),self.fwhm.get())
#         return(l_dict)

#     def tdpulse_inp2dict(self):
#         self.td = self.tdpulse_dict
#         self.dir = self.controller.directory
#         abs_x = float(self.strength.get())*float(self.pol_x.get())
#         abs_y = float(self.strength.get())*float(self.pol_y.get())
#         abs_z = float(self.strength.get())*float(self.pol_z.get())
#         abs_list = [abs_x, abs_y, abs_z]
#         inp_list = [float(self.ts.get()),int(self.ns.get())]
#         epol_list = [float(self.pol_x.get()),float(self.pol_y.get()),float(self.pol_z.get())]
#         laser_dict = self.laser_calc()
#         updatekey(laser_dict, 'frequency', self.freq.get())
#         updatekey(self.td,'absorption_kick',abs_list)
#         updatekey(self.td,'propagate', tuple(inp_list))
#         updatekey(self.td,'electric_pol',epol_list)
#         updatekey(self.td,'dipole_file','dmlaser.dat')
#         updatekey(self.td,'filename', str(self.dir)+'/GS/gs.gpw')
#         updatekey(self.td,'td_potential', True)
#         updatekey(self.td,'txt', 'tdlaser.out')
#         updatekey(self.td,'td_out', 'tdlaser.gpw')
#         updatekey(self.td,'laser', laser_dict)

#         return(self.td)       

#     def init_task(self, td_dict: dict, filename):
#         self.job =RT_LCAO_TDDFT(td_dict, engine.EngineGpaw(),self.controller.status,str(self.controller.directory), filename,keyword='laser')
#         self.controller.task = self.job
#         self.controller.check = True

#     def write_input(self):
#         self.job.write_input()
#         self.controller.check = True
        
#     def save_button(self):
#         inp_dict = self.tdpulse_inp2dict()
#         self.init_task(inp_dict, 'tdlaser')
#         self.write_input()
#         show_message(self.label_msg,"Saved")

#     def view_button(self):
#         inp_dict = self.tdpulse_inp2dict()
#         self.init_task(inp_dict, 'tdlaser')
#         self.controller._show_frame(TextViewerPage, LaserDesignPage, None, task=self.controller.task)

#     def run_job_button(self):
#         try:
#             getattr(self.job.engine,'directory')           
#         except AttributeError:
#             messagebox.showerror(message="Input not saved. Please save the input before job submission")
#         else:
#             self.event_generate('<<ShowJobSubmissionPage>>')

#     def back_button(self):
#         self.event_generate('<<ShowWorkManagerPage>>')

# def updatekey(dict, key, value):
#     dict[key] = value
#     return(dict)

class PlotSpectraPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        

        self.axis = StringVar()

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
        
        self.heading = Label(self.Frame,text="LITESOPH Spectrum Calculations and Plots", fg='blue')
        self.heading['font'] = myFont
        self.heading.place(x=350,y=10)
        
        self.label_pol = Label(self.Frame, text= "Calculation of absorption spectrum:",bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=60)

        self.Frame2_Button_1 = tk.Button(self.Frame,text="Create input",activebackground="#78d6ff",command=lambda:[self.createspec()])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=290,y=60)

        self.label_msg = Label(self.Frame, text= "",fg="black")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=420,y=60)

        self.Frame2_Run = tk.Button(self.Frame,text="Run Job", state= 'disabled',activebackground="#78d6ff",command=lambda:[self.event_generate('<<ShowJobSubmissionPage>>')])
        self.Frame2_Run['font'] = myFont
        self.Frame2_Run.place(x=320,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)

        self.show_plot()

    def show_plot(self):
        check = self.controller.status.check_status('spectra', 2)
        if check is True:
            self.create_plot()  
        else:
            pass        
    
    def create_plot(self):
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.label_pol = Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=130)

        ax_pol = ["x","y","z"]
        self.entry_pol_x = ttk.Combobox(self.Frame, textvariable= self.axis, value = ax_pol, width= 15)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"x")
        self.entry_pol_x.place(x=160,y=130)
        self.entry_pol_x['state'] = 'readonly'
        
        self.Frame2_Plot = tk.Button(self.Frame,text="Plot",activebackground="#78d6ff",command=lambda:[plot_spectra(self.returnaxis(),str(self.controller.directory)+'/Spectrum/spec.dat',str(self.controller.directory)+'/Spectrum/spec.png','Energy (eV)','Photoabsorption (eV$^{-1}$)', None)])
        self.Frame2_Plot['font'] = myFont
        self.Frame2_Plot.place(x=320,y= 130)
    
    def returnaxis(self):
        if self.axis.get() == "x":
            axis = 1
        if self.axis.get() == "y":
            axis = 2
        if self.axis.get() == "z":
            axis = 3
        return axis

    def createspec(self):
        spec_dict = {}
        spec_dict['moment_file'] = pathlib.Path(self.controller.directory) / "TD_Delta" / "dm.dat"
        # spec_dict['spectrum_file'] = pathlib.Path(self.controller.directory) / "Spectrum"/ specfile
        job = Spectrum(spec_dict,  engine.EngineGpaw(), str(self.controller.directory),'spec') 
        job.write_input()
        self.controller.task = job
        self.controller.check = True
        self.controller.status.update_status('spectra', 1)
        show_message(self.label_msg, "Saved")
        self.Frame2_Run.config(state='active')
      

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

class TcmPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.min = DoubleVar()
        self.max = DoubleVar()
        self.step = DoubleVar()
        self.freq = DoubleVar()

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)
        
        self.Frame.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.978)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
        
        self.heading = Label(self.Frame,text="LITESOPH Kohn Sham Decomposition", fg='blue')
        self.heading['font'] = myFont
        self.heading.place(x=350,y=10)

        self.FrameTcm2_label_path = Label(self.Frame,text="Frequency space density matrix",fg="blue")
        self.FrameTcm2_label_path['font'] = myFont
        self.FrameTcm2_label_path.place(x=10,y=50)

        self.Label_freqs = Label(self.Frame,text="List of the Frequencies obtained from the photoabsorption \nspectrum (in eV) at which Fourier transform of density matrix is sought.\n(Entries should be separated by space,eg: 2.1  4)",fg="black", justify='left')
        self.Label_freqs['font'] = myFont
        self.Label_freqs.place(x=10,y=80)
        
        self.TextBox_freqs = Text(self.Frame, height=4, width=60)
        self.TextBox_freqs['font'] = myFont
        self.TextBox_freqs.place(x=10,y=150)

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

        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)

        #self.buttonRetrieve = Button(self.Frame, text="Retrieve Freq",activebackground="#78d6ff",command=lambda:[self.retrieve_input(),self.freq_listbox(), self.tcm_button()])
        self.buttonRetrieve = Button(self.Frame, text="Create input",activebackground="#78d6ff",command=lambda:self.create_tcm())
        self.buttonRetrieve['font'] = myFont
        self.buttonRetrieve.place(x=200,y=380)

        self.Frame_run = tk.Button(self.Frame,text="Run Job", state= 'disabled',activebackground="#78d6ff", command=lambda:[self.event_generate('<<ShowJobSubmissionPage>>')])
        self.Frame_run['font'] = myFont
        self.Frame_run.place(x=360,y=380)
        
    def retrieve_input(self):
        inputValues = self.TextBox_freqs.get("1.0", "end-1c")
        freqs = inputValues.split()

        self.freq_list = []
        for freq in freqs[0:]:
            self.freq_list.append(float(freq))
        return(self.freq_list)   
    
    def create_tcm(self):
        self.retrieve_input()
        gs = pathlib.Path(self.controller.directory) / "GS" / "gs.gpw"
        wf = pathlib.Path(self.controller.directory) / "TD_Delta" / "wf.ulm"
        tcm_dict = {
                'gfilename' : gs,
                'wfilename' : wf,
                'frequencies' : self.freq_list,
                'name' : "x"
                 }         
        self.job = TCM(tcm_dict, engine.EngineGpaw(), self.controller.directory,  'tcm')
        self.job.write_input()
        self.controller.task = self.job 
        self.controller.check = False
        self.Frame_run.config(state= 'active')      

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
  
class TextViewerPage(Frame):

    def __init__(self, parent, controller, file=None, task=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        self.file = file
        self.task = task

        #self.axis = StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)

        self.Frame.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.98)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
  
        self.FrameTcm1_label_path = Label(self, text="LITESOPH Text Viewer",fg="blue")
        self.FrameTcm1_label_path['font'] = myFont
        self.FrameTcm1_label_path.place(x=400,y=10)

        
        text_scroll =Scrollbar(self)
        text_scroll.pack(side=RIGHT, fill=Y)

        my_Text = Text(self, width = 130, height = 20, yscrollcommand= text_scroll.set)
        my_Text['font'] = myFont
        my_Text.place(x=15,y=60)

        if self.file:
            self.inserttextfromfile(self.file, my_Text)
            self.current_file = self.file
        if self.task:
            self.inserttextfromstring(self.task.template, my_Text)
            self.current_file = self.file

        text_scroll.config(command= my_Text.yview)
    
         
        #view = tk.Button(self, text="View",activebackground="#78d6ff",command=lambda:[self.open_txt(my_Text)])
        #view['font'] = myFont
        #view.place(x=150,y=380)

        save = tk.Button(self, text="Save",activebackground="#78d6ff",command=lambda:[self.save_txt(my_Text)])
        save['font'] = myFont
        save.place(x=320, y=380)

        back = tk.Button(self, text="Back",activebackground="#78d6ff",command=lambda:[self.back_button()])
        back['font'] = myFont
        back.place(x=30,y=380)

        # jobsub = tk.Button(self, text="Run Job",bg='blue',fg='white',command=lambda:controller._show_frame(JobSubPage))
        # jobsub['font'] = myFont
        # jobsub.place(x=800,y=380)

    #def open_txt(self,my_Text):
        #text_file_name = filedialog.askopenfilename(initialdir= user_path, title="Select File", filetypes=(("All Files", "*"),))
        #self.current_file = text_file_name
        #self.inserttextfromfile(text_file_name, my_Text)
    
   
    def inserttextfromfile(self, filename, my_Text):
        text_file = open(filename, 'r')
        stuff = text_file.read()
        my_Text.insert(END,stuff)
        text_file.close()
 
    def save_txt(self, my_Text):
        if self.file:
            text_file = self.current_file
            text_file = open(text_file,'w')
            text_file.write(my_Text.get(1.0, END))
        else:
            self.task.write_input(template=my_Text.get(1.0, END))

    def inserttextfromstring(self, string, my_Text):
        my_Text.insert(END,string)
    
    def back_button(self):
        self.event_generate('<<ClickBackButton>>')

        
        

#--------------------------------------------------------------------------------        


if __name__ == '__main__':
   
    
    app = AITG()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
