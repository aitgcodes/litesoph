from tkinter import *                    # importing tkinter, a standart python interface for GUI.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from tkinter import scrolledtext
#from ttkthemes import ThemedTk
import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk
import sys
#import base64
import os
import pathlib 
#import platform
import webbrowser
from tkinter.messagebox import showinfo
from urllib.request import urlopen
#import pandas as pd
#from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib as mpl
#import seaborn as sns
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#---LITESOPH modules

from litesoph.GUI.menubar import MainMenu
from litesoph.simulations import esmd
from litesoph.GUI import projpath
from litesoph.GUI.spec_plot import plot_spectra
from litesoph.lsio.IO import UserInput as ui
from litesoph.simulations.esmd import RT_LCAO_TDDFT, GroundState
from litesoph.simulations import engine
from litesoph.GUI.filehandler import *
from litesoph.GUI.navigation import Nav
#from litesoph.GUI.navigation import TextViewerPage
#from litesoph.GUI.laserframe import Laser
from litesoph.Pre_Processing.preproc import *
from litesoph.simulations.GPAW.gpaw_template import RtLcaoTddft as rt
from litesoph.simulations.GPAW.spectrum import spectrum
#from litesoph.lsio.IO import write22file
from litesoph.GUI.filehandler import Status




TITLE_FONT = ("Helvetica", 18, "bold")

class VISUAL():

     def __init__(self, tool="None", toolpath="/usr/local/bin"):
       
         self.vistool={}
         if tool == "None":
            self.vistool["name"]="None"
            self.vistool["exists"]=False
            self.vistool["params"]=""
         else:
            self.vistool["name"]=tool
            self.vistool["exists"]=True

class AITG(Tk):

    def __init__(self, lsconfig, *args, **kwargs):
        super().__init__()

        self.mainmenu = MainMenu(self)
        self.lsconfig = lsconfig
        self.configs = self.lsconfig.configs
        self.lsroot = self.lsconfig.lsroot
        self.directory = self.configs['lsproject']

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=6)
       
        self.nav = None
        self.refresh_nav(self.directory)
        
        self.window = Frame(self)
        self.window.grid(row=0, column=1)
        
        self.window.grid_rowconfigure(700,weight=700)
        self.window.grid_columnconfigure(800,weight=400)        
        
        self.show_frame(StartPage)
        self.status_init(self.directory)
        
    
    def status_init(self, path):
        self.directory = path
        self.status = Status(self.directory)
        
    
    def show_frame(self, frame, prev = None, next = None):
        
        if isinstance(frame, Frame):
            frame.destroy()
            frame = frame(self.window, self, prev, next)
            frame.grid(row=0, column=1, sticky ="nsew")
            frame.tkraise()
        else:
            frame = frame(self.window, self, prev, next)
            frame.grid(row=0, column=1, sticky ="nsew")
            frame.tkraise()

    def refresh_nav(self, path):

        if isinstance(self.nav, Nav):
            self.nav.destroy()
            self.nav = Nav(self, path)
            self.nav.grid(row=0, column=0, sticky='nw')
        else:
            self.nav = Nav(self, path)
            self.nav.grid(row=0, column=0, sticky='nw')

    def task_input(self,sub_task, task_check):
        if task_check is True:
            if sub_task.get()  == "Ground State":
               self.show_frame(GroundStatePage, WorkManagerPage, JobSubPage)
               path1 = projpath.create_folder(self.directory, "GS")
               os.chdir(path1)
            if sub_task.get() == "Geometry Optimisation":
               self.show_frame(GeomOptPage, WorkManagerPage, JobSubPage)
            if sub_task.get() == "Delta Kick":           
               self.show_frame(TimeDependentPage, WorkManagerPage, JobSubPage)
               path = projpath.create_folder(self.directory, "Spectrum")
               os.chdir(path)  
            if sub_task.get() == "Gaussian Pulse":
               self.show_frame(LaserDesignPage, WorkManagerPage, JobSubPage)
               path = projpath.create_folder(self.directory, "Pulse")
               os.chdir(path)
            if sub_task.get() == "Spectrum":
               self.show_frame(PlotSpectraPage)
            if sub_task.get() == "Dipole Moment and Laser Pulse":
               self.show_frame(DmLdPage)
            if sub_task.get() == "Transition Contribution Map":
               self.show_frame(TcmPage) 
                  
    def gui_inp(self, task, filename, gui_dict):
        
        if task == 'gs':
            ui.user_param.update(gui_dict) # update the user parameters
            dict_input = ui.user_param
            dict_input['directory'] = str(self.directory)+"/GS"
            dict_input['geometry'] = pathlib.Path(self.directory) / "coordinate.xyz"
            engn = engine.choose_engine(dict_input)
            GroundState(dict_input, filename, engn)
            self.status.update_status('gs_inp', 1)
            
        if task == 'td':
            rt.default_input.update(gui_dict)
            dict_input = rt.default_input
            RT_LCAO_TDDFT(dict_input,filename, engine.EngineGpaw(),str(self.directory)+"/Spectrum")
            
    def createspec(self, dipolefile, specfile):
        spec = spectrum()
        spec_dict = spec.user_input
        spec_dict['moment_file'] = pathlib.Path(self.directory) / dipolefile
        spec_dict['spectrum_file'] = pathlib.Path(self.directory) / specfile
        spec.cal_photoabs_spectrum(spec_dict) 
    
class StartPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
              

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        mainframe = ttk.Frame(self,padding="12 12 24 24")
        #mainframe = ttk.Frame(self)
        mainframe.grid(column=1, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        frame =ttk.Frame(self, relief=SUNKEN, padding="6 6 0 24")
        #frame =ttk.Frame(self)
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=10,weight='bold')
        myFont = font.Font(family='Helvetica', size=15, weight='bold')

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 20))

        self.configure(bg="grey60")

        # create a canvas to show project list icon
        canvas_for_project_list_icon=Canvas(frame, bg='gray', height=400, width=400, borderwidth=0, highlightthickness=0)
        canvas_for_project_list_icon.grid(column=1, row=1, sticky=(W, E) ,columnspan=8,rowspan=8)
        #canvas_for_project_list_icon.place(x=5,y=5)

        #image_project_list = Image.open('images/project_list.png')
        #canvas_for_project_list_icon.image = ImageTk.PhotoImage(image_project_list.resize((100,100), Image.ANTIALIAS))
        #canvas_for_project_list_icon.create_image(0,0, image=canvas_for_project_list_icon.image, anchor='nw')
        
        #frame_1_label_1 = Label(frame,text="Manage Job(s)", fg="blue")
        #frame_1_label_1['font'] = myFont
        #frame_1_label_1.grid(row=10, column=2, sticky=(W, E) ,columnspan=3,rowspan=2)

        #label_1 = Label(mainframe,text="Welcome to LITESOPH", bg='#0052cc',fg='#ffffff')
        label_1 = Label(mainframe,text="Welcome to LITESOPH",fg='blue')
        label_1['font'] = myFont
        #label_1.grid(row=0,column=1,sticky=(E,S))
        label_1.place(x=200,y=50)
        
        label_2 = Label(mainframe,text="Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena",fg='blue')
        label_2['font'] = l
        label_2.grid(row=1,column=1)
        #label_2.place(x=200,y=100)

        # create a canvas to show image on
        canvas_for_image = Canvas(mainframe, bg='gray', height=125, width=125, borderwidth=0, highlightthickness=0)
        #canvas_for_image.grid(row=30,column=0, sticky='nesw', padx=0, pady=0)
        canvas_for_image.place(x=30,y=5)

        # create image from image location resize it to 100X100 and put in on canvas
        path1 = pathlib.PurePath(controller.lsroot) / "litesoph" / "GUI" / "images"

        image = Image.open(str(pathlib.Path(path1) / "logo_ls.jpg"))
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((125, 125), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open(str(pathlib.Path(path1) / "project_create.png"))
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = Button(mainframe,text="Start LITESOPH Project", bg="black",fg="white",command=lambda: controller.show_frame(WorkManagerPage))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        button_open_project = Button(mainframe,text="About LITESOPH", bg="black",fg="white")
        button_open_project['font'] = myFont
        button_open_project.place(x=80,y=300)


class WorkManagerPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1 = tk.Frame(self)
        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        self.Frame1_label_path = Label(self.Frame1,text="Project Path",bg="gray",fg="black")
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=10,y=10)

        self.entry_path = Entry(self.Frame1,textvariable="proj_path")
        self.entry_path['font'] = myFont
        self.entry_path.insert(0,str(self.controller.directory))
        self.entry_path.place(x=200,y=10)

        self.label_proj = Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        self.entry_proj = Entry(self.Frame1,textvariable="proj_name")
        self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"graphene")
        self.entry_proj.place(x=200,y=70)
                
        self.button_project = Button(self.Frame1,text="Create New Project",bg='blue',fg='white',command=lambda:[self.retrieve_input(),projpath.create_path(self.projectpath,self.projectname),os.chdir(self.projectpath+"/"+self.projectname),getprojectdirectory(self.projectpath,self.projectname),self.controller.refresh_nav(user_path), controller.status_init(user_path)])
        self.button_project['font'] = myFont
        self.button_project.place(x=125,y=360)
      
        self.Frame1_Button_MainPage = Button(self.Frame1, text="Start Page",bg='blue',fg='white', command=lambda: controller.show_frame(StartPage))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=10,y=360)
        
        self.button_project = Button(self.Frame1,text="Open Existing Project",bg='blue',fg='white',command=lambda:[self.retrieve_input(),projpath.dir_exist(self.projectpath,self.projectname),os.chdir(self.projectpath+"/"+self.projectname),getprojectdirectory(self.projectpath,self.projectname),self.controller.refresh_nav(user_path), controller.status_init(user_path)])
        self.button_project['font'] = myFont
        self.button_project.place(x=290,y=360)
        
        #self.message_label = Label(self.Frame2, text='', foreground='red')
        #self.message_label['font'] = myFont
        #self.message_label.place(x=270,y=15)
 
        #self.message_label2 = Label(self.Frame1, text='', foreground='red')
        #self.message_label2['font'] = myFont
        #self.message_label2.place(x=,y=15)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",bg='blue',fg='white',command=lambda:[open_file(user_path),show_message(self.message_label,"Uploaded")])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        
        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",bg='blue',fg='white',command=self.geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=350,y=10)

        self.label_proj = Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        MainTask = ["--Choose Job--","Preprocessing Jobs","Simulations","Postprocessing Jobs"]

        # Create a list of sub_task
        choosejob = [""]  
        Pre_task = ["Ground State","Geometry Optimisation"]
        Sim_task = ["Delta Kick","Gaussian Pulse"]
        Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Transition Contribution Map","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]
        #Spec_task = ["Absorption Spectrum"]

        def pick_task(e):
            if task.get() == "--Choose Job--":
                sub_task.config(value = choosejob)
                sub_task.current(0)
            if task.get() == "Preprocessing Jobs":
                sub_task.config(value = Pre_task)
                sub_task.current(0)
            if task.get() == "Simulations":
                sub_task.config(value = Sim_task)
                sub_task.current(0)
            if task.get() == "Postprocessing Jobs":
                sub_task.config(value = Post_task)
                sub_task.current(0)
            
        task = ttk.Combobox(self.Frame2,width= 30, values= MainTask)
        task.current(0)
        task['font'] = myFont
        task.place(x=200,y=70)
        task.bind("<<ComboboxSelected>>", pick_task)

        self.Frame2_label_3 = Label(self.Frame2, text="Sub Task",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=130)
          
        sub_task = ttk.Combobox(self.Frame2, width= 30, value = [" "])
        sub_task['font'] = myFont
        sub_task.current(0)
        sub_task.place(x=200,y=130)
                       
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",bg='blue',fg='white',command=lambda:[controller.task_input(sub_task,self.task_check(sub_task))])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=360)

    def geom_visual(self):
        cmd = self.controller.configs['vmd']+ " "+"coordinate.xyz"
        try:
           p = subprocess.run(cmd.split(),capture_output=True, cwd=self.controller.directory)
        except:
            print("Unable to invoke vmd. Command used to call vmd '{}'. supply the appropriate command in lsconfig.in".format(cmd.split()[0]))

    def retrieve_input(self):
        self.projectpath = self.entry_path.get()
        self.projectname = self.entry_proj.get()
    
    def task_check(self,sub_task):
        self.st_var = self.controller.status
        
        if sub_task.get()  == "Ground State":
            path = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            if path.exists() is True:
                return True
            else:
                messagebox.showerror(message= "Upload geometry file")
        elif sub_task.get() == "Delta Kick":
            if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
                return True
            else:
                messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")       
        elif sub_task.get() == "Gaussian Pulse":
            if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
                return True
            else:
                messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")
        elif sub_task.get() == "Spectrum":
            if self.st_var.check_status('gs_cal', 1) is True and self.st_var.check_status('td_cal',1) is True:
                return True
            else:
                messagebox.showerror(message=" Please complete Ground State and Delta kick calculation.")
        elif sub_task.get() == "Dipole Moment and Laser Pulse":
            if self.st_var.check_status('gs_cal', 1) is True and self.st_var.check_status('td_cal',2) is True:
                return True
            else:
                messagebox.showerror(message=" Please complete Ground State and Gaussian Pulse calculation.")
        else:
            return True

