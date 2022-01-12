from tkinter import *                    # importing tkinter, a standart python interface for gui.
from tkinter import ttk                  # importing ttk which is used for styling widgets.
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox

import tkinter.font as font              # importing tkinter fonts to give sizes to the fonts used in the widgets.
import subprocess                        # importing subprocess to run command line jobs as in terminal.
from  PIL import Image,ImageTk
import tkinter as tk

import os
import pathlib 
from configparser import ConfigParser, NoOptionError

from matplotlib.pyplot import show

#---LITESOPH modules
from litesoph import check_config
from litesoph.gui.menubar import MainMenu
from litesoph.gui.spec_plot import plot_spectra, plot_files
from litesoph.lsio.IO import UserInput as ui
from litesoph.simulations.esmd import RT_LCAO_TDDFT, TCM, GroundState, Spectrum
from litesoph.simulations import engine
from litesoph.gui.filehandler import Status,file_check, open_file,show_message
from litesoph.gui.navigation import Nav
from litesoph.gui.filehandler import Status
from litesoph.simulations.choose_engine import choose_engine
from litesoph.simulations.gpaw.gpaw_template import write_laser
from litesoph.utilities.job_submit import JobSubmit


home = pathlib.Path.home()

TITLE_FONT = ("Helvetica", 18, "bold")

class AITG(Tk):

    def __init__(self, lsconfig: ConfigParser, *args, **kwargs):
        super().__init__()

        self.mainmenu = MainMenu(self)
        self.lsconfig = lsconfig
        self.lsroot = check_config(self.lsconfig, "lsroot")
        self.directory = pathlib.Path(self.lsconfig.get("project_path", "lsproject", fallback=str(home)))
    
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=6)
       
        self.nav = None
        self.refresh_nav(self.directory)
        
        self.check = None
        self.window = Frame(self)
        self.window.grid(row=0, column=1)
        
        self.window.grid_rowconfigure(700,weight=700)
        self.window.grid_columnconfigure(800,weight=400)  

        self.frames = {}
        self.task = None
        self.show_frame(StartPage)
    
    
    def status_init(self):
        self.status = Status(self.directory)
        
    
    def show_frame(self, frame, prev = None, next = None,refresh=True, **kwargs):
        
        if frame in self.frames.keys() and refresh is False:
            frame = self.frames[frame]
            frame.tkraise()
        else:
            int_frame = frame(self.window, self, prev, next, **kwargs)
            self.frames[frame]= int_frame
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

    def task_input(self,sub_task, task_check):
        if task_check is True:
            if sub_task.get()  == "Ground State":
               self.show_frame(GroundStatePage, WorkManagerPage, JobSubPage)
            #    path1 = projpath.create_folder(self.directory, "GS")
            #    os.chdir(path1)
            if sub_task.get() == "Geometry Optimisation":
               self.show_frame(GeomOptPage, WorkManagerPage, JobSubPage)
            if sub_task.get() == "Delta Kick":           
               self.show_frame(TimeDependentPage, WorkManagerPage, JobSubPage)
            #    path = projpath.create_folder(self.directory, "Spectrum")
            #    os.chdir(path)  
            if sub_task.get() == "Gaussian Pulse":
               self.show_frame(LaserDesignPage, WorkManagerPage, JobSubPage)
            #    path = projpath.create_folder(self.directory, "Pulse")
            #    os.chdir(path)
            if sub_task.get() == "Spectrum":
               self.show_frame(PlotSpectraPage, WorkManagerPage, JobSubPage)
            if sub_task.get() == "Dipole Moment and Laser Pulse":
               self.show_frame(DmLdPage)
            if sub_task.get() == "Kohn Sham Decomposition":
               self.show_frame(TcmPage, WorkManagerPage, JobSubPage)                
        
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
        path1 = pathlib.PurePath(controller.lsroot) / "litesoph" / "gui" / "images"

        image = Image.open(str(pathlib.Path(path1) / "logo_ls.jpg"))
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((125, 125), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open(str(pathlib.Path(path1) / "project_create.png"))
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = Button(mainframe,text="Start LITESOPH Project", activebackground="#78d6ff",command=lambda: controller.show_frame(WorkManagerPage))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        #button_open_project = Button(mainframe,text="About LITESOPH",fg="white")
        button_open_project = Button(mainframe,text="About LITESOPH")
        button_open_project['font'] = myFont
        button_open_project.place(x=80,y=300)


class WorkManagerPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

        self.proj_path = StringVar()
        self.proj_name = StringVar()
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

        self.entry_path = Entry(self.Frame1,textvariable=self.proj_path)
        self.entry_path['font'] = myFont
        self.entry_path.delete(0, END)
        self.proj_path.set(self.controller.directory)
        self.entry_path.place(x=200,y=10)     

        self.label_proj = Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)
        
        self.entry_proj = Entry(self.Frame1,textvariable=self.proj_name)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=70)
        self.entry_proj.delete(0, END)
                
        self.button_project = Button(self.Frame1,text="Create New Project",activebackground="#78d6ff",command=lambda:[self.create_project(),self.controller.refresh_nav(self.controller.directory), self.controller.status_init()])
        self.button_project['font'] = myFont
        self.button_project.place(x=125,y=380)
      
        self.Frame1_Button_MainPage = Button(self.Frame1, text="Start Page",activebackground="#78d6ff", command=lambda: controller.show_frame(StartPage))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=10,y=380)
        
        self.button_project = Button(self.Frame1,text="Open Existing Project",activebackground="#78d6ff",command=lambda:[self.open_project(),self.update_dirPath(),self.controller.refresh_nav(self.controller.directory),self.controller.status_init()])
        self.button_project['font'] = myFont
        self.button_project.place(x=290,y=380)
        
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

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",activebackground="#78d6ff",command=lambda:[open_file(self.controller.directory),show_message(self.message_label,"Uploaded")])
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        
        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",activebackground="#78d6ff",command=self.geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=350,y=10)

        self.label_proj = Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

        MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]

        # Create a list of sub_task
       
        Pre_task = ["Ground State","Geometry Optimisation"]
        Sim_task = ["Delta Kick","Gaussian Pulse"]
        Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]
        
        
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
        task.set("--choose job task--")
        task['font'] = myFont
        task.place(x=200,y=70)
        task.bind("<<ComboboxSelected>>", pick_task)
        task['state'] = 'readonly'

        self.Frame2_label_3 = Label(self.Frame2, text="Sub Task",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=130)
          
        sub_task = ttk.Combobox(self.Frame2, width= 30, value = [" "])
        sub_task['font'] = myFont
        sub_task.current(0)
        sub_task.place(x=200,y=130)
        sub_task['state'] = 'readonly'   
           
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",activebackground="#78d6ff",command=lambda:[controller.task_input(sub_task,self.task_check(sub_task))])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)
    
    def change_directory(self,path):
        self.controller.directory = pathlib.Path(path)
        os.chdir(self.controller.directory) 

    def update_dirPath(self):
        self.proj_path.set(self.controller.directory.parent)
        self.entry_path.config(textvariable=self.proj_path)
        self.proj_name.set(self.controller.directory.name)
        self.entry_proj.config(textvariable=self.proj_name)

    def open_project(self):
        project_path = filedialog.askdirectory()
        self.change_directory(project_path)
        
    def create_project(self):
        project_path = pathlib.Path(self.entry_path.get()) / self.entry_proj.get()
        try:
            project_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            messagebox.showinfo("Message", f"project:{project_path} already exists, please open the existing project")
        else:
            messagebox.showinfo("Message", f"project:{project_path} is created successfully")
            self.change_directory(project_path)

    def geom_visual(self):
        cmd = check_config(self.controller.lsconfig,"vis")+ " "+"coordinate.xyz"
        try:
           p = subprocess.run(cmd.split(),capture_output=True, cwd=self.controller.directory)
        except:
            print("Unable to invoke vmd. Command used to call vmd '{}'. supply the appropriate command in ~/lsconfig.ini".format(cmd.split()[0]))

    

    def task_check(self,sub_task):
        self.st_var = self.controller.status
        
        if sub_task.get()  == "Ground State":
            path = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            if path.exists() is True:
                return True
            else:
                messagebox.showerror(message= "Upload geometry file")
        # elif sub_task.get() == "Delta Kick":
        #     if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
        #         return True
        #     else:
        #         messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")       
        # elif sub_task.get() == "Gaussian Pulse":
        #     if self.st_var.check_status('gs_inp', 1) is True and self.st_var.check_status('gs_cal',1) is True:
        #         return True
        #     else:
        #         messagebox.showerror(message=" Ground State Calculations not done. Please select Ground State under Preprocessing first.")
        # elif sub_task.get() == "Spectrum":
        #     if self.st_var.check_status('gs_cal', 1) is True:
        #         if self.st_var.check_status('td_cal',1) is True or self.st_var.check_status('td_cal',2) is True:
        #             return True
        #     else:
        #         messagebox.showerror(message=" Please complete Ground State and Delta kick calculation.")
        # elif sub_task.get() == "Dipole Moment and Laser Pulse":
        #     if self.st_var.check_status('gs_cal', 1) is True and self.st_var.check_status('td_cal',2) is True:
        #         return True
        #     else:
        #         messagebox.showerror(message=" Please complete Ground State and Gaussian Pulse calculation.")
        # else:
        return True

    

