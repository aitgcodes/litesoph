import tkinter as tk
from tkinter import ttk
from tkinter import filedialog           # importing filedialog which is used for opening windows to read files.
from tkinter import messagebox
from  PIL import Image,ImageTk
from tkinter import font

import pathlib

from litesoph.gui.filehandler import show_message





class StartPage(tk.Frame):

    def __init__(self, parent, lsroot, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.lsroot = lsroot
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        

        mainframe = ttk.Frame(self,padding="12 12 24 24")
        #mainframe = ttk.Frame(self)
        mainframe.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        frame =ttk.Frame(self, relief=tk.SUNKEN, padding="6 6 0 24")
        #frame =ttk.Frame(self)
        frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        myFont = font.Font(family='Helvetica', size=15, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=10,weight='bold')
        
        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 20))

        parent.configure(bg="grey60")

        # create a canvas to show project list icon
        canvas_for_project_list_icon=tk.Canvas(frame, bg='gray', height=400, width=400, borderwidth=0, highlightthickness=0)
        canvas_for_project_list_icon.grid(column=1, row=1, sticky=(tk.W, tk.E) ,columnspan=8,rowspan=8)
        #canvas_for_project_list_icon.place(x=5,y=5)

        #image_project_list = Image.open('images/project_list.png')
        #canvas_for_project_list_icon.image = ImageTk.PhotoImage(image_project_list.resize((100,100), Image.ANTIALIAS))
        #canvas_for_project_list_icon.create_image(0,0, image=canvas_for_project_list_icon.image, anchor='nw')
        
        #frame_1_label_1 = Label(frame,text="Manage Job(s)", fg="blue")
        #frame_1_label_1['font'] = myFont
        #frame_1_label_1.grid(row=10, column=2, sticky=(W, E) ,columnspan=3,rowspan=2)

        #label_1 = Label(mainframe,text="Welcome to LITESOPH", bg='#0052cc',fg='#ffffff')
        label_1 = tk.Label(mainframe,text="Welcome to LITESOPH",fg='blue')
        label_1['font'] = myFont
        #label_1.grid(row=0,column=1,sticky=(E,S))
        label_1.place(x=200,y=50)
        
        label_2 = tk.Label(mainframe,text="Layer Integrated Toolkit and Engine for Simulations of Photo-induced Phenomena",fg='blue')
        label_2['font'] = l
        label_2.grid(row=1,column=1)
        #label_2.place(x=200,y=100)

        # create a canvas to show image on
        canvas_for_image = tk.Canvas(mainframe, bg='gray', height=125, width=125, borderwidth=0, highlightthickness=0)
        #canvas_for_image.grid(row=30,column=0, sticky='nesw', padx=0, pady=0)
        canvas_for_image.place(x=30,y=5)

        # create image from image location resize it to 100X100 and put in on canvas
        path1 = pathlib.PurePath(self.lsroot) / "litesoph" / "gui" / "images"

        image = Image.open(str(pathlib.Path(path1) / "logo_ls.jpg"))
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((125, 125), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=tk.Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open(str(pathlib.Path(path1) / "project_create.png"))
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = tk.Button(mainframe,text="Start LITESOPH Project", activebackground="#78d6ff",command=lambda: self.event_generate('<<ShowWorkManagerPage>>'))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        #button_open_project = Button(mainframe,text="About LITESOPH",fg="white")
        button_open_project = tk.Button(mainframe,text="About LITESOPH")
        button_open_project['font'] = myFont
        button_open_project.place(x=80,y=300)
                       


class WorkManagerPage(tk.Frame):


    MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]
    Pre_task = ["Ground State","Geometry Optimisation"]
    Sim_task = ["Delta Kick","Gaussian Pulse"]
    Post_task = ["Spectrum","Dipole Moment and Laser Pulse","Kohn Sham Decomposition","Induced Density","Generalised Plasmonicity Index"]

    def __init__(self, parent, lsroot, directory, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        
        self.lsroot = lsroot
        self.directory = directory
        self.proj_path = tk.StringVar()
        self.proj_name = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1 = tk.Frame(self)
        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.489)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        self.Frame1_label_path = tk.Label(self.Frame1,text="Project Path",bg="gray",fg="black")
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=10,y=10)

        self.entry_path = tk.Entry(self.Frame1,textvariable=self.proj_path)
        self.entry_path['font'] = myFont
        self.entry_path.delete(0, tk.END)
        #self.proj_path.set(self.directory)
        self.entry_path.place(x=200,y=10)     

        self.label_proj = tk.Label(self.Frame1,text="Project Name",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)
        
        self.entry_proj = tk.Entry(self.Frame1,textvariable=self.proj_name)
        self.entry_proj['font'] = myFont
        self.entry_proj.place(x=200,y=70)
        self.entry_proj.delete(0, tk.END)
                
        self.button_project = tk.Button(self.Frame1,text="Create New Project",activebackground="#78d6ff",command=self._create_project)
        self.button_project['font'] = myFont
        self.button_project.place(x=125,y=380)
      
        self.Frame1_Button_MainPage = tk.Button(self.Frame1, text="Start Page",activebackground="#78d6ff", command=lambda:self.event_generate('<<ShowStartPage>>'))
        self.Frame1_Button_MainPage['font'] = myFont
        self.Frame1_Button_MainPage.place(x=10,y=380)
        
        self.button_project = tk.Button(self.Frame1,text="Open Existing Project",activebackground="#78d6ff",command=self._open_project)
        self.button_project['font'] = myFont
        self.button_project.place(x=290,y=380)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.501, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        self.Frame2_label_1 = tk.Label(self.Frame2, text="Upload Geometry",bg='gray',fg='black')  
        self.Frame2_label_1['font'] = myFont
        self.Frame2_label_1.place(x=10,y=10)

        self.Frame2_Button_1 = tk.Button(self.Frame2,text="Select",activebackground="#78d6ff",command=self._get_geometry_file)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=200,y=10)

        self.message_label = tk.Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=270,y=15)

        
        self.Frame2_Button_1 = tk.Button(self.Frame2,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.Frame2_Button_1['font'] = myFont
        self.Frame2_Button_1.place(x=350,y=10)

        self.label_proj = tk.Label(self.Frame2,text="Job Type",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=70)

            
        self.task = ttk.Combobox(self.Frame2,width= 30, values= self.MainTask)
        self.task.set("--choose job task--")
        self.task['font'] = myFont
        self.task.place(x=200,y=70)
        self.task.bind("<<ComboboxSelected>>", self.pick_task)
        self.task['state'] = 'readonly'

        self.Frame2_label_3 = tk.Label(self.Frame2, text="Sub Task",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=130)
          
        self.sub_task = ttk.Combobox(self.Frame2, width= 30, value = [" "])
        self.sub_task['font'] = myFont
        self.sub_task.current(0)
        self.sub_task.place(x=200,y=130)
        self.sub_task['state'] = 'readonly'   
           
        Frame2_Button1 = tk.Button(self.Frame2, text="Proceed",activebackground="#78d6ff",command=lambda:self.event_generate('<<SelectTask>>'))
        Frame2_Button1['font'] = myFont
        Frame2_Button1.place(x=10,y=380)

    def pick_task(self, *_):
            if self.task.get() == "Preprocessing Jobs":
                self.sub_task.config(value = self.Pre_task)
                self.sub_task.current(0)
            if self.task.get() == "Simulations":
                self.sub_task.config(value = self.Sim_task)
                self.sub_task.current(0)
            if self.task.get() == "Postprocessing Jobs":
                self.sub_task.config(value = self.Post_task)
                self.sub_task.current(0)

    def update_project_entry(self, proj_path):
        proj_path = pathlib.Path(proj_path)
        self.proj_path.set(proj_path.parent)
        self.entry_path.config(textvariable=self.proj_path)
        self.proj_name.set(proj_path.name)
        self.entry_proj.config(textvariable=self.proj_name)

    def _open_project(self):
        self.event_generate('<<OpenExistingProject>>')

    def get_project_path(self):
        project_path = pathlib.Path(self.entry_path.get()) / self.entry_proj.get()
        return project_path

    def _create_project(self):
        self.event_generate('<<CreateNewProject>>')

    def _get_geometry_file(self):
        self.event_generate('<<GetMolecule>>')
        show_message(self.message_label,"Uploaded")
    
    def _geom_visual(self):
        self.event_generate('<<VisualizeMolecule>>')
    

class GroundStatePage(tk.Frame):
  
    Mainmode = ["nao","fd","pw","gaussian"]
    nao_task = ["dzp","pvalence.dz"]
    fd_task = [""]
    pw_task = [""]
    gauss_task = ["6-31G","STO-2G","STO-3G","STO-6G","3-21G","3-21G*","6-31G*","6-31G**","6-311G","6-311G*","6-311G**","cc-pVDZ","aug-cc-pvtz"]
    octgp_box = ["parallelepiped","minimum", "sphere", "cylinder"]
    nw_box = ["None"]
    gp_box = ["parallelepiped"]
    xc_gp = ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP"]
    xc_nw = ["acm","b3lyp","beckehandh","Hfexch","pbe0","becke88","xpbe96","bhlyp","cam-s12g","cam-s12h","xperdew91","pbeop"]
    xc_oct1 = ["lda_x_1d + lda_e_1d"]
    xc_oct2 = ["lda_x_2d + lda_c_2d_amgb"]
    xc_oct3 = ["lda_x + lda_c_pz_mod"]
    dxc_oct = ["1","2","3"]
    fnsmear = ["semiconducting","fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing"]
    eignsolv = ["rmmdiis","plan","cg","cg_new"]

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        self.job = None
        
        self.Frame1 = tk.Frame(self)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")
        self.Frame1 = tk.Frame(self)
        
        self.mode = tk.StringVar()
        self.xc = tk.StringVar()
        self.basis = tk.StringVar()
        self.charge = tk.StringVar()
        self.maxiter = tk.IntVar()
        self.shape = tk.StringVar()
        self.spinpol = tk.StringVar()
        self.multip = tk.StringVar()
        self.h   = tk.StringVar()
        self.nbands = tk.StringVar()
        self.vacuum = tk.StringVar()
        self.energy = tk.DoubleVar()
        self.density = tk.DoubleVar()
        self.bands = tk.StringVar()
        self.theory = tk.StringVar()
        self.tolerances = tk.StringVar()
        self.dimension = tk.StringVar()
        self.lx = tk.DoubleVar()
        self.ly = tk.DoubleVar()
        self.lz = tk.DoubleVar()
        self.r = tk.DoubleVar()
        self.l = tk.DoubleVar()
        self.dxc = tk.StringVar()
        self.mix = tk.StringVar()
        self.eigen = tk.StringVar()
        self.smear = tk.StringVar()
        self.smearfn = tk.StringVar()
        self.unitconv = tk.StringVar()
        self.unit_box = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.492)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")            
        
        self.Frame1_label_path = tk.Label(self.Frame1,text="LITESOPH input for Ground State",fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.place(x=150,y=10)
      
        self.label_proj = tk.Label(self.Frame1,text="Mode",bg="gray",fg="black")
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

        self.Frame2_label_3 = tk.Label(self.Frame1, text="Basis",bg='gray',fg='black')
        self.Frame2_label_3['font'] = myFont
        self.Frame2_label_3.place(x=10,y=110)
          
        sub_task = ttk.Combobox(self.Frame1, textvariable= self.basis, value = [" "])
        sub_task.current(0)
        sub_task['font'] = myFont
        sub_task.place(x=280,y=110)
        sub_task['state'] = 'readonly'

        self.label_pol_y = tk.Label(self.Frame1, text="Charge", bg= "grey",fg="black")
        self.label_pol_y['font'] = myFont
        self.label_pol_y.place(x=10,y=160)
    
        self.entry_proj = tk.Entry(self.Frame1,textvariable= self.charge)
        self.entry_proj['font'] = myFont
        self.entry_proj.insert(0,"0")
        self.entry_proj.place(x=280,y=160)

        self.label_pol_z = tk.Label(self.Frame1, text="Maximum SCF iteration", bg= "grey",fg="black")
        self.label_pol_z['font'] = myFont
        self.label_pol_z.place(x=10,y=210)
 
        entry = tk.Entry(self.Frame1,textvariable= self.maxiter)
        entry['font'] = myFont
        entry.delete(0,tk.END)
        entry.insert(0,"300")
        entry.place(x=280,y=210)

        self.Frame2_note = tk.Label(self.Frame1,text="Energy Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = tk.Entry(self.Frame1, width= 10, textvariable= self.energy)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"5.0e-7")
        self.entry_proj.place(x=280,y=260)
 
        unit = ttk.Combobox(self.Frame1,width=5, textvariable= self.unitconv , value = ["eV","au","Ha","Ry"])
        unit.current(0)
        unit['font'] = myFont
        unit.place(x=380,y=260)
        unit['state'] = 'readonly'
       
        self.label_proj = tk.Label(self.Frame1,text="Box Shape",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=310)
    
        def pick_frame(e):
            if box_shape.get() == "parallelepiped":
                if task.get() == "fd":
                    self.gp2oct()
            if box_shape.get() == "minimum": 
                self.oct_minsph_frame()
                self.octopus_frame()
            if box_shape.get() == "sphere":
                self.oct_minsph_frame()
                self.octopus_frame()
            if box_shape.get() == "cylinder": 
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

        self.label_msg = tk.Label(self.Frame6,text="")
        self.label_msg['font'] = myFont
        self.label_msg.place(x=300,y=12.5)

        Frame2_Button2 = tk.Button(self.Frame6, text="Run Job",activebackground="#78d6ff",command=lambda:[self.run_job_button()])
        Frame2_Button2['font'] = myFont
        Frame2_Button2.place(x=380,y=10)

    def gp2oct(self):
        self.check = messagebox.askyesno(message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
        if self.check is True:
            self.gpaw_frame()
        else:
            self.oct_ppl_frame()
            self.octopus_frame()
       
    def back_button(self):
        self.event_generate('<<ShowWorkManagerPage>>')
              
            
    def gpaw_frame(self):  

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.01, relheight=0.87, relwidth=0.492)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
        
        self.label_proj = tk.Label(self.Frame2,text="Density",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=10)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.density)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1.0e-4")
        self.entry_proj.place(x=280,y=10)
 
        self.Frame2_note = tk.Label(self.Frame2,text="Exchange Corelation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=60)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.xc, value = self.xc_gp)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=60)
        self.entry_pol_x['state'] = 'readonly'

        self.label_proj = tk.Label(self.Frame2,text="Spacing (in Ang)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=110)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.h)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=280,y=110)
        
        self.Frame2_note = tk.Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.spinpol, value = ["None","True"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=160)
        self.entry_pol_x['state'] = 'readonly'
 
        self.Frame2_note = tk.Label(self.Frame2,text="Number of Bands",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.nbands)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.place(x=280,y=210)

        self.Frame2_note = tk.Label(self.Frame2,text="Vacuum size (in Ang)",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.vacuum)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"6")
        self.entry_proj.place(x=280,y=260)
     
        self.Frame2_note = tk.Label(self.Frame2,text="Band Occupancy",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=310)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.bands, value = ["occupied","unoccupied"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=310)
        self.entry_pol_x['state'] = 'readonly'
        

    def nwchem_frame(self):   

 
        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.01, relheight=0.87, relwidth=0.492)
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
        
        self.Frame2_note = tk.Label(self.Frame2,text="Exchange Corelation",bg="gray",fg="black")
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

        self.Frame2_note = tk.Label(self.Frame2,text="Density Convergence",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=110)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.density)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1.0e-5")
        self.entry_proj.place(x=280,y=110)

        self.Frame2_note = tk.Label(self.Frame2,text="Multiplicity",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        self.entry_proj = tk.Entry(self.Frame2,textvariable= self.multip)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1")
        self.entry_proj.place(x=280,y=160)

        self.Frame2_note = tk.Label(self.Frame2,text="Tolerance",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.tolerances, value = ["tight","accCoul","radius"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=210)
        self.entry_pol_x['state'] = 'readonly'
        

    def oct_ppl_frame(self):
    

        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
   
        self.boxlabel = tk.Label(self.Frame3,text="Simulation box unit",bg="gray",fg="black")
        self.boxlabel['font'] = myFont
        self.boxlabel.place(x=10,y=10)

        unit = ttk.Combobox(self.Frame3, width=9, textvariable= self.unit_box, value = ["au","angstrom"])
        unit.current(0)
        unit['font'] = myFont
        unit.place(x=220,y=10)
        unit['state'] = 'readonly'
 
        #self.note1 = Label(self.Frame3,text="lx",bg="gray",fg="black")
        #self.note1['font'] = myFont
        #self.note1.place(x=10,y=60)
       
        self.note = tk.Label(self.Frame3,text="Length of Box (lx, ly, lz)",bg="gray",fg="black")
        self.note['font'] = myFont
        self.note.place(x=10,y=40)

        self.entry1 = tk.Entry(self.Frame3,width= 5, textvariable= self.lx)
        self.entry1['font'] = myFont
        self.entry1.delete(0,tk.END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=220,y=40)
 
        #self.note2 = Label(self.Frame3,text="ly",bg="gray",fg="black")
        #self.note2['font'] = myFont
        #self.note2.place(x=130,y=60)

        self.entry2 = tk.Entry(self.Frame3, width= 5, textvariable= self.ly)
        self.entry2['font'] = myFont
        self.entry2.delete(0,tk.END)
        self.entry2.insert(0,"0")
        self.entry2.place(x=280,y=40)
    
        #self.note3 = Label(self.Frame3,text="lz",bg="gray",fg="black")
        #self.note3['font'] = myFont
        #self.note3.place(x=250,y=60)

        self.entry3 = tk.Entry(self.Frame3,width=5, textvariable= self.lz)
        self.entry3['font'] = myFont
        self.entry3.delete(0,tk.END)
        self.entry3.insert(0,"0")
        self.entry3.place(x=340,y=40)

                  
    def oct_minsph_frame(self):
  
        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")
    
        self.boxlabel = tk.Label(self.Frame3,text="Simulation box unit",bg="gray",fg="black")
        self.boxlabel['font'] = myFont
        self.boxlabel.place(x=10,y=10)

        unit = ttk.Combobox(self.Frame3, width=9, textvariable= self.unit_box, value = ["au","angstrom"])
        unit.current(0)
        unit['font'] = myFont
        unit.place(x=220,y=10)
        unit['state'] = 'readonly'

        self.note = tk.Label(self.Frame3,text="Radius of Box",bg="gray",fg="black")
        self.note['font'] = myFont
        self.note.place(x=10,y=40)

        self.entry1 = tk.Entry(self.Frame3, textvariable= self.r, width= 7)
        self.entry1['font'] = myFont
        self.entry1.delete(0,tk.END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=220,y=40)

    def oct_cyl_frame(self):

        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.5, rely=0.01, relheight=0.2, relwidth=0.492)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")

        self.boxlabel = tk.Label(self.Frame3,text="Simulation box unit",bg="gray",fg="black")
        self.boxlabel['font'] = myFont
        self.boxlabel.place(x=10,y=10)

        unit = ttk.Combobox(self.Frame3, width=9, textvariable= self.unit_box, value = ["au","angstrom"])
        unit.current(0)
        unit['font'] = myFont
        unit.place(x=220,y=10)
        unit['state'] = 'readonly'

        self.note1 = tk.Label(self.Frame3,text="Length of Cylinder",bg="gray",fg="black")
        self.note1['font'] = myFont
        self.note1.place(x=10,y=40)

        self.entry1 = tk.Entry(self.Frame3, textvariable= self.l, width= 5)
        self.entry1['font'] = myFont
        self.entry1.delete(0,tk.END)
        self.entry1.insert(0,"0")
        self.entry1.place(x=220,y=40)
 
        self.note2 = tk.Label(self.Frame3,text="Radius of Cylinder",bg="gray",fg="black")
        self.note2['font'] = myFont
        self.note2.place(x=280,y=40)

        self.entry2 = tk.Entry(self.Frame3, textvariable= self.r, width= 5)
        self.entry2['font'] = myFont
        self.entry2.delete(0,tk.END)
        self.entry2.insert(0,"0")
        self.entry2.place(x=430,y=40)

    def octopus_frame(self):   

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.5, rely=0.21, relheight=0.67, relwidth=0.492)
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")
         
        self.lb1 = tk.Label(self.Frame2,text="Dimension",bg="gray",fg="black")
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
 
        self.lb2 = tk.Label(self.Frame2,text="Mixing",bg="gray",fg="black")
        self.lb2['font'] = myFont
        self.lb2.place(x=260,y=10)
 
        self.en1 = tk.Entry(self.Frame2,width= 7, textvariable= self.mix)
        self.en1['font'] = myFont
        self.en1.delete(0,tk.END)
        self.en1.insert(0,"0.3")
        self.en1.place(x=360,y=10)

        self.label_proj = tk.Label(self.Frame2,text="Spacing (Ang)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=10,y=60)

        self.entry_proj = tk.Entry(self.Frame2,width= 7, textvariable= self.h)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"0.23")
        self.entry_proj.place(x=110,y=60)

        self.label_proj = tk.Label(self.Frame2, text="Smearing (eV)",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.place(x=260,y=60)

        self.entry_proj = tk.Entry(self.Frame2, width= 7,textvariable= self.smear)
        self.entry_proj['font'] = myFont
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"0.3")
        self.entry_proj.place(x=360,y=60)

        self.lb2 = tk.Label(self.Frame2,text="Smearing Function",bg="gray",fg="black")
        self.lb2['font'] = myFont
        self.lb2.place(x=10,y=110)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.smearfn, value = self.fnsmear)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = tk.Label(self.Frame2,text="Exchange Correlation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=160)

        xc_octopus = ttk.Combobox(self.Frame2, textvariable= self.xc, value = " ")
        xc_octopus['font'] = myFont
        xc_octopus.place(x=280,y=160)
        xc_octopus['state'] = 'readonly'

        self.Frame2_note = tk.Label(self.Frame2,text="Spin Polarisation",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=210)
   
        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.spinpol, value = ["unpolarized","spin_polarized", "spinors"])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=210)
        self.entry_pol_x['state'] = 'readonly'

        self.Frame2_note = tk.Label(self.Frame2,text="Eigen Solver",bg="gray",fg="black")
        self.Frame2_note['font'] = myFont
        self.Frame2_note.place(x=10,y=260)

        self.entry_pol_x = ttk.Combobox(self.Frame2, textvariable= self.eigen, value = self.eignsolv)
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = myFont
        self.entry_pol_x.place(x=280,y=260)
        self.entry_pol_x['state'] = 'readonly'

    def get_parameters(self):
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
            'engine':'gpaw',
            'geometry': str(self.controller.directory)+"/coordinate.xyz"
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
            'engine':'nwchem',
            'geometry': str(self.controller.directory)+"/coordinate.xyz"
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
            'unit_box' : self.unit_box.get(),
            'engine':'octopus',
            'geometry': str(self.controller.directory)+"/coordinate.xyz"
                    }

        if self.basis.get() == '':
            inp_dict_gp['basis']={}

        if self.mode.get() == 'nao':
            inp_dict_gp['mode']='lcao'

        if self.nbands.get() == '':
            inp_dict_gp['nbands']= None

        if self.shape.get() in ['minimum','sphere']:
            inp_dict_oct['box']={'shape':self.shape.get(),'radius':self.r.get()}
        if self.shape.get() == 'cylinder':
            inp_dict_oct['box']={'shape':self.shape.get(),'radius':self.r.get(),'xlength':self.l.get()}
        if self.shape.get() == 'parallelepiped':
            inp_dict_oct['box']={'shape':self.shape.get(),'sizex':self.lx.get(), 'sizey':self.ly.get(), 'sizez':self.lz.get()}

        if self.mode.get() == "gaussian":
            print(inp_dict_nw)
            return inp_dict_nw

        if self.mode.get() in ["nao","pw"]:
            print(inp_dict_gp)
            return inp_dict_gp

        if self.shape.get() in ["minimum","sphere","cylinder"]:
            print(inp_dict_oct)
            return inp_dict_oct

        if self.shape.get() == "parallelepiped":
            if self.check is False:
                print(inp_dict_oct)
                return inp_dict_oct
            else:
                print(inp_dict_gp)
                return inp_dict_gp
    
    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)
            
    def save_button(self):
        self.event_generate('<<SaveGroundStateScript>>')          

    def view_button(self):
        self.event_generate('<<ViewGroundStateScript>>')

    def run_job_button(self):
        self.event_generate('<<SubGroundState>>')


