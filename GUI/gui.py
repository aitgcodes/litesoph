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
from pathlib import Path
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
from litesoph.io.IO import UserInput as ui
from litesoph.simulations.esmd import GroundState
from litesoph.simulations import engine
from litesoph.GUI.filehandler import *
from litesoph.GUI.navigation import Nav
#from litesoph.GUI.laserframe import Laser
#from litesoph.Pre_Processing.preproc import *





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

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        MainMenu(self)
        path=str(Path.home())
        Nav(self,path)
        
        window = Frame(self)
        window.grid(row=0, column=2)
        #window.pack(side="top", fill = "both", expand = True)
        window.grid_rowconfigure(700,weight=700)
        window.grid_columnconfigure(600,weight=400)
        
        self.frames = {}

        for F in (StartPage, WorkManagerPage, GroundStatePage, TimeDependentPage, Laser):
            frame = F(window,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky ="nsew")

        self.show_frame(StartPage)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def task_input(self,task):
        if task.get()  == "Ground State":
            self.show_frame(GroundStatePage)
        if task.get() == "Excited State":
            self.show_frame(TimeDependentPage)
        if task.get() == "Laser Masking":
            self.show_frame(Laser)
                  
    def gui_inp(self,task,**gui_dict):
        if task == 'gs':
            ui.user_param.update(gui_dict) # update the user parameters
            user_input = ui.user_param
            user_input['work_dir'] = user_path
            user_input['geometry'] = user_path+"/coordinate.xyz"
            engn = engine.choose_engine(user_input)
            GroundState(user_input, engn)
        if task == 'td':
            pass
              
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
        
        frame_1_label_1 = Label(frame,text="Manage Job(s)", bg="blue", fg="white")
        frame_1_label_1['font'] = myFont
        frame_1_label_1.grid(row=10, column=2, sticky=(W, E) ,columnspan=3,rowspan=2)

        label_1 = Label(mainframe,text="Welcome to LITESOPH", bg='#0052cc',fg='#ffffff')
        label_1['font'] = myFont
        #label_1.grid(row=0,column=1,sticky=(E,S))
        label_1.place(x=200,y=50)
        
        label_2 = Label(mainframe,text="Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena", bg='#0052cc',fg='#ffffff')
        label_2['font'] = l
        label_2.grid(row=1,column=1)
        #label_2.place(x=200,y=100)

        # create a canvas to show image on
        canvas_for_image = Canvas(mainframe, bg='gray', height=100, width=100, borderwidth=0, highlightthickness=0)
        #canvas_for_image.grid(row=30,column=0, sticky='nesw', padx=0, pady=0)
        canvas_for_image.place(x=30,y=5)

        # create image from image location resize it to 100X100 and put in on canvas
        image = Image.open('images/logo_litesoph.png')
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((100, 100), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open('images/project_create.png')
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = Button(mainframe,text="Start LITESOPH projects", bg="black",fg="white",command=lambda: controller.show_frame(WorkManagerPage))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        # create a canvas to show project list icon
        #canvas_for_project_open=Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        #canvas_for_project_open.place(x=20,y=300)

        #image_project_open = Image.open('images/project_open.png')
        #canvas_for_project_open.image = ImageTk.PhotoImage(image_project_open.resize((50,50), Image.ANTIALIAS))
        #canvas_for_project_open.create_image(0,0, image=canvas_for_project_open.image, anchor='nw')

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
        self.entry_path.insert(0,str(Path.home()))
        self.entry_path.place(x=200,y=10)

        self.label_proj = Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        self.entry_proj = Entry(self.Frame1,textvariable="proj_name")
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"graphene")
        self.entry_proj.place(x=200,y=70)
                
        self.button_project = Button(self.Frame1,text="Create",bg='#0052cc',fg='#ffffff',command=lambda:[self.retrieve_input(),projpath.create_path(self.projectpath,self.projectname)])
        self.button_project['font'] = myFont
        self.button_project.place(x=10,y=300)
      
        self.Frame1_Button_MainPage = Button(self.Frame1, text="Back to Main Page",bg='#0052cc',fg='#ffffff', command=lambda: controller.show_frame(StartPage))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=100,y=300)
        
        self.button_project = Button(self.Frame1,text="Go",bg='#0052cc',fg='#ffffff',command=lambda:[self.retrieve_input(),projpath.dir_exist(self.projectpath,self.projectname),os.chdir(self.projectpath+"/"+self.projectname)])
        #self.button_project = Button(self.Frame1,text="Go",bg='#0052cc',fg='#ffffff',command=lambda:[self.retrieve_input(),projpath.dir_exist(self.projectpath,self.projectname),os.chdir(user_path)])
        self.button_project['font'] = myFont
        self.button_project.place(x=270,y=300)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",bg='#0052cc',fg='#ffffff',command=lambda:[open_file(self.getprojectdirectory()),show_message(self.message_label,"Uploaded")])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        self.Frame2_label_2 = Label(self.Frame2, text="Geometry",bg='gray',fg='black')        
        self.Frame2_label_2['font'] = myFont
        self.Frame2_label_2.place(x=10,y=70)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",bg='#0052cc',fg='#ffffff',command=self.geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=70)

        self.label_proj = Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=130)

        task = ttk.Combobox(self.Frame2, values=["Ground State","Excited State","Laser Masking"])
        task.current(0)
        task['font'] = l
        task.place(x=200,y=130)
                       
        self.Frame2_label_3 = Label(self.Frame2, text="Plot Spectrum",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=190)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Plot",bg='#0052cc',fg='#ffffff',command=self.spectrum_show)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=190)

        #Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",bg='#0052cc',fg='#ffffff',command=lambda:[os.chdir(self.projectpath+"/"+self.projectname),controller.task_input(task)])
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",bg='#0052cc',fg='#ffffff',command=lambda:[controller.task_input(task)])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=300)

        self.Frame2_Button2 = tk.Button(self.Frame2, text="Job Submission",bg='#0052cc',fg='#ffffff',command=self.submit_job)
        self.Frame2_Button2['font'] = myFont
        self.Frame2_Button2.place(x=100,y=300)
    def dir_check(self):
        p = Path('/usr')         
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
        cmd=self.visn.vistool["name"] + " " + self.getprojectdirectory()+"/coordinate.xyz"
        os.system(cmd)
                
    def spectrum_show(self):
        plot_spectra()
        img =Image.open(self.getprojectdirectory()+'/spec.png')
        img.show()

    def submit_job(self):
        top1 = Toplevel()
        top1.geometry("700x600")
        top1.title("Job Handler for LITESOPH Calculations")
        cores_1 = StringVar()

        myFont = font.Font(family='Helvetica', size=15, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        sbj_label1 = Label(top1, text="Number of processors", bg='#0052cc', fg='#ffffff')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=50,y=20)
        sbj_entry1 = Entry(top1,textvariable="cores_1", width=20)
        sbj_entry1.insert(0," ")
        sbj_entry1['font'] = l
        sbj_entry1.place(x=400, y=20)
        #core = core_1.get()     
        sbj_button1 = Button(top1, text="LOCAL",bg='#0052cc', fg='#ffffff',command=lambda:[show_message(msg_label1,"Job Done"),self.submitjob_local()])
        sbj_button1['font'] = myFont
        sbj_button1.place(x=100, y=300)

        msg_label1 = Label(top1, text='', fg='#ffffff')
        msg_label1['font'] = myFont
        msg_label1.place(x=100,y=350)

        sbj_button2 = Button(top1, text="NETWORK",bg='#0052cc', fg='#ffffff',command=self.submitjob_network)
        sbj_button2['font'] = myFont
        sbj_button2.place(x=300, y=300)

        sbj_button3 = Button(top1, text="CLOSE", bg='#0052cc', fg='#ffffff',command=top1.destroy)
        sbj_button3['font'] = myFont
        sbj_button3.place(x=400,y=400)

        
    def submitjob_local(self):
        
        #print("gs calculation initiated...")
        #os.system("python gs.py")
        #os.system("mpirun -np {} python gs.py".format(processors))
        #print("Exited State calculation initiated...")
        #os.system("mpirun -np {} python td.py".format(processors))
        #print("spectrum calculation initiated...")
        #os.system("mpirun -np {} python spec.py".format(processors))
        #runpython(user_path+"/gs.py")
        #runpython(user_path+"/td.py")
        #runpython(user_path+"/spec.py")
        os.system('python gs.py')
        os.system('python td.py')
        os.system('python spec.py')
       
    def submitjob_network(self):
        pass

    def retrieve_input(self):
        self.projectpath = self.entry_path.get()
        self.projectname = self.entry_proj.get()

    def getprojectdirectory(self):
        global user_path
        user_path = self.projectpath+"/"+self.projectname
        return user_path


