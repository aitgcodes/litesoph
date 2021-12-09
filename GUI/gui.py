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
#from litesoph.GUI.laserframe import Laser
from litesoph.Pre_Processing.preproc import *
from litesoph.simulations.GPAW.gpaw_template import RtLcaoTddft as rt
from litesoph.simulations.GPAW.spectrum import spectrum
from litesoph.lsio.IO import write22file
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

    def __init__(self, lsroot, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        MainMenu(self)
        path=str(pathlib.Path.home())
        Nav(self,path)
        
        window = Frame(self)
        window.grid(row=0, column=2)
        #window.pack(side="top", fill = "both", expand = True)
        window.grid_rowconfigure(700,weight=700)
        window.grid_columnconfigure(800,weight=400)
        
        self.lsroot = lsroot
        self.frames = {}

        for F in (StartPage, WorkManagerPage, GroundStatePage, TimeDependentPage, LaserDesignPage, PlotSpectraPage, JobSubPage, TcmPage):
            frame = F(window,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky ="nsew")

        self.show_frame(StartPage)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def task_input(self,sub_task):
        if sub_task.get()  == "Ground State":
            self.show_frame(GroundStatePage)
        if sub_task.get() == "Delta Kick":
            self.show_frame(TimeDependentPage)
        if sub_task.get() == "Gaussian Pulse":
            self.show_frame(LaserDesignPage)
        if sub_task.get() == "Spectrum":
            self.show_frame(PlotSpectraPage)
        if sub_task.get() == "Transition Contribution Map":
            self.show_frame(TcmPage)
                  
    def gui_inp(self,task,**gui_dict):
        
        if task == 'gs':
            ui.user_param.update(gui_dict) # update the user parameters
            dict_input = ui.user_param
            dict_input['directory'] = user_path
            dict_input['geometry'] = pathlib.Path(user_path) / "coordinate.xyz"
            engn = engine.choose_engine(dict_input)
            GroundState(dict_input, engn)
            write2status(str(user_path),'gs_inp','True')
            
        if task == 'td':
            rt.default_input.update(gui_dict)
            dict_input = rt.default_input
            RT_LCAO_TDDFT(dict_input, engine.EngineGpaw(),user_path)
            write2status(str(user_path),'td_inp','True')

    def createspec(self):
        spec = spectrum()
        spec_dict = spec.user_input
        spec_dict['moment_file'] = pathlib.Path(user_path) / 'dm.dat'
        spec_dict['spectrum_file'] = pathlib.Path(user_path) / 'spec.dat'
        spec.cal_photoabs_spectrum(spec_dict)

def write2status(path, key = None, value = None):
        stat_obj = Status()
        if key is None and value is None:
                write22file(path,'status.txt',stat_obj.status_template, stat_obj.status_dict)
        else :
                stat_obj.status_dict[key] = value
                write22file(path,'status.txt',stat_obj.status_template, stat_obj.status_dict)    
    
class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
              
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

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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
        self.entry_path.insert(0,str(pathlib.Path.home()))
        self.entry_path.place(x=200,y=10)

        self.label_proj = Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        self.entry_proj = Entry(self.Frame1,textvariable="proj_name")
        self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"graphene")
        self.entry_proj.place(x=200,y=70)
                
        self.button_project = Button(self.Frame1,text="Create New Project",bg='#0052cc',fg='#ffffff',command=lambda:[self.retrieve_input(),projpath.create_path(self.projectpath,self.projectname),os.chdir(self.projectpath+"/"+self.projectname),getprojectdirectory(self.projectpath,self.projectname)])
        self.button_project['font'] = myFont
        self.button_project.place(x=125,y=360)
      
        self.Frame1_Button_MainPage = Button(self.Frame1, text="Start Page",bg='#0052cc',fg='#ffffff', command=lambda: controller.show_frame(StartPage))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=10,y=360)
        
        self.button_project = Button(self.Frame1,text="Open Existing Project",bg='#0052cc',fg='#ffffff',command=lambda:[self.retrieve_input(),projpath.dir_exist(self.projectpath,self.projectname),os.chdir(self.projectpath+"/"+self.projectname),getprojectdirectory(self.projectpath,self.projectname)])
        self.button_project['font'] = myFont
        self.button_project.place(x=290,y=360)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",bg='#0052cc',fg='#ffffff',command=lambda:[open_file(user_path),show_message(self.message_label,"Uploaded")])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        
        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",bg='#0052cc',fg='#ffffff',command=self.geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=350,y=10)

        self.label_proj = Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]

        # Create a list of sub_task  
        Pre_task = ["Ground State","Geometry"]
        Sim_task = ["Delta Kick","Gaussian Pulse"]
        Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Transition Contribution Map","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]
        #Spec_task = ["Absorption Spectrum"]

        def pick_task(e):
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
                       
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",bg='#0052cc',fg='#ffffff',command=lambda:[controller.task_input(sub_task)])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=360)

        
    def init_visualization(self):
        visn = VISUAL()
        for tool in ["vmd","VMD","VESTA","vesta"]:
            line=subprocess.run(["which", tool], capture_output=True,text=True).stdout
            chkline = "no {} in".format(tool)
            if not chkline in line:
               visn.vistool["exists"] = True
               visn.vistool["name"] = tool
               break
        self.visn = visn

    def geom_visual(self):
        self.init_visualization()
        cmd=self.visn.vistool["name"] + " " + str(user_path) +"/coordinate.xyz"
        os.system(cmd)
  

    def retrieve_input(self):
        self.projectpath = self.entry_path.get()
        self.projectname = self.entry_proj.get()