class JobSubPage(tk.Frame):

    def __init__(self, parent, task, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.task = task
        self.runlocal_np =  None
        self.run_script_path = None

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')

        self.Frame1 = tk.Frame(self)
        self.processors = tk.IntVar()
        self.ip = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.rpath = tk.StringVar()

        self.Frame1.place(relx=0.01, rely=0.01, relheight=0.25, relwidth=0.978)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        sbj_label1 = tk.Label(self.Frame1, text="LITESOPH Local Job Submission", fg='blue')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=350,y=10)

        sbj_label1 = tk.Label(self.Frame1, text="Number of processors", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=50)

        sbj_entry1 = tk.Entry(self.Frame1,textvariable= self.processors, width=20)
        self.processors.set(1)
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=50)
        
        #sbj_label1 = Label(self.Frame2, text="To submit job through Network, provide details", bg='gray', fg='black')
        #sbj_label1['font'] = myFont
        #sbj_label1.place(x=15,y=110)

        sbj_button1 = tk.Button(self.Frame1, text="Run Local",activebackground="#78d6ff",command=lambda:[self.submitjob_local()])
        sbj_button1['font'] = myFont
        sbj_button1.place(x=600, y=50)

        self.msg_label1 = tk.Label(self.Frame1, text='', fg='blue')
        self.msg_label1['font'] = myFont
        self.msg_label1.place(x=700,y=55)

        self.Frame2 = tk.Frame(self)
        self.Frame2.place(relx=0.01, rely=0.26, relheight=0.60, relwidth=0.978)
        
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(cursor="fleur")

        sbj_label1 = tk.Label(self.Frame2, text="LITESOPH Network Job Submission", fg='blue')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=340,y=10)
        
        sbj_label1 = tk.Label(self.Frame2, text= "Host IP address", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=50)
 
        sbj_entry1 = tk.Entry(self.Frame2,textvariable= self.ip, width=20)
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=50)

        sbj_label1 = tk.Label(self.Frame2, text= "User Name", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=100)

        sbj_entry1 = tk.Entry(self.Frame2,textvariable= self.username, width=20)
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=100)
 
        sbj_label1 = tk.Label(self.Frame2, text= "Password", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=150)

        sbj_entry1 = tk.Entry(self.Frame2,textvariable= self.password, width=20, show = '*')
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=150)

        sbj_label1 = tk.Label(self.Frame2, text= "Remote Path", bg='gray', fg='black')
        sbj_label1['font'] = myFont
        sbj_label1.place(x=15,y=200)

        sbj_entry1 = tk.Entry(self.Frame2,textvariable= self.rpath, width=20)
        sbj_entry1['font'] = l
        sbj_entry1.place(x=200,y=200)
      
        #sbj_button2 = Button(self.Frame2, text="Create Job Script",activebackground="#78d6ff")
        #sbj_button2['font'] = myFont
        #sbj_button2.place(x=600, y=60)
         
        #sbj_button2 = Button(self.Frame2, text="Upload Job Script",activebackground="#78d6ff",command =lambda:[self.open_file(self.controller.directory),show_message(self.message_label,"Uploaded")])
        sbj_button2 = tk.Button(self.Frame2, text="Upload Job Script",activebackground="#78d6ff",command = self.upload_script)
        sbj_button2['font'] = myFont
        sbj_button2.place(x=600, y=150)
  
        self.message_label = tk.Label(self.Frame2, text='', foreground='red')
        self.message_label['font'] = myFont
        self.message_label.place(x=800,y=155)

        sbj_button2 = tk.Button(self.Frame2, text="Run Job Network",activebackground="#78d6ff", command=lambda:[self.submitjob_network()])
        sbj_button2['font'] = myFont
        sbj_button2.place(x=600, y=200)
 
        self.Frame3 = tk.Frame(self)
        self.Frame3.place(relx=0.01, rely=0.86, relheight=0.12, relwidth=0.978)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")

        back2prev = tk.Button(self.Frame3, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ClickBackButton>>'))
        back2prev['font'] = myFont
        back2prev.place(x=15,y=10)

        back = tk.Button(self.Frame3, text="Back to main page",activebackground="#78d6ff",command=lambda:[self.event_generate('<<ShowWorkManagerPage>>')])
        back['font'] = myFont
        back.place(x=600,y=10)              

    def get_processors(self):
        return self.processors.get()

    def submitjob_local(self):
        event = '<<Run'+self.task+'Local>>'
        self.event_generate(event)
    #     if self.controller.check is not True:
    #         from litesoph.utilities.job_submit import get_submit_class
    #         self.submit = get_submit_class(engine=self.task.engine, configs=self.controller.lsconfig, nprocessors=self.processors.get())
    #         process = self.task.run(self.submit)
    #     else:
    #         from litesoph.gui.job_validation import select_job
    #         job = self.checkjob()
    #         select_job(self,job, self.controller.status)     
        

    # def checkjob(self):
    #     try:
    #         if type(self.controller.task).__name__ == 'GroundState':
    #             return('gs')
    #         if type(self.controller.task).__name__ == 'RT_LCAO_TDDFT':
    #             return self.controller.task.keyword  
    #         if type(self.controller.task).__name__ == 'Spectrum':
    #             return('spec')
    #         if type(self.controller.task).__name__ == 'TCM':
    #             return('tcm')
    #         if type(self.controller.task).__name__ == 'InducedDensity':
    #             return('indensity')
    #     except:
    #         messagebox.showerror(message="Input not created!. Please create input before submitting the job ")

    # def call_run(self,key, value):
    #     from litesoph.utilities.job_submit import get_submit_class
    #     self.submit = get_submit_class(engine=self.task.engine, configs=self.controller.lsconfig, nprocessors=self.processors.get())
    #     process = self.task.run(self.submit)
    #     f = tk.file_check(self.job_d['check_list'], self.controller.directory) 
    #     f_check = f.check_list(self.job_d['out']) 
    #     if f_check is True:
    #         self.controller.status.update_status(key, value) 
    #         show_message(self.msg_label1,"Job Done")
    #     else:
    #         show_message(self.msg_label1, "Error while generating output") 
            
   
    # def run_job(self, key, value1, value2):
    #     if self.job_d['cal_check'] is False:
    #         self.call_run(key, value1)  
    #     else:
    #         show_message(self.msg_label1, "")
    #         check_yn = messagebox.askyesno(title="Job is done",message="Do you want to redo the calculation? ")
    #         if check_yn is True:
    #             self.controller.status.update_status(key, value2)
    #             self.call_run(key, value1)

    def upload_script(self):

        top1 = tk.Toplevel()
        top1.geometry("600x500")
        top1.title("LITESOPH Job Script Viewer")

        cores_1 = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        text_scroll =tk.Scrollbar(top1) 
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        my_Text = tk.Text(top1, width = 78, height = 25, yscrollcommand= text_scroll.set)
        my_Text['font'] = myFont
        my_Text.place(x=15,y=60)
        #if selectedfile is not None:
            #self.inserttextfromfile(selectedfile, my_Text)
            #self.current_file = selectedfile

        text_scroll.config(command= my_Text.yview)
        
        #def inserttextfromfile(self, filename, my_Text):
            #text_file = open(filename, 'r')
            #stuff = text_file.read()
            #my_Text.insert(END,stuff)
            #text_file.close()

        view = tk.Button(top1, text="Select Script",activebackground="#78d6ff",command=lambda:[self.open_txt(my_Text)])
        view['font'] = myFont
        view.place(x=100,y=450)

        save = tk.Button(top1, text="Save",activebackground="#78d6ff",command=lambda:[self.save_txt(my_Text)])
        save['font'] = myFont
        save.place(x=280, y=450)
        
        close = tk.Button(top1, text="Close", activebackground="#78d6ff",command=top1.destroy)
        close['font'] = myFont
        close.place(x=400,y=450)
        
    def open_txt(self,my_Text):
            self.run_script_path = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=(("All files","*.*"),))
            #text_file_name = open_file(user_path) 
            self.current_file = self.run_script_path
            text_file = open(self.run_script_path, 'r')
            stuff = text_file.read()
            my_Text.insert(tk.END,stuff)
            text_file.close()     

    def save_txt(self,my_Text):
            text_file = self.current_file
            text_file = open(text_file,'w')
            text_file.write(my_Text.get(1.0, tk.END))
    
    def submitjob_network(self):
        event = '<<Run'+self.task+'Network>>'
        self.event_generate(event)
        
    def get_network_dict(self):

        network_job_dict = {
          'ip':self.ip.get(),
          'username':self.username.get(),
          'password':self.password.get(),
          'remote_path':self.rpath.get(),
            } 
        return network_job_dict