class GroundStatePage(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        h   = StringVar()
        nbands = StringVar()
        vacuum = StringVar()
        mode = StringVar()
        xc = StringVar()
        basis = StringVar()
        myFont = font.Font(family='Courier', size=10, weight ='bold')
        j=('Courier',20,'bold')
        k=('Courier',60,'bold')
        l=('Courier',20,'bold')
        n=font.Font(size=900)
       
        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))

        self.configure(bg="grey60")
        label_mode = Label(self,text = "Mode", font =myFont,bg="grey60",fg="gainsboro")
        label_mode.place(x=5,y=10)

        self.drop_mode =  ttk.Combobox(self, textvariable= mode, values=[ "lcao", "fd","pw","gaussian"])
        self.drop_mode.current(0)
        self.drop_mode['font'] = myFont
        self.drop_mode.place(x=250,y=10)

        label_ftype = Label(self, text= "Exchange Correlation", font =myFont,bg="grey60",fg="gainsboro")
        label_ftype.place(x=5,y=50)

        self.drop_ftype =  ttk.Combobox(self, textvariable= xc, values=["PBE", "LDA","B3LYP"])
        self.drop_ftype.current(0)
        self.drop_ftype['font'] = myFont
        self.drop_ftype.place(x=250, y=50)

        label_basis = Label(self, text= "Basis", font =myFont,bg="grey60",fg="gainsboro" )
        label_basis.place(x=5,y=100)

        self.drop_basis =  ttk.Combobox(self, textvariable= basis, values=["dzp","pvalence.dz","6-31+G*","6-31+G","6-31G*","6-31G","3-21G","cc-pvdz"])
        self.drop_basis.current(0)
        self.drop_basis['font'] = myFont
        self.drop_basis.place(x=250,y=100)

        label_spacing= Label(self, text= "Spacing (in a.u)", font =myFont,bg="grey60",fg="gainsboro"  )
        label_spacing.place(x=5,y=150)

        self.entry_spacing = ttk.Entry(self,textvariable= h)
        self.entry_spacing['font'] = myFont
        self.entry_spacing.insert(0,"0.3")
        self.entry_spacing.place(x= 250, y =150 )

        label_bands = Label(self, text= "Number of bands",  font =myFont,bg="grey60",fg="gainsboro"  )
        label_bands.place(x=5,y=200)

        self.entry_bands=ttk.Entry(self,textvariable= nbands)
        self.entry_bands['font']=myFont
        self.entry_bands.place(x=250,y=200)

        label_vacuum = Label(self,text="Vacuum size (in Angstrom)", font =myFont,bg="grey60",fg="gainsboro")
        label_vacuum.place(x=5,y=250)

        self.entry_vacuum=ttk.Entry(self,textvariable= vacuum)
        self.entry_vacuum['font'] = myFont
        self.entry_vacuum.insert(0,"6")
        self.entry_vacuum.place(x=250,y=250)
                
        enter = ttk.Button(self, text="GS Input", style="TButton", command=lambda:[controller.gui_inp('gs',**inp2dict()),messagebox.showinfo("Message", "Input for ground state calculation is Created")])
        enter.place(x=250,y=330)
        back_gpaw = ttk.Button(self, text="Back",style="TButton",command=lambda:controller.show_frame(WorkManagerPage))
        back_gpaw.place(x=450,y=330)
        
        def inp2dict():
            inp_dict = {
             'mode': mode.get(),
             'xc': xc.get(),
             'basis': basis.get(),
             'vacuum': vacuum.get(),
             'h': h.get(),
             'nbands' : nbands.get(),
             'properties': 'get_potential_energy()',
             'engine':'gpaw'
                     }          
            return inp_dict    
                
                 