def getprojectdirectory(path, name):
    global user_path
    user_path = pathlib.Path(path) / name
    return user_path

class GroundStatePage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
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
        
        Mainmode = ["lcao","fd","pw","gaussian"]

        # Create a list of sub_task  
        lcao_task = ["dzp","pvalence.dz","cc-pvdz"]
        fd_task = ["none"]
        pw_task = ["none"]
        gauss_task = ["6-31+G*","6-31+G","6-31G*","6-31G","3-21G"]

        def pick_task(e):
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

        self.label_pol_y = Label(self.Frame1, text="Spacing (in a.u)", bg= "grey",fg="black")
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
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)
        
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
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= spinpol, value = ["None","Yes"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=110)

        self.Frame2_note = Label(self.Frame2,text="multiplicity",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = Entry(self.Frame2,textvariable= multip)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=160)
  
        self.Frame2_note = Label(self.Frame2,text="Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0.0005")
        self.entry_proj.place(x=250,y=210)

        self.Frame2_note = Label(self.Frame2,text="maxtiter",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame2,textvariable= maxiter)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"300")
        self.entry_proj.place(x=250,y=260)
     
        self.Frame2_note = Label(self.Frame2,text="Bands",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=310)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= bands, value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=250,y=310)

        Frame2_Button1 = tk.Button(self.Frame2, text="Save and View Input",bg='#0052cc',fg='#ffffff', command=lambda:[controller.gui_inp('gs',**gs_inp2dict())])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(JobSubPage))
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

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
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
      
        self.label_proj = Label(self.Frame1,text="laser strength in a.u",bg="gray",fg="black")
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
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)

        

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.Frame2_note = Label(self.Frame2,text="Optional Input Parameters",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=10)
 
        Frame2_Button1 = tk.Button(self.Frame2, text="Save and view Input",bg='#0052cc',fg='#ffffff',command=lambda:[controller.gui_inp('td', **td_inp2dict())])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(JobSubPage))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=350,y=380)
   
        def td_inp2dict():
            td_dict = rt.default_input
            td_dict['absorption_kick'][0] = float(strength.get())*float(self.ex.get())
            td_dict['absorption_kick'][1] = float(strength.get())*float(self.ey.get())
            td_dict['absorption_kick'][2] = float(strength.get())*float(self.ez.get())
            inp_list = [float(dt.get()),float(Nt.get())]
            td_dict['propagate'] = tuple(inp_list)
            return td_dict