def getprojectdirectory(path, name):
    global user_path
    user_path = pathlib.Path(path) / name
    return user_path

class GroundStatePage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame1 = tk.Frame(self)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        h   = StringVar()
        nbands = StringVar()
        vacuum = StringVar()
        mode = StringVar()
        xc = StringVar()
        basis = StringVar()
        charge = StringVar()
        spinpol = StringVar()
        multip = StringVar()
        energy = StringVar()
        bands = StringVar()
        maxiter = StringVar()

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")            
        
        self.Frame1_label_path = Label(self.Frame1,text="LITESOPH input for Ground State",fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=150,y=10)
      
        self.label_proj = Label(self.Frame1,text="Mode",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)
        
        Mainmode = ["--Choose Mode--","lcao","fd","pw","gaussian"]

        # Create a list of sub_task  
        choosemode = [""]
        lcao_task = ["dzp","pvalence.dz","cc-pvdz"]
        fd_task = [""]
        pw_task = [""]
        gauss_task = ["6-31+G*","6-31+G","6-31G*","6-31G","3-21G"]

        def pick_task(e):
            if task.get() == "--Choose Mode--":
                sub_task.config(value = choosemode)
                sub_task.current(0)
            if task.get() == "lcao":
                sub_task.config(value = lcao_task)
                sub_task.current(0)
            if task.get() == "fd":
                sub_task.config(value = fd_task)
                sub_task.current(0)
            if task.get() == "pw":
                sub_task.config(value = pw_task)
                sub_task.current(0)
            if task.get() == "gaussian":
                sub_task.config(value = gauss_task)
                sub_task.current(0)

        task = ttk.Combobox(self.Frame1, textvariable = mode, values= Mainmode)
        task.current(0)
        task['font'] = myFont
        task.place(x=250,y=60)
        task.bind("<<ComboboxSelected>>", pick_task)

        self.Frame2_label_3 = Label(self.Frame1, text="Basis",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=110)
          
        sub_task = ttk.Combobox(self.Frame1, textvariable= basis, value = [" "])
        sub_task.current(0)
        sub_task['font'] = myFont
        sub_task.place(x=250,y=110)

        self.label = Label(self.Frame1, text="Exchange Correlation", bg= "grey",fg="black")
        self.label['font'] = myFont
        self.label.place(x=10,y=160)
       
        exch_cor = ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"]

        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= xc, value = exch_cor)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=160)

        self.label_pol_y = Label(self.Frame1, text="Spacing (in Angstrom)", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=210)
    
        self.entry_proj = Entry(self.Frame1,textvariable= h)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=250,y=210)

        self.label_pol_z = Label(self.Frame1, text="Number of Bands", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=260)
 
        self.entry_proj = Entry(self.Frame1,textvariable= nbands)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=260)

        self.label_proj = Label(self.Frame1,text="Vacuum size (in Angstrom)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= vacuum)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"6")
        self.entry_proj.place(x=250,y=310)
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)
        
        Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",bg='blue',fg='white', command=lambda:[controller.gui_inp('gs','gs',gs_inp2dict()), show_message(self.label_msg, "Saved")])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=350,y=380)

        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=370,y=350)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.label_proj = Label(self.Frame2,text="Charge",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame2,textvariable= charge)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=60)
        
        self.Frame2_note = Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=110)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= spinpol, value = ["None","True"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=110)

        self.Frame2_note = Label(self.Frame2,text="Multiplicity",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = Entry(self.Frame2,textvariable= multip)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=160)
  
        self.Frame2_note = Label(self.Frame2,text="Energy Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"5e-05")
        self.entry_proj.place(x=250,y=210)

        self.Frame2_note = Label(self.Frame2,text="Maxiter",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame2,textvariable= maxiter)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"300")
        self.entry_proj.place(x=250,y=260)
     
        self.Frame2_note = Label(self.Frame2,text="Band Occupancy",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=310)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= bands, value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=310)

        Frame2_Button3 = tk.Button(self.Frame2, text="View Input",bg='blue',fg='white', command=lambda:[controller.gui_inp('gs','gs',gs_inp2dict()), controller.show_frame(TextViewerPage, GroundStatePage, None)])
        Frame2_Button3['font'] = myFont
        Frame2_Button3.place(x=10,y=380)
 
        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(self.next, GroundStatePage, None))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=350,y=380)

        def gs_inp2dict():
            inp_dict = {
                'mode': mode.get(),
                'xc': xc.get(),
                'basis': basis.get(),
                'vacuum': vacuum.get(),
                'h': h.get(),
                'nbands' : nbands.get(),
                'charge' : charge.get(),
                'spinpol' : spinpol.get(),
                'multip' : None, 
                'convergence' : {'energy' : float(energy.get()), 'bands' : bands.get()},
                'maxiter' : maxiter.get(),
                'properties': 'get_potential_energy()',
                'engine':'gpaw'
                        }          
            return inp_dict  

class GeomOptPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame1 = tk.Frame(self)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        h   = StringVar()
        nbands = StringVar()
        vacuum = StringVar()
        mode = StringVar()
        xc = StringVar()
        basis = StringVar()
        charge = StringVar()
        spinpol = StringVar()
        multip = StringVar()
        energy = StringVar()
        bands = StringVar()
        maxiter = StringVar()

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")            
        
        self.Frame1_label_path = Label(self.Frame1,text="LITESOPH input for Geometery Optimisation",fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=150,y=10)
      
        self.label_proj = Label(self.Frame1,text="Mode",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)
        
        Mainmode = ["--Choose Mode--","lcao","fd","pw","gaussian"]

        # Create a list of sub_task  
        choosemode = [""]
        lcao_task = ["dzp","pvalence.dz","cc-pvdz"]
        fd_task = [""]
        pw_task = [""]
        gauss_task = ["6-31+G*","6-31+G","6-31G*","6-31G","3-21G"]

        def pick_task(e):
            if task.get() == "--Choose Mode--":
                sub_task.config(value = choosemode)
                sub_task.current(0)
            if task.get() == "lcao":
                sub_task.config(value = lcao_task)
                sub_task.current(0)
            if task.get() == "fd":
                sub_task.config(value = fd_task)
                sub_task.current(0)
            if task.get() == "pw":
                sub_task.config(value = pw_task)
                sub_task.current(0)
            if task.get() == "gaussian":
                sub_task.config(value = gauss_task)
                sub_task.current(0)

        task = ttk.Combobox(self.Frame1, textvariable = mode, values= Mainmode)
        task.current(0)
        task['font'] = myFont
        task.place(x=250,y=60)
        task.bind("<<ComboboxSelected>>", pick_task)

        self.Frame2_label_3 = Label(self.Frame1, text="Basis",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=110)
          
        sub_task = ttk.Combobox(self.Frame1, textvariable= basis, value = [" "])
        sub_task.current(0)
        sub_task['font'] = myFont
        sub_task.place(x=250,y=110)

        self.label = Label(self.Frame1, text="Exchange Correlation", bg= "grey",fg="black")
        self.label['font'] = myFont
        self.label.place(x=10,y=160)
       
        exch_cor = ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"]

        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= xc, value = exch_cor)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=160)

        self.label_pol_y = Label(self.Frame1, text="Spacing (in Angstrom)", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=210)
    
        self.entry_proj = Entry(self.Frame1,textvariable= h)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=250,y=210)

        self.label_pol_z = Label(self.Frame1, text="Number of Bands", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=260)
 
        self.entry_proj = Entry(self.Frame1,textvariable= nbands)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=260)

        self.label_proj = Label(self.Frame1,text="Vacuum size (in Angstrom)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= vacuum)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"6")
        self.entry_proj.place(x=250,y=310)
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)
        
        Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",bg='blue',fg='white', command=lambda:[controller.gui_inp('gs','gs',gs_inp2dict()), show_message(self.label_msg, "Saved")])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=350,y=380)

        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=370,y=350)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.label_proj = Label(self.Frame2,text="Charge",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame2,textvariable= charge)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=60)
        
        self.Frame2_note = Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=110)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= spinpol, value = ["None","True"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=110)

        self.Frame2_note = Label(self.Frame2,text="Multiplicity",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = Entry(self.Frame2,textvariable= multip)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=160)
  
        self.Frame2_note = Label(self.Frame2,text="Energy Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"5e-05")
        self.entry_proj.place(x=250,y=210)

        self.Frame2_note = Label(self.Frame2,text="Maxiter",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame2,textvariable= maxiter)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"300")
        self.entry_proj.place(x=250,y=260)
     
        self.Frame2_note = Label(self.Frame2,text="Band Occupancy",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=310)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= bands, value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=310)

        Frame2_Button3 = tk.Button(self.Frame2, text="View Input",bg='blue',fg='white', command=lambda:[controller.gui_inp('gs','gs',gs_inp2dict()), controller.show_frame(TextViewerPage, GroundStatePage, None)])
        Frame2_Button3['font'] = myFont
        Frame2_Button3.place(x=10,y=380)
 
        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(self.next, GroundStatePage, None))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=350,y=380)

        def gs_inp2dict():
            inp_dict = {
                'mode': mode.get(),
                'xc': xc.get(),
                'basis': basis.get(),
                'vacuum': vacuum.get(),
                'h': h.get(),
                'nbands' : nbands.get(),
                'charge' : charge.get(),
                'spinpol' : spinpol.get(),
                'multip' : None, 
                'convergence' : {'energy' : float(energy.get()), 'bands' : bands.get()},
                'maxiter' : maxiter.get(),
                'properties': 'get_potential_energy()',
                'engine':'gpaw'
                        }          
            return inp_dict  

  
class TimeDependentPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame1 = tk.Frame(self)
        #self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        strength = StringVar()
        self.ex = StringVar()
        self.ey = StringVar()
        self.ez = StringVar()
        dt = StringVar()
        Nt = StringVar()    
                
        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")            
        
        self.Frame1_label_path = Label(self.Frame1,text="LITESOPH input for Delta Kick",fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=150,y=10)
      
        self.label_proj = Label(self.Frame1,text="Laser strength in a.u",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)
        
        inval = ["1e-5","1e-3"]
        self.entry_proj = ttk.Combobox(self.Frame1,textvariable= strength, value = inval)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"1e-5")
        self.entry_proj.place(x=250,y=60)

        self.label_pol_x = Label(self.Frame1, text="Electric Polarisation in x axis", bg= "grey",fg="black")
        self.label_pol_x['font'] = myFont
        self.label_pol_x.place(x=10,y=110)
        
        pol_list = ["0","1"]
        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= self.ex , value = pol_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"0")
        self.entry_pol_x.place(x=250,y=110)

        self.label_pol_y = Label(self.Frame1, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=160)
    
        self.entry_pol_y = ttk.Combobox(self.Frame1, textvariable= self.ey, value = pol_list)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.insert(0,"0")
        self.entry_pol_y.place(x=250,y=160)

        self.label_pol_z = Label(self.Frame1, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=210)
 
        self.entry_pol_z = ttk.Combobox(self.Frame1, textvariable= self.ez ,value = pol_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"0")
        self.entry_pol_z.place(x=250,y=210)

        self.label_proj = Label(self.Frame1,text="Propagation time step (in attosecond)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= dt)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"10")
        self.entry_proj.place(x=250,y=260)

        self.label_proj = Label(self.Frame1,text="Total time steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= Nt)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"200")
        self.entry_proj.place(x=250,y=310)
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)

        Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",bg='blue',fg='white',command=lambda:[controller.gui_inp('td','td', td_inp2dict()), controller.status.update_status('td_inp', 1), show_message(self.label_msg, "Saved")])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=350,y=380)

        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=370,y=350)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.Frame2_note = Label(self.Frame2,text="Optional Input Parameters",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=10)
 
        Frame2_Button1 = tk.Button(self.Frame2, text="View Input",bg='blue',fg='white',command=lambda:[controller.gui_inp('td','td', td_inp2dict()),controller.status.update_status('td_inp', 1), controller.show_frame(TextViewerPage, TimeDependentPage, None)])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(self.next, TimeDependentPage, None))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=350,y=380)
   
        def td_inp2dict():
            td_dict = rt.default_input
            path = str(controller.directory) + "/GS"
            td_dict['filename'] = path +"/gs.gpw"
            td_dict['absorption_kick'][0] = float(strength.get())*float(self.ex.get())
            td_dict['absorption_kick'][1] = float(strength.get())*float(self.ey.get())
            td_dict['absorption_kick'][2] = float(strength.get())*float(self.ez.get())
            inp_list = [float(dt.get()),float(Nt.get())]
            td_dict['propagate'] = tuple(inp_list)
            return td_dict

class LaserDesignPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        self.tdpulse_dict = rt.default_input
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame1 = tk.Frame(self)
        #self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        self.strength = StringVar()
        self.inval = StringVar()
        self.pol_x = StringVar()
        self.pol_y = StringVar()
        self.pol_z = StringVar()
        self.fwhm = StringVar()
        self.freq = StringVar()
        self.ts = StringVar()
        self.ns = StringVar()
        self.tin = StringVar()

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        
        self.Frame1_label_path = Label(self.Frame1,text="LITESOPH Input for Laser Design", fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=125,y=10)
      
             
        self.label_pol_x = Label(self.Frame1, text="Electric Polarisation in x axis", bg= "grey",fg="black")
        self.label_pol_x['font'] = myFont
        self.label_pol_x.place(x=10,y=60)
        
        pol_list = ["0","1"]
        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= self.pol_x, value = pol_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"0")
        self.entry_pol_x.place(x=250,y=60)

        self.label_pol_y = Label(self.Frame1, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=110)
    
        self.entry_pol_y = ttk.Combobox(self.Frame1,textvariable= self.pol_y, value = pol_list)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.insert(0,"0")
        self.entry_pol_y.place(x=250,y=110)

        self.label_pol_z = Label(self.Frame1, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=160)
 
        self.entry_pol_z = ttk.Combobox(self.Frame1,textvariable= self.pol_z, value = pol_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"0")
        self.entry_pol_z.place(x=250,y=160)

        self.label_proj = Label(self.Frame1,text="Frequency in eV",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame1,textvariable= self.freq)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=210)

        self.label_proj = Label(self.Frame1,text="Time step in attosecond ",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= self.ts)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"10")
        self.entry_proj.place(x=250,y=260)
        
        self.label_proj = Label(self.Frame1,text="Number of Steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= self.ns)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"2000")
        self.entry_proj.place(x=250,y=310)
 
        Frame1_Button1 = tk.Button(self.Frame1, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=10,y=380)
        
        Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",bg='blue',fg='white', command=lambda:[self.tdpulse_inp2dict(),controller.gui_inp('td','td_pulse', self.td),controller.status.update_status('td_inp', 2), show_message(self.label_msg, "Saved")])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=350,y=380)
  
        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=370,y=350)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.label_proj = Label(self.Frame2,text="Time Origin (tin)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame2,textvariable= self.tin)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=60)

        self.label_proj = Label(self.Frame2,text="Pulse Amplitute at tin",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=110)
 
        inval_list = ["1e-8", "1e-9"]
        self.entry_pol_z = ttk.Combobox(self.Frame2,textvariable= self.inval, value = inval_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"1e-8")
        self.entry_pol_z.place(x=250,y=110)

        #self.entry_proj = Entry(self.Frame2,textvariable= inval)
        #self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"0")
        #self.entry_proj.place(x=250,y=110)

        self.label_proj = Label(self.Frame2,text="Laser Strength in a.u",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=160)
    
        instr = ["1e-5","1e-3"]
        self.entry_proj = ttk.Combobox(self.Frame2,textvariable= self.strength, value = instr)
        self.entry_proj['font'] = myFont
        self.entry_proj.current(0)
        self.entry_proj.place(x=250,y=160)

        self.label_proj = Label(self.Frame2,text="Full Width Half Max (FWHM in eV)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= self.fwhm)
        self.fwhm.set("0.2")
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=210)

        # self.button_project = Button(self.Frame2,text="Laser Design",bg='#0052cc',fg='#ffffff',command=self.laser_calc())
        # self.button_project['font'] = myFont
        # self.button_project.place(x=10,y=380)        
 
        Frame2_Button1 = tk.Button(self.Frame2, text="View Input",bg='blue',fg='white', command=lambda:[self.tdpulse_inp2dict(),controller.gui_inp('td','td_pulse', self.td),self.controller.status.update_status('td_inp', 2), controller.show_frame(TextViewerPage, LaserDesignPage, None)])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)
        
        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(self.next, LaserDesignPage, None))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=350,y=380)
      
    def laser_calc(self):
        l_dict = laser_design(self.strength.get(), self.inval.get(),self.tin.get(),self.fwhm.get())
        return(l_dict)

    def tdpulse_inp2dict(self):
        self.td = self.tdpulse_dict
        abs_x = float(self.strength.get())*float(self.pol_x.get())
        abs_y = float(self.strength.get())*float(self.pol_y.get())
        abs_z = float(self.strength.get())*float(self.pol_z.get())
        abs_list = [abs_x, abs_y, abs_z]
        inp_list = [float(self.ts.get()),int(self.ns.get())]
        epol_list = [float(self.pol_x.get()),float(self.pol_y.get()),float(self.pol_z.get())]
        laser_dict = self.laser_calc()
        updatekey(laser_dict, 'frequency', self.freq.get())
        updatekey(self.td,'absorption_kick',abs_list)
        updatekey(self.td,'propagate', tuple(inp_list))
        updatekey(self.td,'electric_pol',epol_list)
        updatekey(self.td,'dipole_file','dmpulse.dat')
        updatekey(self.td,'filename', 'gs.gpw')
        updatekey(self.td,'td_potential', True)
        updatekey(self.td,'txt', 'tdpulse.out')
        updatekey(self.td,'td_out', 'tdpulse.gpw')
        updatekey(self.td,'laser', laser_dict)
        return(self.td)       