class TimeDependentPage(Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        myFont = font.Font(family='Courier', size=30, weight ='bold')
        j=('Courier',20,'bold')
        k=('Courier',60,'bold')
        l=('Courier',20,'bold')
        n=font.Font(size=900)

    #    Frame.__init__(self, parent)
    #    myFont = font.Font(family='Courier', size=20, weight ='bold')
    #    j=font.Font(family ='Courier', size=20,weight='bold')
    #    k=font.Font(family ='Courier', size=40,weight='bold')
    #    l=font.Font(family ='Courier', size=15,weight='bold')

        self.configure(bg="grey60")

        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 25))
        gui_style.configure("BW.TLabel",foreground='black',background='gainsboro',font=('Helvetica', 18))
        gui_style.configure('K.TButton', foreground='black',background='gainsboro',font=('Helvetica', 8))

        label_strength = Label(self, text= "Laser strength (in a.u)",font=j,bg= "grey60",fg="gainsboro")
        label_strength.place(x=5,y=10)

        label_polarization = Label(self, text= "Electric polarization:",font=j,bg= "grey60",fg="gainsboro")
        label_polarization.place(x=5,y=50)

        label_pol_x = Label(self, text="Select the value of x", font=j,bg= "grey60",fg="gainsboro")
        label_pol_x.place(x=5,y=100)

        label_pol_y = Label(self, text="Select the value of y", font=j,bg= "grey60",fg="gainsboro")
        label_pol_y.place(x=5,y=150)

        label_pol_z = Label(self, text="Select the value of z", font=j,bg= "grey60",fg="gainsboro")
        label_pol_z.place(x=5,y=200)

        label_timestep = Label(self, text= "Propagation time step (in attosecond)",font=j,bg= "grey60",fg="gainsboro")
        label_timestep.place(x=5,y=250)

        label_steps=Label(self, text= "Total time steps",font=j,bg= "grey60",fg="gainsboro")
        label_steps.place(x=5,y=300)

        drop_strength =  ttk.Combobox(self, values=[ "1e-5", "1e-3"])
        drop_strength.current(0)
        drop_strength['font'] = l
        drop_strength.place(x=600,y=10)

        drop_pol_x =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_x.current(0)
        drop_pol_x['font'] = l
        drop_pol_x.place(x=600, y=100)

        drop_pol_y =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_y.current(0)
        drop_pol_y['font'] = l
        drop_pol_y.place(x=600, y=150)

        drop_pol_z =  ttk.Combobox(self, values=[ "0", "1"])
        drop_pol_z.current(0)
        drop_pol_z['font'] = l
        drop_pol_z.place(x=600, y=200)

        entry_dt = ttk.Entry(self,textvariable="dt")
        entry_dt['font']=l
        entry_dt.insert(0,"10")
        entry_dt.place(x=600, y=250 )

        entry_Nt = ttk.Entry(self,textvariable="Nt")
        entry_Nt['font']=l
        entry_Nt.insert(0,"2000")
        entry_Nt.place(x=600, y=300 )

        enter = ttk.Button(self, text="ES Input", style="TButton", command=lambda:[messagebox.showinfo("Message", "Input for Excited State calculation is Created"), esmd.tddft_input_file(drop_strength.get(), drop_pol_x.get(), drop_pol_y.get(), drop_pol_z.get(), entry_dt.get(), entry_Nt.get())])
        enter.place(x=300,y=350)

        back = ttk.Button(self, text="BACK",style="TButton",command=lambda:controller.show_frame(WorkManagerPage))
        back.place(x=500, y=350)