class LaserDesignPage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
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
        inval = StringVar()
        pol_x = StringVar()
        pol_y = StringVar()
        pol_z = StringVar()
        fwhm = StringVar()
        freq = StringVar()
        ts = StringVar()
        ns = StringVar()
        tin = StringVar()

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
        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= pol_x, value = pol_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"0")
        self.entry_pol_x.place(x=250,y=60)

        self.label_pol_y = Label(self.Frame1, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=110)
    
        self.entry_pol_y = ttk.Combobox(self.Frame1,textvariable= pol_y, value = pol_list)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.insert(0,"0")
        self.entry_pol_y.place(x=250,y=110)

        self.label_pol_z = Label(self.Frame1, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=160)
 
        self.entry_pol_z = ttk.Combobox(self.Frame1,textvariable= pol_z, value = pol_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"0")
        self.entry_pol_z.place(x=250,y=160)

        self.label_proj = Label(self.Frame1,text="Frequency in eV",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame1,textvariable= freq)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=210)

        self.label_proj = Label(self.Frame1,text="Time step in attosecond ",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= ts)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"10")
        self.entry_proj.place(x=250,y=260)
        
        self.label_proj = Label(self.Frame1,text="Number of Steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= ns)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"2000")
        self.entry_proj.place(x=250,y=310)
 
        Frame1_Button1 = tk.Button(self.Frame1, text="Back",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=10,y=380)
        
        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.label_proj = Label(self.Frame2,text="Time Origin (tin)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame2,textvariable= tin)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=250,y=60)

        self.label_proj = Label(self.Frame2,text="Pulse Amplitute at tin",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=110)
 
        inval_list = ["-8", "-9"]
        self.entry_pol_z = ttk.Combobox(self.Frame2,textvariable= inval, value = inval_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"-8")
        self.entry_pol_z.place(x=250,y=110)

        #self.entry_proj = Entry(self.Frame2,textvariable= inval)
        #self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"0")
        #self.entry_proj.place(x=250,y=110)

        self.label_proj = Label(self.Frame2,text="Laser Strength",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=160)
    
        instr = ["1e-5","1e-3"]
        self.entry_proj = ttk.Combobox(self.Frame2,textvariable= strength, value = instr)
        self.entry_proj['font'] = myFont
        self.entry_proj.current(0)
        self.entry_proj.place(x=250,y=160)

        self.label_proj = Label(self.Frame2,text="Full Width Half Max (FWHM in eV)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= fwhm)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=250,y=210)

        self.button_project = Button(self.Frame2,text="Laser Design",bg='#0052cc',fg='#ffffff',command=lambda:[laser_calc(**(inp2dict()))])
        self.button_project['font'] = myFont
        self.button_project.place(x=10,y=380)        
 
        Frame2_Button1 = tk.Button(self.Frame2, text="Save and View Input",bg='#0052cc',fg='#ffffff')
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=180,y=380)
        
        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(JobSubPage))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=400,y=380)
        
        def inp2dict():
            laser_default = pre_proc()
            inp_dict = laser_default.default_dict
            inp_dict['task'] = 'design'
            inp_dict['design']['inval'] = loginval.get()
            #inp_dict['design']['tin'] = tin.get()
            inp_dict['design']['fwhm'] = fwhm.get()
            return inp_dict

        def laser_calc(**gui_dict):
            laser_default = pre_proc()
            laser_dict = laser_default.default_dict
            laser_dict.update(gui_dict)    #update input and task
            d = unpack(laser_dict)

class PlotSpectraPage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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

        self.Frame2_Button_1 = tk.Button(self.Frame,text="Plot",bg='#0052cc',fg='#ffffff', command=lambda:[controller.createspec(),self.spectrum_show(self.returnaxis())])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=250,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
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
         

    def spectrum_show(self, axis):
        
        plot_spectra(int(axis))
        path = pathlib.Path(user_path) / "spec.png"
        img =Image.open(path)
        img.show()