class GroundStatePage(Frame):
  
    Mainmode = ["nao","fd","pw","gaussian"]
    nao_task = ["dzp","pvalence.dz"]
    fd_task = [""]
    pw_task = [""]
    gauss_task = ["6-31G","STO-2G","STO-3G","STO-6G","3-21G","3-21G*","6-31G*","6-31G**","6-311G","6-311G*","6-311G**","cc-pVDZ","aug-cc-pvtz"]
    octgp_box = ["Parallelepiped","Minimum", "Sphere", "Cylinder"]
    nw_box = ["None"]
    gp_box = ["Parallelepiped"]
    xc_gp = ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"]
    xc_nw = ["acm","b3lyp","beckehandh","Hfexch","pbe0","becke88","xpbe96","bhlyp","cam-s12g","cam-s12h","xperdew91","pbeop"]
    xc_oct1 = ["lda_x_1d+lda_e_1d"]
    xc_oct2 = ["lda_x_2d+lda_c_2d_amgb"]
    xc_oct3 = ["lda_x+lda_e_pz_mod"]
    dxc_oct = ["1","2","3"]
    fnsmear = ["semiconducting","fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"]
    eignsolv = ["rmmdiis","plan","cg","cg_new"]

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        self.job = None
        
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
        
        self.mode = StringVar()
        self.xc = StringVar()
        self.basis = StringVar()
        self.charge = StringVar()
        self.maxiter = IntVar()
        self.shape = StringVar()
        self.spinpol = StringVar()
        self.multip = StringVar()
        self.h   = StringVar()
        self.nbands = StringVar()
        self.vacuum = StringVar()
        self.energy = DoubleVar()
        self.density = DoubleVar()
        self.bands = StringVar()
        self.theory = StringVar()
        self.tolerances = StringVar()
        self.dimension = StringVar()
        self.lx = StringVar()
        self.ly = StringVar()
        self.lz = StringVar()
        self.r = StringVar()
        self.l = StringVar()
        self.dxc = StringVar()
        self.mix = StringVar()
        self.eigen = StringVar()
        self.smear = StringVar()
        self.smearfn = StringVar()
        self.unitconv = StringVar()

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
        
        def pick_task(e):
            if task.get() == "nao":
                sub_task.config(value = self.nao_task)
                sub_task.current(0)
                box_shape.config(value = self.gp_box)
                box_shape.current(0)
                self.gpaw_frame()
            if task.get() == "fd":
                sub_task.config(value = self.fd_task)
                sub_task.current(0)
                box_shape.config(value = self.octgp_box)
                box_shape.set("--choose box--")
            if task.get() == "pw":
                sub_task.config(value = self.pw_task)
                sub_task.current(0)
                box_shape.config(value = self.gp_box)
                box_shape.current(0)
                self.gpaw_frame()
            if task.get() == "gaussian":
                sub_task.config(value = self.gauss_task)
                sub_task.current(0)
                box_shape.config(value = self.nw_box)
                box_shape.current(0)
                self.nwchem_frame()
            

        task = ttk.Combobox(self.Frame1, textvariable = self.mode, values= self.Mainmode)
        task.set("--choose mode--")
        task['font'] = myFont
        task.place(x=280,y=60)
        task.bind("<<ComboboxSelected>>", pick_task)
        task['state'] = 'readonly'

        self.Frame2_label_3 = Label(self.Frame1, text="Basis",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=110)
          
        sub_task = ttk.Combobox(self.Frame1, textvariable= self.basis, value = [" "])
        sub_task.current(0)
        sub_task['font'] = myFont
        sub_task.place(x=280,y=110)
        sub_task['state'] = 'readonly'

        self.label_pol_y = Label(self.Frame1, text="Charge", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=160)
    
        self.entry_proj = Entry(self.Frame1,textvariable= self.charge)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=280,y=160)

        self.label_pol_z = Label(self.Frame1, text="Maximum SCF iteration", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=210)
 
        entry = Entry(self.Frame1,textvariable= self.maxiter)
        entry['font'] = myFont
        entry.delete(0,END)
        entry.insert(0,"300")
        entry.place(x=280,y=210)

        self.Frame2_note = Label(self.Frame1,text="Energy Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1, width= 10, textvariable= self.energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"5.0e-7")
        self.entry_proj.place(x=280,y=260)
 
        unit = ttk.Combobox(self.Frame1,width=5, textvariable= self.unitconv , value = ["eV","au","Ha","Ry"])
        unit.current(0)
        unit['font'] = myFont
        unit.place(x=380,y=260)
        unit['state'] = 'readonly'
       
        self.label_proj = Label(self.Frame1,text="Box Shape",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)
    
        def pick_frame(e):
            if box_shape.get() == "Parallelepiped":
                if task.get() == "fd":
                    self.gp2oct()
            if box_shape.get() == "Minimum": 
                self.oct_minsph_frame()
                self.octopus_frame()
            if box_shape.get() == "Sphere":
                self.oct_minsph_frame()
                self.octopus_frame()
            if box_shape.get() == "Cylinder": 
                self.oct_cyl_frame()
                self.octopus_frame()

        box_shape = ttk.Combobox(self.Frame1, textvariable= self.shape, value = [" "])
        box_shape.current(0)
        box_shape['font'] = myFont
        box_shape.place(x=280,y=310)
        box_shape.bind("<<ComboboxSelected>>", pick_frame)
        box_shape['state'] = 'readonly'
       
        #self.Frame7 = tk.Frame(self)
        #self.Frame7.place(relx=0.1, rely=0.88, relheight=0.12, relwidth=0.492)

        #self.Frame7.configure(relief='groove')
        #self.Frame7.configure(borderwidth="2")
        #self.Frame7.configure(relief="groove")
        #self.Frame7.configure(cursor="fleur")
 
        Button1 = tk.Button(self.Frame1, text="Back",activebackground="#78d6ff",command=lambda:[self.back_button()])
        Button1['font'] = myFont
        Button1.place(x=10,y=380)
      
        self.Frame6 = tk.Frame(self)
        self.Frame6.place(relx=0.5, rely=0.87, relheight=0.13, relwidth=0.492)

        self.Frame6.configure(relief='groove')
        self.Frame6.configure(borderwidth="2")
        self.Frame6.configure(relief="groove")
        self.Frame6.configure(cursor="fleur")

        Frame2_Button3 = tk.Button(self.Frame6, text="View Input",activebackground="#78d6ff",command=lambda:[self.view_button()])
        Frame2_Button3['font'] = myFont
        Frame2_Button3.place(x=10,y=10)

        Frame1_Button1 = tk.Button(self.Frame6, text="Save Input",activebackground="#78d6ff",command=lambda:[self.save_button()])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=200,y=10)

        self.label_msg = Label(self.Frame6,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=300,y=12.5)

        Frame2_Button2 = tk.Button(self.Frame6, text="Run Job",activebackground="#78d6ff",command=lambda:[self.run_job_button()])
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=380,y=10)
 
    def gp2oct(self):
        check = messagebox.askyesno(message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
        if check is True:
            self.gpaw_frame()
        else:
            self.oct_ppl_frame()
            self.octopus_frame()
       
    def back_button(self):
        self.controller.show_frame(WorkManagerPage)
              
            
    def gpaw_frame(self):  
 
        myFont = font.Font(family='Helvetica', size=10, weight='bold') 
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.01, relheight=0.87, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.Frame2_note = Label(self.Frame2,text="Exchange Corelation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=60)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.xc, value = self.xc_gp)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=60)
        self.entry_pol_x['state'] = 'readonly'

        self.label_proj = Label(self.Frame2,text="Spacing (in Ang)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=110)

        self.entry_proj = Entry(self.Frame2,textvariable= self.h)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=280,y=110)
        
        self.Frame2_note = Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.spinpol, value = ["None","True"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=160)
        self.entry_pol_x['state'] = 'readonly'
 
        self.Frame2_note = Label(self.Frame2,text="Number of Bands",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= self.nbands)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.place(x=280,y=210)

        self.Frame2_note = Label(self.Frame2,text="Vacuum size (in Ang)",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame2,textvariable= self.vacuum)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"6")
        self.entry_proj.place(x=280,y=260)
     
        self.Frame2_note = Label(self.Frame2,text="Band Occupancy",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=310)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.bands, value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=310)
        self.entry_pol_x['state'] = 'readonly'
        

    def nwchem_frame(self):   

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
 
        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.01, relheight=0.87, relwidth=0.492)
        
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
        
        self.Frame2_note = Label(self.Frame2,text="Exchange Corelation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=60)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.xc, value = self.xc_nw)
        self.entry_pol_x.current(4)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=60)
        self.entry_pol_x['state'] = 'readonly'

        #self.label_proj = Label(self.Frame2,text="Theory",bg="gray",fg="black")
        #self.label_proj['font'] = myFont
        #self.label_proj.place(x=10,y=60)
        
        #self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.theory, value = ["scf","dft"])
        #self.entry_pol_x.current(1)
        #self.entry_pol_x['font'] = myFont
        #self.entry_pol_x.place(x=280,y=60)
        #self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = Label(self.Frame2,text="Density Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=110)

        self.entry_proj = Entry(self.Frame2,textvariable= self.density)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"1.0e-5")
        self.entry_proj.place(x=280,y=110)

        self.Frame2_note = Label(self.Frame2,text="Multiplicity",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = Entry(self.Frame2,textvariable= self.multip)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"1")
        self.entry_proj.place(x=280,y=160)

        self.Frame2_note = Label(self.Frame2,text="Tolerance",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.tolerances, value = ["tight","accCoul","radius"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=210)
        self.entry_pol_x['state'] = 'readonly'
        

    def oct_ppl_frame(self):

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
   
        self.note = Label(self.Frame3,text="Length of Box (lx, ly, lz)",bg="gray",fg="black")
        self.note['font'] = myFont
        self.note.place(x=10,y=10)
 
        #self.note1 = Label(self.Frame3,text="lx",bg="gray",fg="black")
        #self.note1['font'] = myFont
        #self.note1.place(x=10,y=60)
       
        self.entry1 = Entry(self.Frame3,width= 7, textvariable= self.lx)
        self.entry1['font'] = myFont
        self.entry1.delete(0,END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=110,y=60)
 
        #self.note2 = Label(self.Frame3,text="ly",bg="gray",fg="black")
        #self.note2['font'] = myFont
        #self.note2.place(x=130,y=60)

        self.entry2 = Entry(self.Frame3, width= 7, textvariable= self.ly)
        self.entry2['font'] = myFont
        self.entry2.delete(0,END)
        self.entry2.insert(0,"0")
        self.entry2.place(x=240,y=60)
    
        #self.note3 = Label(self.Frame3,text="lz",bg="gray",fg="black")
        #self.note3['font'] = myFont
        #self.note3.place(x=250,y=60)

        self.entry3 = Entry(self.Frame3,width= 7, textvariable= self.lz)
        self.entry3['font'] = myFont
        self.entry3.delete(0,END)
        self.entry3.insert(0,"0")
        self.entry3.place(x=360,y=60)
          
    def oct_minsph_frame(self):

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
    
        self.note = Label(self.Frame3,text="Radius of Box",bg="gray",fg="black")
        self.note['font'] = myFont
        self.note.place(x=10,y=10)

        self.entry1 = Entry(self.Frame3, textvariable= self.r)
        self.entry1['font'] = myFont
        self.entry1.delete(0,END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=280,y=10)

    def oct_cyl_frame(self):

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
 
        self.note1 = Label(self.Frame3,text="Length of Cylinder",bg="gray",fg="black")
        self.note1['font'] = myFont
        self.note1.place(x=10,y=10)

        self.entry1 = Entry(self.Frame3, textvariable= self.l)
        self.entry1['font'] = myFont
        self.entry1.delete(0,END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=280,y=10)
 
        self.note2 = Label(self.Frame3,text="Radius of Cylinder",bg="gray",fg="black")
        self.note2['font'] = myFont
        self.note2.place(x=10,y=60)

        self.entry2 = Entry(self.Frame3, textvariable= self.r)
        self.entry2['font'] = myFont
        self.entry2.delete(0,END)
        self.entry2.insert(0,"0")
        self.entry2.place(x=280,y=60)

    def octopus_frame(self):   
 
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.21, relheight=0.67, relwidth=0.492)
        
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
         
        self.lb1 = Label(self.Frame2,text="Dimension",bg="gray",fg="black")
        self.lb1['font'] = myFont
        self.lb1.place(x=10,y=10)
   
        def pick_xc(e):
            if self.cb1.get() == "1":
                xc_octopus.config(value = self.xc_oct1)
                xc_octopus.current(0)
            if self.cb1.get() == "2":
                xc_octopus.config(value = self.xc_oct2)
                xc_octopus.current(0)
            if self.cb1.get() == "3":
                xc_octopus.config(value = self.xc_oct3)
                xc_octopus.current(0)

        self.cb1 = ttk.Combobox(self.Frame2,width= 10, textvariable= self.dxc, value = self.dxc_oct)
        self.cb1.set("--choose--")
        self.cb1['font'] = myFont
        self.cb1.place(x=110,y=10)
        self.cb1.bind("<<ComboboxSelected>>", pick_xc)
        self.cb1['state'] = 'readonly'
 
        self.lb2 = Label(self.Frame2,text="Mixing",bg="gray",fg="black")
        self.lb2['font'] = myFont
        self.lb2.place(x=260,y=10)
 
        self.en1 = Entry(self.Frame2,width= 7, textvariable= self.mix)
        self.en1['font'] = myFont
        self.en1.delete(0,END)
        self.en1.insert(0,"0.3")
        self.en1.place(x=360,y=10)

        self.label_proj = Label(self.Frame2,text="Spacing (Ang)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame2,width= 7, textvariable= self.h)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=110,y=60)

        self.label_proj = Label(self.Frame2, text="Smearing (eV)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=260,y=60)

        self.entry_proj = Entry(self.Frame2, width= 7,textvariable= self.smear)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,END)
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=360,y=60)

        self.lb2 = Label(self.Frame2,text="Smearing Function",bg="gray",fg="black")
        self.lb2['font'] = myFont
        self.lb2.place(x=10,y=110)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.smearfn, value = self.fnsmear)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = Label(self.Frame2,text="Exchange Correlation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        xc_octopus = ttk.Combobox(self.Frame2, textvariable= self.xc, value = " ")
        xc_octopus['font'] = myFont
        xc_octopus.place(x=280,y=160)
        xc_octopus['state'] = 'readonly'

        self.Frame2_note = Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.spinpol, value = ["None","True"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=210)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = Label(self.Frame2,text="Eigen Solver",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.eigen, value = self.eignsolv)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=260)
        self.entry_pol_x['state'] = 'readonly'

    def gs_inp2dict(self):
        inp_dict_gp = {
            'mode': self.mode.get(),
            'xc': self.xc.get(),
            'vacuum': self.vacuum.get(),
            'basis':{'default': self.basis.get()},
            'h': self.h.get(),
            'nbands' : self.nbands.get(),
            'charge' : self.charge.get(),
            'spinpol' : self.spinpol.get(), 
            'multip' : self.multip.get(), 
            'convergence': {'energy' : self.energy.get(),  # eV / electron
                        'density' :  self.density.get(),
                        'eigenstates': 4.0e-8,  # eV^2
                        'bands' : self.bands.get()}, 
            'maxiter' : self.maxiter.get(),
            'box': self.shape.get(),
            'properties': 'get_potential_energy()',
            'engine':'gpaw'
                    }   

        inp_dict_nw = {
            'mode': self.mode.get(),
            'xc': self.xc.get(),
            'tolerances': self.tolerances.get(),
            'basis': self.basis.get(),
            'energy': self.energy.get(),
            'density' : self.density.get(),
            'charge' : self.charge.get(),
            'multip' : self.multip.get(),
            'maxiter' : self.maxiter.get(),
            'engine':'nwchem'
                    }

        inp_dict_oct = {
            'mode': self.mode.get(),
            'xc': self.xc.get(),
            'energy': self.energy.get(),
            'dimension' : self.dxc.get(),
            'spacing': self.h.get(),
            'spin_pol': self.spinpol.get(),
            'charge': self.charge.get(),
            'e_conv': self.energy.get(),
            'max_iter': self.maxiter.get(),
            'eigensolver':self.eigen.get(),
            'smearing':self.smear.get(),
            'smearing_func':self.smearfn.get(),
            'mixing':self.mix.get(),
            'box':{'shape':self.shape.get()},
            'engine':'octopus'
                    }

        if self.basis.get() == '':
            inp_dict_gp['basis']={}

        if self.mode.get() == 'nao':
            inp_dict_gp['mode']='lcao'

        if self.shape.get() in ['Minimum','Sphere']:
            inp_dict_oct['box']={'shape':self.shape.get(),'radius':self.r.get()}
        if self.shape.get() == 'Cylinder':
            inp_dict_oct['box']={'shape':self.shape.get(),'radius':self.r.get(),'xlength':self.l.get()}
        if self.shape.get() == 'Parallelepiped':
            inp_dict_oct['box']={'shape':self.shape.get(),'sizex':self.lx.get(), 'sizey':self.ly.get(), 'sizez':self.lz.get()}

        if self.mode.get() == "gaussian":
 
            inp_dict_nw['directory'] = str(self.controller.directory)+"/"+ str(dir)
            inp_dict_nw['geometry'] = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            print(inp_dict_nw)
            # engn = choose_engine(inp_dict_nw)
            # self.job = GroundState(inp_dict_nw,engn,self.controller.status, self.controller.directory, filename)
            # self.controller.task = self.job
            return inp_dict_nw

        if self.mode.get() in ["nao","pw"]:
  
            inp_dict_gp['directory'] = str(self.controller.directory)+"/"+ str(dir)
            inp_dict_gp['geometry'] = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            print(inp_dict_gp)
            # engn = choose_engine(inp_dict_gp)
            # self.job = GroundState(inp_dict_gp,engn,self.controller.status, self.controller.directory, filename)
            # self.controller.task = self.job
            return inp_dict_gp

        if self.shape.get() in ["Minimum","Sphere","Cylinder"]:
            inp_dict_oct['directory'] = str(self.controller.directory)+"/"+ str(dir)
            inp_dict_oct['geometry'] = pathlib.Path(self.controller.directory) / "coordinate.xyz"
            print(inp_dict_oct)
            # engn = choose_engine(inp_dict_gp)
            # self.job = GroundState(inp_dict_gp,engn,self.controller.status, self.controller.directory, filename)
            # self.controller.task = self.job
            return inp_dict_oct

        if self.shape.get() == "Parallelepiped":
            if self.xc.get() in ["lda_x_1d+lda_e_1d","lda_x_2d+lda_c_2d_amgb","lda_x+lda_e_pz_mod"]:
                inp_dict_oct['directory'] = str(self.controller.directory)+"/"+ str(dir)
                inp_dict_oct['geometry'] = pathlib.Path(self.controller.directory) / "coordinate.xyz"
                print(inp_dict_oct)
                # engn = choose_engine(inp_dict_gp)
                # self.job = GroundState(inp_dict_gp,engn,self.controller.status, self.controller.directory, filename)
                # self.controller.task = self.job
                return inp_dict_oct
            else:
                inp_dict_gp['directory'] = str(self.controller.directory)+"/"+ str(dir)
                inp_dict_gp['geometry'] = pathlib.Path(self.controller.directory) / "coordinate.xyz"
                print(inp_dict_gp)
                # engn = choose_engine(inp_dict_gp)
                # self.job = GroundState(inp_dict_gp,engn,self.controller.status, self.controller.directory, filename)
                # self.controller.task = self.job
                return inp_dict_gp


    def init_task(self, inp_dict: dict, filename):
        engn = choose_engine(inp_dict)
        self.job = GroundState(inp_dict,engn,self.controller.status, self.controller.directory, filename)
        self.controller.task = self.job

    def save_button(self):
        inp_dict = self.gs_inp2dict()
        self.init_task(inp_dict, 'gs')
        self.write_input()
        show_message(self.label_msg,"Saved")

    def view_button(self):

        if hasattr('self.job.engine','directory'):
            self.gs_inp2dict()
            self.controller.show_frame(TextViewerPage, GroundStatePage, None, task=self.controller.task)
        else:
            inp_dict = self.gs_inp2dict()
            self.init_task(inp_dict, 'gs')
            self.controller.show_frame(TextViewerPage, GroundStatePage, None, task=self.controller.task)

    def run_job_button(self):
        self.controller.show_frame(JobSubPage, GroundStatePage, None)
        
    def write_input(self):
        self.job.write_input()
        self.controller.check = True
        self.controller.status.update_status('gs_inp', 1)


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
        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        occup   = StringVar()
        #nbands = StringVar()
        vacuum = StringVar()
        mode = StringVar()
        xc = StringVar()
        basis = StringVar()
        charge = StringVar()
        smear = StringVar()
        forces = StringVar()
        energy = StringVar()
        bands = StringVar()
        maxiter = StringVar()
        
        self.Frame1_label_path = Label(self.Frame1,text="LITESOPH input for Geometery Optimisation",fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=150,y=10)
      
        self.label_proj = Label(self.Frame1,text="Mode",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)
        
        Mainmode = ["lcao","fd","pw","gaussian"]

        # Create a list of sub_task  
        lcao_task = ["dzp","pvalence.dz"]
        fd_task = [""]
        pw_task = [""]
        gauss_task = ["STO-3G","6-31+G*","6-31+G","6-31G*","6-31G","3-21G","cc-pVDZ"]

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
        task.set("--choose mode--")
        task['font'] = myFont
        task.place(x=280,y=60)
        task.bind("<<ComboboxSelected>>", pick_task)
        task['state'] = 'readonly'

        self.Frame2_label_3 = Label(self.Frame1, text="Basis",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=110)
          
        sub_task = ttk.Combobox(self.Frame1, textvariable= basis, value = [" "])
        sub_task.current(0)
        sub_task['font'] = myFont
        sub_task.place(x=280,y=110)
        sub_task['state'] = 'readonly'

        self.label = Label(self.Frame1, text="Exchange Correlation", bg= "grey",fg="black")
        self.label['font'] = myFont
        self.label.place(x=10,y=160)
       
        exch_cor = ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"]

        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= xc, value = exch_cor)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=160)
        self.entry_pol_x['state'] = 'readonly'

        self.label_pol_y = Label(self.Frame1, text="Force Convergence (in eV/Angstrom)", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=210)
    
        self.entry_proj = Entry(self.Frame1,textvariable= forces)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"5e-04")
        self.entry_proj.place(x=280,y=210)

        self.label_pol_z = Label(self.Frame1, text="Energy Converegence (in eV/electron)", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=260)
 
        self.entry_proj = Entry(self.Frame1,textvariable= energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"5e-05")
        self.entry_proj.place(x=280,y=260)

        self.label_proj = Label(self.Frame1,text="Vacuum size (in Angstrom)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= vacuum)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"6")
        self.entry_proj.place(x=280,y=310)
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",activebackground="#78d6ff",command=lambda:controller.show_frame(WorkManagerPage))
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)
        
        # Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",activebackground="#78d6ff", command=lambda:[controller.gui_inp('opt','opt',opt_inp2dict()), show_message(self.label_msg, "Saved")])
        # Frame1_Button1['font'] = myFont
        # Frame1_Button1.place(x=300,y=380)

        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=320,y=350)

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
        self.entry_proj.place(x=280,y=60)
        
        self.Frame2_note = Label(self.Frame2,text="Occupations",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=110)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= occup, value = ["FermiDirac","Gaussian"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = Label(self.Frame2,text="smearing width",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = Entry(self.Frame2,textvariable= smear)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0.0")
        self.entry_proj.place(x=280,y=160)
  
        #self.Frame2_note = Label(self.Frame2,text="Energy Convergence",bg="gray",fg="black")
        #self.Frame2_note['font'] = myFont
        #self.Frame2_note.place(x=10,y=210)

        #self.entry_proj = Entry(self.Frame2,textvariable= energy)
        #self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"5e-05")
        #self.entry_proj.place(x=250,y=210)

        self.Frame2_note = Label(self.Frame2,text="Maxiter",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = Entry(self.Frame2,textvariable= maxiter)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"300")
        self.entry_proj.place(x=280,y=210)
     
        self.Frame2_note = Label(self.Frame2,text="Band Occupancy",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)
  
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= bands , value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=260)
        self.entry_pol_x['state'] = 'readonly'

        #self.entry_proj = Entry(self.Frame2,textvariable= fmax)
        #self.entry_proj['font'] = myFont
        #self.entry_proj.insert(0,"0.05")
        #self.entry_proj.place(x=250,y=310)
        
        # Frame2_Button3 = tk.Button(self.Frame2, text="View Input",activebackground="#78d6ff",command=lambda:[controller.gui_inp('opt','opt',opt_inp2dict()), controller.show_frame(TextViewerPage, GroundStatePage, None)])
        # Frame2_Button3['font'] = myFont
        # Frame2_Button3.place(x=10,y=380)
 
        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",activebackground="#78d6ff",command=lambda:controller.show_frame(JobSubPage, GroundStatePage, None))
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=300,y=380)

        def opt_inp2dict():
            inp_dict = {
                'mode': mode.get(),
                'xc': xc.get(),
                'basis': basis.get(),
                'vacuum': vacuum.get(),
                'occup': occup.get(),
                'smear' : smear.get(),
                'charge' : charge.get(),
                #'spinpol' : spinpol.get(),
                #'fmax' : fmax.get(), 
                'convergence' : {'energy' : float(energy.get()),'forces' : float(forces.get()), 'bands' : bands.get()},
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
        
        self.strength = StringVar()
        self.ex = StringVar()
        self.ey = StringVar()
        self.ez = StringVar()
        self.dt = StringVar()
        self.Nt = StringVar()    
        self.v = StringVar()        
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
        self.entry_proj = ttk.Combobox(self.Frame1,textvariable= self.strength, value = inval)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"1e-5")
        self.entry_proj.place(x=280,y=60)
        self.entry_proj['state'] = 'readonly'

        self.label_pol_x = Label(self.Frame1, text="Electric Polarisation in x axis", bg= "grey",fg="black")
        self.label_pol_x['font'] = myFont
        self.label_pol_x.place(x=10,y=110)
        
        pol_list = ["0","1"]
        self.entry_pol_x = ttk.Combobox(self.Frame1, textvariable= self.ex , value = pol_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"0")
        self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'

        self.label_pol_y = Label(self.Frame1, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=160)
    
        self.entry_pol_y = ttk.Combobox(self.Frame1, textvariable= self.ey, value = pol_list)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.insert(0,"0")
        self.entry_pol_y.place(x=280,y=160)
        self.entry_pol_y['state'] = 'readonly'

        self.label_pol_z = Label(self.Frame1, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=210)
 
        self.entry_pol_z = ttk.Combobox(self.Frame1, textvariable= self.ez ,value = pol_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"0")
        self.entry_pol_z.place(x=280,y=210)
        self.entry_pol_z['state'] = 'readonly'

        self.label_proj = Label(self.Frame1,text="Propagation time step (in attosecond)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= self.dt)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"10")
        self.entry_proj.place(x=280,y=260)

        self.label_proj = Label(self.Frame1,text="Total time steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)

        self.entry_proj = Entry(self.Frame1,textvariable= self.Nt)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"200")
        self.entry_proj.place(x=280,y=310)
        
        Frame1_Button3 = tk.Button(self.Frame1, text="Back",activebackground="#78d6ff",command=lambda:self.back_button())
        Frame1_Button3['font'] = myFont
        Frame1_Button3.place(x=10,y=380)

        Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",activebackground="#78d6ff",command=lambda:[self.save_button()])
        #Frame1_Button1 = tk.Button(self.Frame1, text="Save Input",activebackground="#78d6ff",command=lambda:[td_inp2dict()])
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=300,y=380)

        self.label_msg = Label(self.Frame1,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=320,y=350)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
   
        self.Frame2_note = Label(self.Frame2,text="Note: Please select wavefunction for Kohn Sham Decomposition",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=70)
    
        values = {"Dipole Moment" :"1","Wavefunction": "2"}
        self.v.set("1")
        # Loop is used to create multiple Radiobuttons
        # rather than creating each button separately
        for (text, value) in values.items():
            Radiobutton(self.Frame2, text = text, variable = self.v,
                value = value).pack(side = TOP, anchor=NW, ipady = 5)
 
        Frame2_Button1 = tk.Button(self.Frame2, text="View Input",activebackground="#78d6ff",command=lambda:[self.view_button()])
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

        Frame2_Button2 = tk.Button(self.Frame2, text="Run Job",activebackground="#78d6ff",command=lambda:self.run_job_button())
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=300,y=380)

    def td_inp2dict(self):
        td_dict = {}
        kick = [float(self.strength.get())*float(self.ex.get()),
                float(self.strength.get())*float(self.ey.get()),
                float(self.strength.get())*float(self.ez.get())]
        path = str(self.controller.directory) + "/GS"
        td_dict['filename'] = path +"/gs.gpw"
        td_dict['absorption_kick'] = kick
        td_dict['analysis_tools'] = self.analysis_tool()
        inp_list = [float(self.dt.get()),float(self.Nt.get())]
        td_dict['propagate'] = tuple(inp_list)

        return td_dict

    def analysis_tool(self): 
        if self.v.get() == "1":
            return("dipolemoment")
        elif self.v.get() == "2":
            return("wavefunction")
    

    def init_task(self, td_dict: dict, filename):
        self.job =RT_LCAO_TDDFT(td_dict, engine.EngineGpaw(),self.controller.status,str(self.controller.directory), filename, keyword='delta')
        self.controller.task = self.job
        self.controller.check = True

    def write_input(self):
        self.job.write_input()
        self.controller.check = True
        #self.controller.status.update_status('gs_inp', 1)


    def save_button(self):
        inp_dict = self.td_inp2dict()
        self.init_task(inp_dict, 'td')
        self.write_input()
        show_message(self.label_msg,"Saved")

    def view_button(self):

        if hasattr('self.controller.task.engine','directory'):
            self.td_inp2dict()
            self.controller.show_frame(TextViewerPage, TimeDependentPage, None, task=self.controller.task)
        else:
            inp_dict = self.td_inp2dict()
            self.init_task(inp_dict, 'gs')
            self.controller.show_frame(TextViewerPage, TimeDependentPage, None, task=self.controller.task)

    def run_job_button(self):
        self.controller.show_frame(JobSubPage, TimeDependentPage, None)

    def back_button(self):
        self.controller.show_frame(WorkManagerPage)

        
    

    

class LaserDesignPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
        self.tdpulse_dict = {}
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

        self.label_proj = Label(self.Frame1,text="Time Origin (tin)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = Entry(self.Frame1,textvariable= self.tin)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=280,y=60)
        
        self.label_proj = Label(self.Frame1,text="Pulse Amplitute at tin",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=100)
 
        inval_list = ["1e-8", "1e-9"]
        self.entry_pol_z = ttk.Combobox(self.Frame1,textvariable= self.inval, value = inval_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"1e-8")
        self.entry_pol_z.place(x=280,y=100)
        self.entry_pol_z['state'] = 'readonly'

        self.label_proj = Label(self.Frame1,text="Laser Strength in a.u",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=140)
    
        instr = ["1e-5","1e-3"]
        self.entry_proj = ttk.Combobox(self.Frame1,textvariable= self.strength, value = instr)
        self.entry_proj['font'] = myFont
        self.entry_proj.current(0)
        self.entry_proj.place(x=280,y=140)
        self.entry_proj['state'] = 'readonly'

        self.label_proj = Label(self.Frame1,text="Full Width Half Max (FWHM in eV)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=180)

        self.entry_proj = Entry(self.Frame1,textvariable= self.fwhm)
        self.fwhm.set("0.2")
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=280,y=180)

        self.label_proj = Label(self.Frame1,text="Frequency in eV",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=220)

        self.entry_proj = Entry(self.Frame1,textvariable= self.freq)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=280,y=220)

        self.label_proj = Label(self.Frame1,text="Time step in attosecond ",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=260)

        self.entry_proj = Entry(self.Frame1,textvariable= self.ts)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"10")
        self.entry_proj.place(x=280,y=260)
        
        self.label_proj = Label(self.Frame1,text="Number of Steps",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=300)

        self.entry_proj = Entry(self.Frame1,textvariable= self.ns)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"2000")
        self.entry_proj.place(x=280,y=300)
 
        Frame1_Button1 = tk.Button(self.Frame1, text="Back",activebackground="#78d6ff",command=lambda:self.back_button())
        Frame1_Button1['font'] = myFont
        Frame1_Button1.place(x=10,y=380)
        
        self.button_project = Button(self.Frame1,text="Next",activebackground="#78d6ff",command=lambda:[self.choose_laser()])
        self.button_project['font'] = myFont
        self.button_project.place(x=350,y=380)

        self.button_project = Button(self.Frame1,text="Laser Design",activebackground="#78d6ff",command=lambda:[self.laser_button()])
        self.button_project['font'] = myFont
        self.button_project.place(x=170,y=380)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.label_pol_x = Label(self.Frame2, text="Electric Polarisation in x axis", bg= "grey",fg="black")
        self.label_pol_x['font'] = myFont
        self.label_pol_x.place(x=10,y=60)
        
        pol_list = ["0","1"]
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.pol_x, value = pol_list)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.insert(0,"0")
        self.entry_pol_x.place(x=280,y=60)
        self.entry_pol_x['state'] = 'readonly'

        self.label_pol_y = Label(self.Frame2, text="Electric Polarisation in y axis", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=110)
    
        self.entry_pol_y = ttk.Combobox(self.Frame2,textvariable= self.pol_y, value = pol_list)
        self.entry_pol_y['font'] = myFont
        self.entry_pol_y.insert(0,"0")
        self.entry_pol_y.place(x=280,y=110)
        self.entry_pol_y['state'] = 'readonly'

        self.label_pol_z = Label(self.Frame2, text="Electric Polarisation in z axis", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=160)
 
        self.entry_pol_z = ttk.Combobox(self.Frame2,textvariable= self.pol_z, value = pol_list)
        self.entry_pol_z['font'] = myFont
        self.entry_pol_z.insert(0,"0")
        self.entry_pol_z.place(x=280,y=160) 
        self.entry_pol_z['state'] = 'readonly'

        self.Frame2_Button1 = tk.Button(self.Frame2, state='disabled', text="Save Input",activebackground="#78d6ff", command=lambda:[self.save_button()])
        self.Frame2_Button1['font'] = myFont
        self.Frame2_Button1.place(x=10,y=380)

        self.label_msg = Label(self.Frame2,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=10,y=350)
 
        self.Frame2_Button2 = tk.Button(self.Frame2, state='disabled', text="View Input",activebackground="#78d6ff", command=lambda:[self.view_button()])
        self.Frame2_Button2['font'] = myFont
        self.Frame2_Button2.place(x=170,y=380)
        
        self.Frame2_Button3 = tk.Button(self.Frame2, state='disabled', text="Run Job",activebackground="#78d6ff",command=lambda:self.run_job_button())
        self.Frame2_Button3['font'] = myFont
        self.Frame2_Button3.place(x=350,y=380)
        self.Frame3 = None
        self.button_refresh()

    def view_button(self):
        self.tdpulse_inp2dict('td_pulse')
        self.controller.show_frame(TextViewerPage, LaserDesignPage, None, task=self.job)

    def create_frame3(self):
        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
    
    def laser_button(self):
        dir = pathlib.Path(self.controller.directory)/ "TD_Laser"
        write_laser(self.laser_pulse(), 'laser', self.controller.directory )
        self.plot_canvas(str(self.controller.directory)+"/laser.dat", 1, 'time(in fs)','Laser strength(in au)')
       

    def plot_canvas(self,filename, axis, x,y):
        from litesoph.utilities.units import au_to_fs
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
        figure = Figure(figsize=(5, 3), dpi=100)
        data_ej = np.loadtxt(filename) 
        #plt.figure(figsize=(5, 3), dpi=100)

        if self.Frame3 is not None:
            self.Frame3.destroy()
            
        self.create_frame3()
        self.ax = figure.add_subplot(1, 1, 1)
        self.ax.plot(data_ej[:, 0]*au_to_fs, data_ej[:, axis], 'k')
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.set_xlabel(x)
        self.ax.set_ylabel(y)

        self.Frame3.canvas = FigureCanvasTkAgg(figure, master=self.Frame3)
        self.Frame3.canvas.draw()
        self.Frame3.canvas.get_tk_widget().pack(side =LEFT,fill='both', expand=True)
        self.Frame3.toolbar = NavigationToolbar2Tk(self.Frame3.canvas, self.Frame3)
        self.Frame3.toolbar.update()
        self.Frame3.canvas._tkcanvas.pack(side= tk.TOP,fill ='both')
        #plt.savefig('pulse.png')

    def button_refresh(self):
        self.st_var = self.controller.status 
        if self.st_var.check_status('td_inp', 2):
            self.Frame2.tkraise() 
            self.Frame2_Button1.config(state='active') 
            self.Frame2_Button2.config(state='active') 
            self.Frame2_Button3.config(state='active') 
               

    def choose_laser(self):
        check = messagebox.askyesno(message= "Do you want to proceed with this laser set up?")
        if check is True:
            self.Frame2.tkraise()
            self.Frame2_Button1.config(state='active') 
            self.Frame2_Button2.config(state='active') 
            self.Frame2_Button3.config(state='active') 
        else:
            messagebox.showinfo(message="Please enter the laser design inputs.") 
            self.controller.show_frame(LaserDesignPage,WorkManagerPage,JobSubPage)

    def laser_pulse(self):
        l_dict = self.laser_calc()
        l_dict['frequency'] = self.freq.get()
        l_dict['time0'] ="{}e3".format(l_dict['time0'])
        range = int(self.ns.get())* float(self.ts.get())
        l_dict['range'] = range
        l_dict['sincos'] = 'sin'
        return(l_dict)              
      
    def laser_calc(self):
        from litesoph.pre_processing.laser_design import laser_design
        l_dict = laser_design(self.strength.get(), self.inval.get(),self.tin.get(),self.fwhm.get())
        return(l_dict)

    def tdpulse_inp2dict(self):
        self.td = self.tdpulse_dict
        self.dir = self.controller.directory
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
        updatekey(self.td,'dipole_file','dmlaser.dat')
        updatekey(self.td,'filename', str(self.dir)+'/GS/gs.gpw')
        updatekey(self.td,'td_potential', True)
        updatekey(self.td,'txt', 'tdlaser.out')
        updatekey(self.td,'td_out', 'tdlaser.gpw')
        updatekey(self.td,'laser', laser_dict)

        return(self.td)       

    def init_task(self, td_dict: dict, filename):
        self.job =RT_LCAO_TDDFT(td_dict, engine.EngineGpaw(),self.controller.status,str(self.controller.directory), filename,keyword='laser')
        self.controller.task = self.job
        self.controller.check = True

    def write_input(self):
        self.job.write_input()
        self.controller.check = True
        

    def save_button(self):
        inp_dict = self.tdpulse_inp2dict()
        self.init_task(inp_dict, 'tdlaser')
        self.write_input()
        show_message(self.label_msg,"Saved")

    def view_button(self):

        if hasattr('self.controller.task.engine','directory'):
            self.tdpulse_inp2dict()
            self.controller.show_frame(TextViewerPage, LaserDesignPage, None, task=self.job)
        else:
            inp_dict = self.tdpulse_inp2dict()
            self.init_task(inp_dict, 'tdlaser')
            self.controller.show_frame(TextViewerPage, LaserDesignPage, None, task=self.controller.task)

    def run_job_button(self):
        self.controller.show_frame(JobSubPage, LaserDesignPage, None)

    def back_button(self):
        self.controller.show_frame(WorkManagerPage)

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

        self.Frame2_Run = tk.Button(self.Frame,text="Run Job", state= 'disabled',activebackground="#78d6ff",command=lambda:[self.controller.show_frame(JobSubPage, PlotSpectraPage, None)])
        self.Frame2_Run['font'] = myFont
        self.Frame2_Run.place(x=320,y=380)
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:controller.show_frame(WorkManagerPage))
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
      

class JobSubPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)
        self.processors = IntVar()

        self.Frame.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.978)
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

        sbj_entry1 = Entry(self,textvariable= self.processors, width=20)
        self.processors.set(1)
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=60)
        
        sbj_label1 = Label(self, text="To submit job through Network, provide details", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=110)

        sbj_button1 = Button(self, text="Run Local",activebackground="#78d6ff",command=lambda:[self.submitjob_local()])
        sbj_button1['font'] = myFont
        sbj_button1.place(x=600, y=60)

        self.msg_label1 = Label(self, text='', fg='blue')
        self.msg_label1['font'] = myFont
        self.msg_label1.place(x=600,y=100)

        back2prev = tk.Button(self, text="Back",activebackground="#78d6ff",command=lambda:controller.show_frame(self.prev, self, None))
        back2prev['font'] = myFont
        back2prev.place(x=15,y=380)

        back = tk.Button(self, text="Back to main page",activebackground="#78d6ff",command=lambda:[controller.show_frame(WorkManagerPage)])
        back['font'] = myFont
        back.place(x=600,y=380)              

    def submitjob_local(self):
        if self.controller.check is not True:
            from litesoph.utilities.job_submit import get_submit_class
            self.submit = get_submit_class(engine=self.controller.task.engine, configs=self.controller.lsconfig, nprocessors=self.processors.get())
            process = self.controller.task.run(self.submit)
        else:
            from litesoph.gui.job_validation import select_job
            job = self.checkjob()
            select_job(self,job, self.controller.status)     

    # def submitjob(self):
    #     from litesoph.utilities.job_submit import get_submit_class
    #     self.submit = get_submit_class(engine=self.controller.task.engine, configs=self.controller.lsconfig, nprocessors=self.processors.get())
    #     process = self.controller.task.run(self.submit)
        

    def checkjob(self):
        try:
            if type(self.controller.task).__name__ == 'GroundState':
                return('gs')
            if type(self.controller.task).__name__ == 'RT_LCAO_TDDFT':
                return self.controller.task.keyword  
            if type(self.controller.task).__name__ == 'Spectrum':
                return('spec')
            if type(self.controller.task).__name__ == 'TCM':
                return('tcm')
            if type(self.controller.task).__name__ == 'InducedDensity':
                return('indensity')
        except:
            messagebox.showerror(message="Input not created!. Please create input before submitting the job ")

    def call_run(self,key, value):
        from litesoph.utilities.job_submit import get_submit_class
        self.submit = get_submit_class(engine=self.controller.task.engine, configs=self.controller.lsconfig, nprocessors=self.processors.get())
        process = self.controller.task.run(self.submit)
        f = file_check(self.job_d['check_list'], self.controller.directory) 
        f_check = f.check_list(self.job_d['out']) 
        if f_check is True:
            self.controller.status.update_status(key, value) 
            show_message(self.msg_label1,"Job Done")
        else:
            show_message(self.msg_label1, "Error while generating output") 
            
   
    def run_job(self, key, value1, value2):
        if self.job_d['cal_check'] is False:
            self.call_run(key, value1)  
        else:
            show_message(self.msg_label1, "")
            check_yn = messagebox.askyesno(title="Job is done",message="Do you want to redo the calculation? ")
            if check_yn is True:
                self.controller.status.update_status(key, value2)
                self.call_run(key, value1)

    
    def submitjob_network(self):
        pass