class TextViewerPage(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.save_txt = None
        self.task_name = None
        myFont = tk.font.Font(family='Helvetica', size=10, weight='bold')

        j=tk.font.Font(family ='Courier', size=20,weight='bold')
        k=tk.font.Font(family ='Courier', size=40,weight='bold')
        l=tk.font.Font(family ='Courier', size=15,weight='bold')

        self.Frame = tk.Frame(self)

        self.Frame.place(relx=0.01, rely=0.01, relheight=0.99, relwidth=0.98)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
  
        self.FrameTcm1_label_path = tk.Label(self, text="LITESOPH Text Viewer",fg="blue")
        self.FrameTcm1_label_path['font'] = myFont
        self.FrameTcm1_label_path.place(x=400,y=10)

        
        text_scroll =tk.Scrollbar(self)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_view = tk.Text(self, width = 130, height = 20, yscrollcommand= text_scroll.set)
        self.text_view['font'] = myFont
        self.text_view.place(x=15,y=60)

        text_scroll.config(command= self.text_view.yview)

        save = tk.Button(self, text="Save",activebackground="#78d6ff",command=self.save)
        save['font'] = myFont
        save.place(x=320, y=380)

        back = tk.Button(self, text="Back",activebackground="#78d6ff",command=lambda:[self.back_button()])
        back['font'] = myFont
        back.place(x=30,y=380)
    
    def set_task_name(self, name):
        self.task_name = name
   
    def insert_text(self, text):
        self.text_view.insert(tk.END, text)
 
    def save(self):
        self.save_txt = self.text_view.get(1.0, tk.END)
        self.event_generate(f'<<Save{self.task_name}>>')
    
    def back_button(self):
        self.event_generate(f'<<View{self.task_name}Page>>')