class JobSubPage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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

        sbj_label1 = Label(self, text="LITESOPH Job Submission", bg='#0052cc', fg='#ffffff')
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

        sbj_button1 = Button(self, text="Run Local",bg='#0052cc', fg='#ffffff',command=lambda:[self.submitjob_local(sbj_entry1.get()),show_message(self.msg_label1,"Job Done")])
        sbj_button1['font'] = myFont
        sbj_button1.place(x=600, y=60)

        self.msg_label1 = Label(self, text='', fg='#ffffff')
        self.msg_label1['font'] = myFont
        self.msg_label1.place(x=600,y=100)

        back = tk.Button(self, text="Back to main page",bg='#0052cc',fg='#ffffff',command=lambda:[self.deletelabel(self.msg_label1),controller.show_frame(WorkManagerPage)])
        back['font'] = myFont
        back.place(x=600,y=400)
              

    def deletelabel(self,label):
        label.destroy()
         
    def submitjob_local(self, processors):
        
        gs_check = search_string(str(user_path), 'status.txt' , 'gs_inp = True')
        td_check = search_string(str(user_path), 'status.txt' , 'td_inp = True')
        self.job_select(gs_check,td_check,processors)
        
    def job_select(self,gs_check, td_check, processors):
        from litesoph.simulations.run_local import run_local
        if gs_check is False and td_check is False:
            show_message(self.msg_label1, "Input files not found")

        if gs_check is True and td_check is False:
            if processors == "1" :
                result = run_local('gs.py',user_path)
                show_message(self.msg_label1,"Job Done")               
            else:
                result = run_local('gs.py',user_path,int(processors))
                        
        if gs_check is True and td_check is True:
            if processors == "1" :
                result = run_local('td.py',user_path)
                show_message(self.msg_label1,"Job Done")               
            else:
                result = run_local('td.py',user_path,int(processors))
                  

    def submitjob_network(self):

        pass