class DmLdPage(Frame):

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
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
    
        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:controller.show_frame(WorkManagerPage))
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

    def __init__(self, parent, controller,prev, next):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
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

        Frame_Button1 = tk.Button(self.Frame, text="Back",activebackground="#78d6ff",command=lambda:controller.show_frame(WorkManagerPage))
        Frame_Button1['font'] = myFont
        Frame_Button1.place(x=10,y=380)

        #self.buttonRetrieve = Button(self.Frame, text="Retrieve Freq",activebackground="#78d6ff",command=lambda:[self.retrieve_input(),self.freq_listbox(), self.tcm_button()])
        self.buttonRetrieve = Button(self.Frame, text="Create input",activebackground="#78d6ff",command=lambda:self.create_tcm())
        self.buttonRetrieve['font'] = myFont
        self.buttonRetrieve.place(x=200,y=380)

        self.Frame_run = tk.Button(self.Frame,text="Run Job", state= 'disabled',activebackground="#78d6ff", command=lambda:[self.controller.show_frame(JobSubPage, TcmPage, None)])
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

    def __init__(self, parent, controller,prev, next, file=None, task=None):
        Frame.__init__(self, parent)
        self.controller = controller
        self.prev = prev
        self.next = next
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

        # jobsub = tk.Button(self, text="Run Job",bg='blue',fg='white',command=lambda:controller.show_frame(JobSubPage))
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
        self.controller.show_frame(self.prev, WorkManagerPage, JobSubPage, refresh=False)

        
        

#--------------------------------------------------------------------------------        


if __name__ == '__main__':
   
    
    app = AITG()
    app.title("AITG - LITESOPH")
    #app.geometry("1500x700")
    app.resizable(True,True)
    app.mainloop()