def updatekey(dict, key, value):
    dict[key] = value
    return(dict)

class PlotSpectraPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

        self.axis = StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame = tk.Frame(self) 
        
        self.Frame.place(relx=0.01, rely=0.01, relheight=1.98, relwidth=0.978)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
        
        self.heading = Label(self.Frame,text="LITESOPH Spectrum Calculations and Plots", fg='blue')
        self.heading['font'] = myFont
        self.heading.place(x=350,y=10)
        
        self.label_pol = Label(self.Frame, text= "Axis of Electric polarization:",bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=60)

        self.label_pol = Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=110)

        ax_pol = ["x","y","z"]
        self.entry_pol_x = ttk.Combobox(self.Frame, textvariable= self.axis, value = ax_pol)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"x")
        self.entry_pol_x.place(x=250,y=110)

        self.Frame2_Button_1 = tk.Button(self.Frame,text="Plot",bg='blue',fg='white', command=lambda:[controller.createspec('Spectrum/dm.dat', 'Spectrum/spec.dat'),spectrum_show(str(controller.directory)+'/Spectrum','spec.dat','delta',self.returnaxis(),'Energy (eV)','Photoabsorption (eV$^{-1}$)')])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=250,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)
        
    def returnaxis(self):
        if self.axis.get() == "x":
            axis = 1
        if self.axis.get() == "y":
            axis = 2
        if self.axis.get() == "z":
            axis = 3
        return axis

class JobSubPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

        #self.axis = StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)

        processors = StringVar()
        job = StringVar()

        self.Frame.place(relx=0.01, rely=0.01, relheight=1.98, relwidth=0.978)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")

        sbj_label1 = Label(self, text="LITESOPH Job Submission", fg='blue')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=350,y=10)

        sbj_label1 = Label(self, text="Number of processors", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=60)

        sbj_entry1 = Entry(self,textvariable= processors, width=20)
        sbj_entry1.insert(0,"1")
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=60)
        
        sbj_label1 = Label(self, text="To submit job through Network, provide details", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=110)

        sbj_button1 = Button(self, text="Run Local",bg='blue', fg='white',command=lambda:[self.submitjob_local(sbj_entry1.get())])
        sbj_button1['font'] = myFont
        sbj_button1.place(x=600, y=60)

        self.msg_label1 = Label(self, text='', fg='blue')
        self.msg_label1['font'] = myFont
        self.msg_label1.place(x=600,y=100)

        back = tk.Button(self, text="Back to main page",bg='blue',fg='white',command=lambda:[controller.show_frame(WorkManagerPage)])
        back['font'] = myFont
        back.place(x=600,y=400)              

    # def deletelabel(self,label):
    #     label.destroy()
         
    def submitjob_local(self, processors):
        job = self.checkjob()
        self.select_job(job,processors)

    def checkjob(self):
        if self.prev.__name__ == 'GroundStatePage':
            return('gs')
        if self.prev.__name__ == 'TimeDependentPage':
            return('delta')   
        if self.prev.__name__ == 'LaserDesignPage':
            return('pulse')
        
    def call_run(self, filename, directory,key, value, processors):
        from litesoph.Utilities.run_local import run_local
        if processors == "1" :
            result = run_local(filename, directory) 
            self.controller.status.update_status(key, value) 
            show_message(self.msg_label1,"Job Done")
        else:
            result = run_local(filename, directory,int(processors)) 
            self.controller.status.update_status(key, value) 
            show_message(self.msg_label1,"Job Done")         
    
    def run_job(self,filename, directory, check, key, value1, value2, processors):
        if check is False:
            self.call_run(filename, directory,key, value1, processors) 
        else:
            show_message(self.msg_label1, "")
            check_yn = messagebox.askyesno(title="Job is done",message="Do you want to redo the calculation? ")
            if check_yn is True:
                self.controller.status.update_status(key, value2)
                self.call_run(filename, directory,key, value1, processors)

    def select_job(self, job, processors):
        self.st_var = self.controller.status
        if job == 'gs':
            path = str(self.controller.directory)+"/GS"
            msg2 = 'GS inputs not found'
            gs_check = self.st_var.check_status('gs_inp', 1)
            gs_cal_check = self.st_var.check_status('gs_cal', 1)
            if gs_check is True :
                self.run_job('gs.py',path,gs_cal_check, 'gs_cal', 1, 0, processors)                  
            else:
                show_message(self.msg_label1, msg2)

        if job == 'delta':
            path = str(self.controller.directory)+"/Spectrum"
            msg2 = 'Inputs not found'
            td_check = self.st_var.check_status('td_inp', 1) 
            gs_cal_check = self.st_var.check_status('gs_cal', 1)
            td_cal_check = self.st_var.check_status('td_cal', 1)
            if td_check is True and gs_cal_check is True :
                self.run_job('td.py',path,td_cal_check,'td_cal', 1, 0, processors)                 
            else:
                if td_check is False:
                    show_message(self.msg_label1,"Inputs not found. Please create inputs for delta kick." ) 
                elif gs_cal_check is False:
                    show_message(self.msg_label1, "Inputs not found. Please run GS calculation.")   
                        
        if job == 'pulse':
            path = str(self.controller.directory)+"/Pulse"
            td_check = self.st_var.check_status('td_inp', 2)
            gs_cal_check = self.st_var.check_status('gs_cal', 1)
            td_cal_check = self.st_var.check_status('td_cal', 2)
            if td_check is True and gs_cal_check is True:
                self.run_job('td_pulse.py',path,td_cal_check,'td_cal', 2, 1, processors)                  
            else:
                show_message(self.msg_label1, "Inputs not found.")                 

    def submitjob_network(self):
        pass

class DmLdPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

        self.plot_task = StringVar()
        self.compo = StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame = tk.Frame(self) 
        
        self.Frame.place(relx=0.01, rely=0.01, relheight=1.98, relwidth=0.978)
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

        plot_list = ["Dipole Moment","Laser Pulse"]
        self.entry_pol_x = ttk.Combobox(self.Frame,textvariable=self.plot_task, value = plot_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"Dipole Moment")
        self.entry_pol_x.place(x=250,y=60)


        #self.label_pol = Label(self.Frame, text= "Axis of Electric polarization:",fg="black")
        #self.label_pol['font'] = myFont
        #self.label_pol.place(x=10,y=110)

        self.label_pol = Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=110)

        com_pol = ["x component","y component","z component","total magnitude"]
        self.entry_pol_x = ttk.Combobox(self.Frame, textvariable= self.compo, value = com_pol)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"x component")
        self.entry_pol_x.place(x=250,y=110)

        self.Frame2_Button_1 = tk.Button(self.Frame,text="Plot",bg='blue',fg='white', command=lambda:[spectrum_show('dmpulse.dat','dm',self.returnaxis(),"time(attosecond)","Dipole moment")])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=250,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)
        
    def returnaxis(self):
        if self.compo.get() == "x component":
            axis = 2
        if self.compo.get() == "y component":
            axis = 3
        if self.compo.get() == "z component":
            axis = 4
        if self.compo.get() == "total magnitude":
            axis = 1
        return axis

def spectrum_show(directory,filename, suffix, axis, x, y):
        imgfile = "spec_{}_{}.png".format(suffix, axis)
        imgpath = str(directory) +"/" +imgfile
        filepath = str(directory)+"/"+filename
        plot_spectra(int(axis),filepath, imgpath, x, y)
        path = pathlib.Path(imgpath)
        img =Image.open(path)
        img.show()         

class TcmPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.FrameTcm1 = tk.Frame(self)
        
        strength = StringVar()
        pol_x = StringVar()
        pol_y = StringVar()
        pol_z = StringVar()
        dt = StringVar()
        Nt = StringVar()

        self.FrameTcm1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.FrameTcm1.configure(relief='groove')
        self.FrameTcm1.configure(borderwidth="2")
        self.FrameTcm1.configure(relief="groove")
        self.FrameTcm1.configure(cursor="fleur")

        self.FrameTcm1_label_path = Label(self.FrameTcm1,text="LITESOPH TCM Input",fg="blue")
        self.FrameTcm1_label_path['font'] = myFont
        self.FrameTcm1_label_path.place(x=150,y=10)

        self.label_strength = Label(self.FrameTcm1,text="Laser strength (in a.u)",bg="gray",fg="black")
        self.label_strength['font'] = myFont
        self.label_strength.place(x=10,y=60)

        inval = ["1e-5","1e-3"]
        self.Tcm_entry_strength = ttk.Combobox(self.FrameTcm1, value = inval)
        self.Tcm_entry_strength['font'] = myFont
        self.Tcm_entry_strength.insert(0,"1e-5")
        self.Tcm_entry_strength.place(x=250,y=60)

        self.Tcm_label_pol_x = Label(self.FrameTcm1, text="Electric Polarisation in x axis", bg= "grey",fg="black")
        self.Tcm_label_pol_x['font'] = myFont
        self.Tcm_label_pol_x.place(x=10,y=110)

        pol_list = ["0","1"]
        self.Tcm_entry_pol_x = ttk.Combobox(self.FrameTcm1, value = pol_list)
        self.Tcm_entry_pol_x['font'] = myFont
        self.Tcm_entry_pol_x.insert(0,"0")
        self.Tcm_entry_pol_x.place(x=250,y=110)

        self.Tcm_label_pol_y = Label(self.FrameTcm1, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.Tcm_label_pol_y['font'] = myFont
        self.Tcm_label_pol_y.place(x=10,y=160)

        
        self.Tcm_entry_pol_y = ttk.Combobox(self.FrameTcm1, value = pol_list)
        self.Tcm_entry_pol_y['font'] = myFont
        self.Tcm_entry_pol_y.insert(0,"0")
        self.Tcm_entry_pol_y.place(x=250,y=160)

        self.Tcm_label_pol_z = Label(self.FrameTcm1, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.Tcm_label_pol_z['font'] = myFont
        self.Tcm_label_pol_z.place(x=10,y=210)

        self.Tcm_entry_pol_z = ttk.Combobox(self.FrameTcm1, value = pol_list)
        self.Tcm_entry_pol_z['font'] = myFont
        self.Tcm_entry_pol_z.insert(0,"1")
        self.Tcm_entry_pol_z.place(x=250,y=210)

        self.Tcm_label_ts = Label(self.FrameTcm1,text="Time step (attosecond)",bg="gray",fg="black")
        self.Tcm_label_ts['font'] = myFont
        self.Tcm_label_ts.place(x=10,y=260)

        self.Tcm_entry_ts = Entry(self.FrameTcm1,textvariable= dt)
        self.Tcm_entry_ts['font'] = myFont
        self.Tcm_entry_ts.insert(0,"10")
        self.Tcm_entry_ts.place(x=250,y=260)

        self.Tcm_label_ns = Label(self.FrameTcm1,text="No of steps",bg="gray",fg="black")
        self.Tcm_label_ns['font'] = myFont
        self.Tcm_label_ns.place(x=10,y=310)

        self.Tcm_entry_ns = Entry(self.FrameTcm1,textvariable= Nt)
        self.Tcm_entry_ns['font'] = myFont
        self.Tcm_entry_ns.insert(0,"2000")
        self.Tcm_entry_ns.place(x=250,y=310)

        self.Tcm_label_note = Label(self.FrameTcm1,text="Note: This input creates the TD wavefunctions (required for TCM)",fg="black")
        self.Tcm_label_note['font'] = myFont
        self.Tcm_label_note.place(x=10,y=350)

        self.Tcm_Button = tk.Button(self.FrameTcm1, text="Back",bg='blue',fg='white',command=lambda:controller.show_frame(WorkManagerPage))
        self.Tcm_Button['font'] = myFont
        self.Tcm_Button.place(x=10,y=380)

        self.Tcm_TDInput_button = Button(self.FrameTcm1,text="Save Input",bg='blue',fg='white')
        self.Tcm_TDInput_button['font'] = myFont
        self.Tcm_TDInput_button.place(x=340,y=380)

        self.FrameTcm2 = tk.Frame(self)
        self.FrameTcm2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.FrameTcm2.configure(relief='groove')
        self.FrameTcm2.configure(borderwidth="2")
        self.FrameTcm2.configure(relief="groove")
        self.FrameTcm2.configure(cursor="fleur")

        self.FrameTcm2_label_path = Label(self.FrameTcm2,text="Frequency space density matrix",fg="blue")
        self.FrameTcm2_label_path['font'] = myFont
        self.FrameTcm2_label_path.place(x=150,y=10)

        self.Label_freqs = Label(self.FrameTcm2,text="Frequencies (in eV/a.u) ",bg="gray",fg="black")
        self.Label_freqs['font'] = myFont
        self.Label_freqs.place(x=10,y=60)

        self.TextBox_freqs = Text(self.FrameTcm2, height=10, width=65)
        self.TextBox_freqs['font'] = myFont
        self.TextBox_freqs.place(x=10,y=110)
        
        explanation = """Please type in the frequencies (in eV/a.u.) at which Fourier transform of density matrix is sought. For a list provide numbers separated by commas. For a range provide the details as <min value>-<max value>-<step size>"""
        
        #self.Label_expl = tk.Label(self.FrameTcm2, justify=tk., text=explanation).pack(side="left")
        #self.Label_expl = Label(self.FrameTcm2, justify=tk.LEFT, padx = 25, text= explanation, bg="gray",fg="black").pack(side="left")
        #self.Label_expl['font'] = myFont
        #self.Label_expl.place(x=10,y=60)

        #self.Tcm_label_note = Label(self.FrameTcm2,text="Please type in the frequencies (in eV/a.u.) at which Fourier transform of density matrix is sought. For a list provide numbers separated by commas. For a range provide the details as <min value>-<max value>-<step size>",bg="gray",fg="black")
        #self.Tcm_label_note['font'] = myFont
        #self.Tcm_label_note.place(x=10,y=300)

        self.buttonRetrieve = Button(self.FrameTcm2, text="Retrieve Freq",bg='blue',fg='white',command=lambda: retrieve_input())
        self.buttonRetrieve['font'] = myFont
        self.buttonRetrieve.place(x=10,y=380)

        self.buttonInputFdm = Button(self.FrameTcm2,text="View Input",bg='blue',fg='white', command=lambda:controller.show_frame(TextViewerPage))
        self.buttonInputFdm['font'] = myFont
        self.buttonInputFdm.place(x=200,y=380)
        
        FrameTcm2_Button1 = tk.Button(self.FrameTcm2, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(JobSubPage))
        FrameTcm2_Button1['font'] = myFont
        FrameTcm2_Button1.place(x=360,y=380)
        

        def retrieve_input():
            inputValues = self.TextBox_freqs.get("1.0", "end-1c")
            freqs = inputValues.split()

            freqs_lst = []
            for freq in freqs[0:]:
                freqs_lst.append(float(freq))

            # print(freqs_lst)

        def tcm_td_inp2dict():
            td_dict = rt.default_input
            td_dict['absorption_kick'][0] = float(strength.get())*float(self.ex.get())
            td_dict['absorption_kick'][1] = float(strength.get())*float(self.ey.get())
            td_dict['absorption_kick'][2] = float(strength.get())*float(self.ez.get())
            inp_list = [float(dt.get()),float(Nt.get())]
            td_dict['propagate'] = tuple(inp_list)
            return td_dict  

  
class TextViewerPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

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

        
        text_scroll.config(command= my_Text.yview)
    
         
        view = tk.Button(self, text="View Text",bg='blue',fg='white',command=lambda:[self.open_txt(my_Text)])
        view['font'] = myFont
        view.place(x=150,y=380)

        save = tk.Button(self, text="Save", bg= 'blue',fg='white',command=lambda:[self.save_txt(my_Text)])
        save['font'] = myFont
        save.place(x=320, y=380)

        back = tk.Button(self, text="Back",bg='blue',fg='white',command=lambda:[controller.show_frame(self.prev, WorkManagerPage, JobSubPage)])
        back['font'] = myFont
        back.place(x=15,y=380)

        # jobsub = tk.Button(self, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(JobSubPage))
        # jobsub['font'] = myFont
        # jobsub.place(x=800,y=380)

    def open_txt(self,my_Text):
        text_file_name = filedialog.askopenfilename(initialdir= user_path, title="Select File", filetypes=(("All Files", "*"),))
        self.current_file = text_file_name
        text_file = open(text_file_name, 'r')
        stuff = text_file.read()
        my_Text.insert(END,stuff)
        text_file.close()
    
    def save_txt(self,my_Text):
        text_file = self.current_file
        text_file = open(text_file,'w')
        text_file.write(my_Text.get(1.0, END))
        


#--------------------------------------------------------------------------------        


if __name__ == '__main__':
   
    
    app = AITG()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