class TcmPage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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

        self.FrameTcm1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.FrameTcm1.configure(relief='groove')
        self.FrameTcm1.configure(borderwidth="2")
        self.FrameTcm1.configure(relief="groove")
        self.FrameTcm1.configure(cursor="fleur")

        self.FrameTcm1_label_path = Label(self.FrameTcm1,text="Input parameters for TD calculations",bg="gray",fg="black")
        self.FrameTcm1_label_path['font'] = myFont
        self.FrameTcm1_label_path.place(x=10,y=10)

        self.label_strength = Label(self.FrameTcm1,text="laser strength (in a.u)",bg="gray",fg="black")
        self.label_strength['font'] = myFont
        self.label_strength.place(x=10,y=70)

        inval = ["1e-5","1e-3"]
        self.Tcm_entry_strength = ttk.Combobox(self.FrameTcm1, value = inval)
        self.Tcm_entry_strength['font'] = myFont
        self.Tcm_entry_strength.insert(0,"1e-5")
        self.Tcm_entry_strength.place(x=200,y=70)

        self.Tcm_label_pol_x = Label(self.FrameTcm1, text="Select the value of x", bg= "grey",fg="black")
        self.Tcm_label_pol_x['font'] = myFont
        self.Tcm_label_pol_x.place(x=10,y=150)

        pol_list = ["0","1"]
        self.Tcm_entry_pol_x = ttk.Combobox(self.FrameTcm1, value = pol_x)
        self.Tcm_entry_pol_x['font'] = myFont
        self.Tcm_entry_pol_x.insert(0,"0")
        self.Tcm_entry_pol_x.place(x=200,y=150)

        self.Tcm_label_pol_y = Label(self.FrameTcm1, text="Select the value of y", bg= "grey",fg="black")
        self.Tcm_label_pol_y['font'] = myFont
        self.Tcm_label_pol_y.place(x=10,y=190)

        
        self.Tcm_entry_pol_y = ttk.Combobox(self.FrameTcm1, value = pol_y)
        self.Tcm_entry_pol_y['font'] = myFont
        self.Tcm_entry_pol_y.insert(0,"0")
        self.Tcm_entry_pol_y.place(x=200,y=190)

        self.Tcm_label_pol_z = Label(self.FrameTcm1, text="Select the value of z", bg= "grey",fg="black")
        self.Tcm_label_pol_z['font'] = myFont
        self.Tcm_label_pol_z.place(x=10,y=230)

        self.Tcm_entry_pol_z = ttk.Combobox(self.FrameTcm1, value = pol_z)
        self.Tcm_entry_pol_z['font'] = myFont
        self.Tcm_entry_pol_z.insert(0,"1")
        self.Tcm_entry_pol_z.place(x=200,y=230)

        self.Tcm_label_ts = Label(self.FrameTcm1,text="dt (in attosecond) ",bg="gray",fg="black")
        self.Tcm_label_ts['font'] = myFont
        self.Tcm_label_ts.place(x=10,y=280)

        self.Tcm_entry_ts = Entry(self.FrameTcm1,textvariable= dt)
        self.Tcm_entry_ts['font'] = myFont
        self.Tcm_entry_ts.insert(0,"10")
        self.Tcm_entry_ts.place(x=200,y=280)

        self.Tcm_label_ns = Label(self.FrameTcm1,text="No of steps",bg="gray",fg="black")
        self.Tcm_label_ns['font'] = myFont
        self.Tcm_label_ns.place(x=10,y=320)

        self.Tcm_entry_ns = Entry(self.FrameTcm1,textvariable= Nt)
        self.Tcm_entry_ns['font'] = myFont
        self.Tcm_entry_ns.insert(0,"2000")
        self.Tcm_entry_ns.place(x=200,y=320)

        self.Tcm_label_note = Label(self.FrameTcm1,text="Note: This input creates the TD wavefunctions (required for TCM)",bg="gray",fg="black")
        self.Tcm_label_note['font'] = myFont
        self.Tcm_label_note.place(x=10,y=370)

        self.Tcm_TDInput_button = Button(self.FrameTcm1,text="Create TDInput",bg="blue",fg="black")
        self.Tcm_TDInput_button['font'] = myFont
        self.Tcm_TDInput_button.place(x=200,y=400)

        self.FrameTcm2 = tk.Frame(self)
        self.FrameTcm2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.FrameTcm2.configure(relief='groove')
        self.FrameTcm2.configure(borderwidth="2")
        self.FrameTcm2.configure(relief="groove")
        self.FrameTcm2.configure(cursor="fleur")

        self.FrameTcm2_label_path = Label(self.FrameTcm2,text="Frequency space density matrix",bg="gray",fg="black")
        self.FrameTcm2_label_path['font'] = myFont
        self.FrameTcm2_label_path.place(x=100,y=10)

        self.Label_freqs = Label(self.FrameTcm2,text="Frequencies (in eV) ",bg="gray",fg="black")
        self.Label_freqs['font'] = myFont
        self.Label_freqs.place(x=10,y=100)

        self.TextBox_freqs = Text(self.FrameTcm2, height=7, width=10)
        self.TextBox_freqs['font'] = myFont
        self.TextBox_freqs.place(x=200,y=100)

        self.buttonRetrieve = Button(self.FrameTcm2, height=2, width=20, text="Retrieve Frequencies",bg='#0052cc',fg='#ffffff',command=lambda: retrieve_input())
        self.buttonRetrieve['font'] = myFont
        self.buttonRetrieve.place(x=320,y=150)

        self.buttonInputFdm = Button(self.FrameTcm2,text="Create Input files for TCM plot",bg='#0052cc',fg='#ffffff')
        self.buttonInputFdm['font'] = myFont
        self.buttonInputFdm.place(x=10,y=300)


        FrameTcm2_Button1 = tk.Button(self.FrameTcm2, text="Back to Work Manager Page",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
        FrameTcm2_Button1['font'] = myFont
        FrameTcm2_Button1.place(x=10,y=400)
        

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


#--------------------------------------------------------------------------------        


if __name__ == '__main__':
    
    app = AITG()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