class Laser(Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1 = tk.Frame(self)

        inval = StringVar()
        pol_x = StringVar()
        pol_y = StringVar()
        pol_z = StringVar()
        fwhm = StringVar()
        freq = StringVar()
        ts = StringVar()
        ns = StringVar()

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        self.Frame1_label_path = Label(self.Frame1,text="Laser Masking",bg="gray",fg="black")
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=100,y=10)
       
        self.label_proj = Label(self.Frame1,text="Laser Strength",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        self.entry_proj = Entry(self.Frame1,textvariable= inval)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=70)
        
        self.label_pol = Label(self.Frame1, text= "Electric polarization:",bg= "grey",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.place(x=10,y=100)

        self.label_pol_x = Label(self.Frame1, text="Select the value of x", bg= "grey",fg="black")
        self.label_pol_x['font'] = myFont
        self.label_pol_x.place(x=10,y=140)

        self.entry_pol_x = Entry(self.Frame1,textvariable= pol_x)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=200,y=140)

        self.label_pol_y = Label(self.Frame1, text="Select the value of y", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=180)

        self.entry_pol_y = Entry(self.Frame1,textvariable= pol_y)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.place(x=200,y=180)

        self.label_pol_z = Label(self.Frame1, text="Select the value of z", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=220)

        self.entry_pol_z = Entry(self.Frame1,textvariable= pol_z)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.place(x=200,y=220)

        self.label_proj = Label(self.Frame1,text="FWHM",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= fwhm)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=260)

        self.label_proj = Label(self.Frame1,text="Frequency",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=300)

        self.entry_proj = Entry(self.Frame1,textvariable= freq)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=300)

        self.label_proj = Label(self.Frame1,text="time step",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=340)

        self.entry_proj = Entry(self.Frame1,textvariable= ts)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=340)
        
        self.label_proj = Label(self.Frame1,text="No of steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=380)

        self.entry_proj = Entry(self.Frame1,textvariable= ns)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=380)


        #self.button_project = Button(self.Frame1,text="Calculate",bg='#0052cc',fg='#ffffff',command=lambda:[laser_calc(**(inp2dict()))])
        #self.button_project['font'] = myFont
        #self.button_project.place(x=10,y=300)
        
        #def inp2dict():
            #laser_default = pre_proc()
            #inp_dict = laser_default.default_dict
            #print(inp_dict)
            #inp_dict['task'] = 'design'
            #inp_dict['design']['inval'] = inval.get()
            #inp_dict['design']['tin'] = tin.get()
            #inp_dict['design']['fwhm'] = fwhm.get()
            #print(inp_dict)
            #return inp_dict

        #def laser_calc(**gui_dict):
            #laser_default = pre_proc()
            #laser_dict = laser_default.default_dict
            #laser_dict.update(gui_dict)    #update input and task
            #d = unpack(laser_dict)
            #print(d)

            
            

        # self.Frame1_Button_MainPage = Button(self.Frame1, text="Back to Main Page",bg='#0052cc',fg='#ffffff', command=lambda: controller.show_frame(StartPage))
        # self.Frame1_Button_MainPage['font'] = myFont
        # self.Frame1_Button_MainPage.place(x=100,y=300)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.message_label = Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        self.Frame2_label_2 = Label(self.Frame2, text="Geometry",bg='gray',fg='black')        
        self.Frame2_label_2['font'] = myFont
        self.Frame2_label_2.place(x=10,y=70)

        # self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",bg='#0052cc',fg='#ffffff',command=self.geom_visual)
        # self.Frame2_Button_1['font'] = myFont
        # self.Frame2_Button_1.place(x=200,y=70)

        self.label_proj = Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=130)

        task = ttk.Combobox(self.Frame2, values=["Ground State","Spectrum","Excited State","Analysis"])
        task.current(0)
        task['font'] = l
        task.place(x=200,y=130)
                       
        self.Frame2_label_3 = Label(self.Frame2, text="Plot Spectrum",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=190)

        # self.Frame2_Button_1 = tk.Button(self.Frame2,text="Plot",bg='#0052cc',fg='#ffffff',command=self.spectrum_show)
        # self.Frame2_Button_1['font'] = myFont
        # self.Frame2_Button_1.place(x=200,y=190)

        Frame2_Button1 = tk.Button(self.Frame2, text="Back",bg='#0052cc',fg='#ffffff',command=lambda:controller.show_frame(WorkManagerPage))
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=300)

        # self.Frame2_Button2 = tk.Button(self.Frame2, text="Job Submission",bg='#0052cc',fg='#ffffff',command=self.submit_job)
        # self.Frame2_Button2['font'] = myFont
        # self.Frame2_Button2.place(x=100,y=300)

#--------------------------------------------------------------------------------        


if __name__ == '__main__':

    app = AITG()
    #app = ThemedTk(theme="arc")
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
