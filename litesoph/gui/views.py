import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from  PIL import Image,ImageTk
from tkinter import font

import pathlib

from litesoph.gui import images
from litesoph.simulations.project_status import show_message
from litesoph.gui.input_validation import Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15
from litesoph.simulations.models import AutoModeModel
from litesoph.gui.engine_views import get_gs_engine_page

########## tooltip description ###########
from litesoph.gui import tooltipdoc
from idlelib.tooltip import Hovertip


class StartPage(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
       
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

        #parent.configure(bg="grey60")

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

        image = Image.open(images.LITESOPH_LOGO_BIG)
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((125, 125), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        # create a canvas to show project list icon
        canvas_for_project_create=tk.Canvas(mainframe, bg='gray', height=50, width=50, borderwidth=0, highlightthickness=0)
        canvas_for_project_create.place(x=20,y=200)

        image_project_create = Image.open(images.PROJECT_CREATE_ICON)
        canvas_for_project_create.image = ImageTk.PhotoImage(image_project_create.resize((50,50), Image.ANTIALIAS))
        canvas_for_project_create.create_image(0,0, image=canvas_for_project_create.image, anchor='nw')

        button_create_project = tk.Button(mainframe,text="Start LITESOPH Project", activebackground="#78d6ff",command=lambda: self.event_generate('<<ShowWorkManagerPage>>'))
        button_create_project['font'] = myFont
        button_create_project.place(x=80,y=200)

        #button_open_project = Button(mainframe,text="About LITESOPH",fg="white")
        button_open_project = tk.Button(mainframe,text="About LITESOPH")
        button_open_project['font'] = myFont
        button_open_project.place(x=80,y=300)

class WorkManagerPage(ttk.Frame):

    MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]
    Pre_task = ["Ground State"]
    Sim_task = ["Delta Kick","Gaussian Pulse"]
    Post_task = ["Compute Spectrum","Kohn Sham Decomposition","Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]
    engine_list = ['auto-mode','gpaw', 'nwchem', 'octopus']

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
               
        self._default_var = {
            'proj_path' : ['str'],
            'proj_name' : ['str'],
            'task' : ['str', '--choose job task--'],
            'sub_task' : ['str'],
            'dynamics': ['str','--dynamics type--'],
            'laser': ['str','-- laser type--'],
            'plot':['str', '-- choose option --'],
        }
        self.parent = parent
        self.engine = tk.StringVar(value='auto-mode')

        self._var = var_define(self._default_var)
        label_design.update({"font":myfont()})
        
        self.plot_option = None

        self.Frame1 =ttk.Frame(self)
        self.Frame1.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
       
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(cursor="fleur")

        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=2)

        self.label_proj = tk.Label(self.Frame1,text="Project Name",bg=label_design['bg'],fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(column=0, row= 0, sticky=tk.W,  pady=10, padx=10)        
        
        self.entry_proj = tk.Entry(self.Frame1,textvariable=self._var['proj_name'])
        self.entry_proj['font'] = myfont()
        self.entry_proj.grid(column=1, row= 0, sticky=tk.W)
        self.entry_proj.delete(0, tk.END)
                
        self.button_project = tk.Button(self.Frame1,text="Create New Project",width=18, activebackground="#78d6ff",command=self._create_project)
        self.button_project['font'] = myfont()
        self.button_project.grid(column=2, row= 0, sticky=tk.W, padx= 10, pady=10)        
        
        self.button_project = tk.Button(self.Frame1,text="Open Existing Project",activebackground="#78d6ff",command=self._open_project)
        self.button_project['font'] = myfont()
        self.button_project.grid(column=2, row= 2, sticky=tk.W, padx= 10, pady=10)

        self.Frame2 = ttk.Frame(self)
        self.Frame2.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        # self.grid_columnconfigure(1, weight=1)

        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(cursor="fleur")

        common_frame = ttk.Frame(self.Frame2)
        common_frame.grid(row=0, column=0, sticky='w')

        self.Frame2_label_1 = tk.Label(common_frame, text="Upload Geometry",bg=label_design['bg'],fg=label_design['fg'])  
        self.Frame2_label_1['font'] = myfont()
        self.Frame2_label_1.grid(column=0, row= 0, sticky='w', padx=4,  pady=10)    
        myTip_Frame2_label_1 = Hovertip(self.Frame2_label_1, tooltipdoc.upload_geometry_doc)   

        self.Frame2_Button_1 = tk.Button(common_frame,text="Select",activebackground="#78d6ff",command=self._get_geometry_file)
        self.Frame2_Button_1['font'] = myfont()
        self.Frame2_Button_1.grid(column=1, row= 0, padx=10,  pady=10)
        myTip_Frame2_Button_1 = Hovertip(self.Frame2_Button_1,tooltipdoc.select_geometry_doc)       

        self.message_label = tk.Label(common_frame, text='', foreground='red')
        self.message_label['font'] = myfont()
        self.message_label.grid(column=2, row= 0, padx=10,  pady=10)       
        
        self.Frame2_Button_1 = tk.Button(common_frame,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.Frame2_Button_1['font'] = myfont()
        self.Frame2_Button_1.grid(column=3, row= 0, padx=10,  pady=10)

        self.engine_source_label = tk.Label(common_frame,text="Source",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        self.engine_source_label['font'] = myfont()
        self.engine_source_label.grid(row= 1, column=0,  sticky='w',padx=4, pady=10)   
        myTip_engine_source_label = Hovertip(self.engine_source_label, tooltipdoc.engine_source_doc)    
            
        self.engine_source = ttk.Combobox(common_frame,width=20, textvariable= self.engine, values= self.engine_list)
        self.engine_source['font'] = myfont()
        self.engine_source.grid(row= 1, column=1, columnspan=2, padx=4, pady=10)
        self.engine_source['state'] = 'readonly'

        self.label_proj = tk.Label(common_frame,text="Job Type",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        self.label_proj['font'] = myfont()
        self.label_proj.grid(row= 2, column=0,  sticky='w', padx=4, pady=10) 
        myTip_label_proj = Hovertip(self.label_proj, tooltipdoc.jobtype_doc)    
      
            
        self.entry_task = ttk.Combobox(common_frame,width=20, textvariable= self._var['task'], values= self.MainTask)
        self.entry_task['font'] = myfont()
        self.entry_task.grid(row= 2, column=1, columnspan=2, padx=4, pady=10)
       
        self.entry_task.bind("<<ComboboxSelected>>", self.pick_task)
        self.entry_task['state'] = 'readonly'

        self.sub_task_frame = ttk.Frame(self.Frame2)
        self.sub_task_frame.grid(row=1, column=0, sticky='w')
        

        self.show_sub_task_frame(self.sub_task_frame)
       
        self.Frame3 = ttk.Frame(self)
        self.Frame3.grid(column=0, row=2,  sticky=(tk.N, tk.W, tk.E, tk.S)) 

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(cursor="fleur")

        Frame3_Button1 = tk.Button(self.Frame3, text="Proceed",activebackground="#78d6ff",command=self.proceed_button)
        Frame3_Button1['font'] = myfont()
        Frame3_Button1.pack(side=tk.RIGHT, padx=10)
        self.show_sub_task_frame(self.sub_task_frame)

        self.Frame_status = ttk.Frame(self)
        self.Frame_status.grid(row=0, column=1, rowspan=2, sticky='nsew') 
        self.Frame_status.configure(relief='groove', borderwidth="2", cursor="fleur" )

    def show_sub_task_frame(self,parent):

        for widget in parent.winfo_children():
            widget.destroy()

        common_sub_task_frame = ttk.Frame(parent)        
        common_sub_task_frame.grid(row=0, column=0)  

        self.Frame2_label_3 = tk.Label(common_sub_task_frame, text="Sub Task",bg=label_design['bg'],fg=label_design['fg'])
        self.Frame2_label_3['font'] = myfont()
        self.Frame2_label_3.grid( row= 0,column=0, sticky='nswe', padx=4, pady=10) 
        myTip_Frame2_label_3 = Hovertip(self.Frame2_label_3, tooltipdoc.subtask_doc)    

        
        self.entry_sub_task = ttk.Combobox(common_sub_task_frame, width= 20, textvariable=self._var['sub_task'], value = [''])
        self.entry_sub_task['font'] = myfont()
        self.entry_sub_task.current(0)
        self.entry_sub_task.grid(row= 0, column=1, sticky='nswe',  pady=10, padx=68)       
        self.entry_sub_task['state'] = 'readonly'  

        self.entry_sub_task.bind("<<ComboboxSelected>>", self.pick_sub_task)
        self.entry_sub_task['state'] = 'readonly'       
           

    def show_sim_task_frame(self, parent):

        for widget in parent.winfo_children():
            widget.destroy()

        sim_sub_task_frame = ttk.Frame(parent)
        sim_sub_task_frame.grid(row=1, column=0)

        self.sub_task_label = tk.Label(sim_sub_task_frame, text="Sub Task",bg=label_design['bg'],fg=label_design['fg'])
        self.sub_task_label['font'] = myfont()
        self.sub_task_label.grid(column=0, row= 0, sticky='nswe', padx=4, pady=10)        
          
        self.dynamics_type = ttk.Combobox(sim_sub_task_frame, width= 15, textvariable=self._var['dynamics'], value = ['electrons', 'electron+ion','ions'])
        self.dynamics_type['font'] = myfont()
        self.dynamics_type.set('--dynamics type--')
        self.dynamics_type.grid(column=1, row= 0, sticky='nsew',  pady=10, padx=65)       
        self.dynamics_type['state'] = 'readonly'  

        self.laser_type = ttk.Combobox(sim_sub_task_frame, width= 13, textvariable=self._var['laser'], value = ['None', 'Delta Pulse', 'Gaussian Pulse', 'Customised Pulse'])
        self.laser_type['font'] = myfont()
        self.laser_type.set('-- laser type--')
        self.laser_type.grid(column=2, row= 0, sticky='nsew',  pady=10, padx=6)       
        self.laser_type['state'] = 'readonly'       

    def show_plot_option_frame(self, parent):
        
        self.plot_option = ttk.Combobox(parent, width= 15, textvariable=self._var['plot'], value = ['Spectrum', 'Dipole Moment', 'Laser'])
        self.plot_option['font'] = myfont()
        self.plot_option.set('--choose option--')
        self.plot_option.grid(column=1, row= 0, sticky='nsew', pady=10, padx=3)       
        self.plot_option['state'] = 'readonly'

    def pick_task(self, *_):
        if self._var['task'].get() == "Preprocessing Jobs":
            self.show_sub_task_frame(self.sub_task_frame)
            self.entry_sub_task.config(value = self.Pre_task)
            self.entry_sub_task.current(0)
        elif self._var['task'].get() == "Simulations":
            self.show_sim_task_frame(self.sub_task_frame)
                # self.entry_sub_task.config(value = self.Sim_task)
                # self.entry_sub_task.current(0)
        elif self._var['task'].get() == "Postprocessing Jobs":
            self.show_sub_task_frame(self.sub_task_frame)
            self.entry_sub_task.config(value = self.Post_task)
            self.entry_sub_task.current(0)                

    def pick_sub_task(self,*_):
        if self._var['sub_task'].get() == "Plot":
            self.show_plot_option_frame(self.sub_task_frame)
        else:
            if self.plot_option:
                self.plot_option.destroy()    
            
    def update_project_entry(self, proj_path):
        proj_path = pathlib.Path(proj_path)
        self._var['proj_path'].set(proj_path.parent)
        self.entry_path.config(textvariable=self._var['proj_path'])
        self._var['proj_name'].set(proj_path.name)
        self.entry_proj.config(textvariable=self._var['proj_name'])

    def _open_project(self):
        self.event_generate('<<OpenExistingProject>>')

    def _create_project(self):
        self.event_generate('<<CreateNewProject>>')

    def _get_geometry_file(self):
        self.event_generate('<<GetMolecule>>')
        
    def _geom_visual(self):
        self.event_generate('<<VisualizeMolecule>>')

    def proceed_button(self):
        """ event generate on proceed button"""

        self.event_generate('<<SelectProceed>>')   

    def show_upload_label(self):
        show_message(self.message_label,"Uploaded")

    def get_value(self, key):
        return self._var[key].get()

    def set_value(self,key,value):
        self._var[key].set(value)
        
    def refresh_var(self):
        for key, value in self._default_var.items():
            try:
                self._var[key].set(value[1])
            except IndexError:
                self._var[key].set('')    

def var_define(var_dict:dict):
    var_def_dict ={}
    for key, type_value in var_dict.items():
        type = type_value[0]
        try:
            value = type_value[1]
            if type == 'str':
                var ={ key : tk.StringVar(value=value)}
            elif type == 'int':
                var ={ key : tk.IntVar(value=value)}
            elif type == 'float':
                var ={ key : tk.DoubleVar(value=value)}
        except IndexError:
            if type == 'str':
                var ={ key : tk.StringVar()}
            elif type == 'int':
                var ={ key : tk.IntVar()}
            elif type == 'float':
                var ={ key : tk.DoubleVar()}   
         
        var_def_dict.update(var)

    return var_def_dict

def define_tk_var(var_dict:dict):
    from litesoph.lsio.data_types import DataTypes as DT
    var_def_dict ={}
    var_type = {
        DT.boolean : tk.BooleanVar,
        DT.integer : tk.IntVar,
        DT.string : tk.StringVar,
        DT.decimal : tk.DoubleVar
    }
    for key, value in var_dict.items():
        #type = value['type']
        
        vtype = var_type.get(value['type'], tk.StringVar)
        try:
            v = value['default_value']
        except KeyError:
            v = ''
        var_def_dict[key] = vtype(value=v)   

    return var_def_dict
        

class View_note(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.job = None

        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')
        style = ttk.Style()
        notebook = ttk.Notebook(self)
        notebook.grid()
        style.configure("TNotebook.Tab", font=('Helvetica','10'))
        #style.map("TNotebook.Tab", background=[('selected')])
        
        self.Frame1 = ttk.Frame(notebook, borderwidth=2, relief='groove')
        self.Frame2 = ttk.Frame(notebook, borderwidth=2, relief='groove')
        self.Frame3 = ttk.Frame(notebook, borderwidth=2, relief='groove')

        self.Frame1.grid(row=0, column=0)
        self.Frame2.grid(row=0, column=0)
        self.Frame3.grid(row=0, column=0)

        notebook.add(self.Frame1, text='System')
        notebook.add(self.Frame2, text='Calculation Details')
        notebook.add(self.Frame3, text='Advanced Info')

        self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button.grid(row=10, column=0,columnspan=10, sticky='nswe')

    def add_jobsub(self):
        """ Adds Job Sub buttons to View_note"""

        self.frame_run = ttk.Frame(self,borderwidth=2, relief='groove')
        self.frame_run.grid(row=0, column=1, sticky='nsew')

        self.sublocal_Button2 = tk.Button(self.frame_run, text="Submit Local", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubLocalGroundState>>'))
        self.sublocal_Button2['font'] = myfont()
        self.sublocal_Button2.grid(row=1, column=2,padx=2, pady=6, sticky='nsew')
        
        self.subnet_Button3 = tk.Button(self.frame_run, text="Submit Network", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubNetworkGroundState>>'))
        self.subnet_Button3['font'] = myfont()
        self.subnet_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')
        
    def set_sub_button_state(self,state):
        self.sublocal_Button2.config(state=state)
        self.subnet_Button3.config(state=state)


class GroundStatePage(View_note):
  
    
    def __init__(self, parent,engine,*args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.parent = parent
        self.engine = tk.StringVar(value=engine)
        self.engine.trace_add('write', self.on_engine_change)
        self.job = None

        self.add_jobsub()
        self.frame_collection()
        self.on_engine_change()
        
    def on_engine_change(self, *_):
    
        f_list = [self.Frame1_sub.winfo_children, 
                self.Frame2_sub.winfo_children,
                self.Frame3_sub.winfo_children]

        for frame in f_list:
            for widget in frame():
                widget.destroy()

        if self.engine.get() == 'auto-mode':
            self.gs_dict = AutoModeModel.ground_state
            self._var = define_tk_var(self.gs_dict)
            self.show_system_tab(self.Frame1_sub)
            return

        self.engine_page = get_gs_engine_page(self.engine.get(), self)
        self.gs_dict = self.engine_page.default_para
        self._var = self.engine_page._var = define_tk_var(self.gs_dict)
        self.engine_page.create_input_widgets()

    def tab1_button_frame(self):

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.Frame1_Button1 = tk.Button(self.frame_button, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.Frame1_Button1['font'] = myFont
        self.Frame1_Button1.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

    def tab2_button_frame(self):
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.view_Button2 = tk.Button(self.frame_button, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.view_Button2['font'] = myFont
        self.view_Button2.grid(row=0, column=2,padx=3, pady=3,sticky='nsew')
        
        self.save_Button3 = tk.Button(self.frame_button, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.save_Button3['font'] = myFont
        self.save_Button3.grid(row=0, column=4, padx=3, pady=3,sticky='nsew')

        self.label_msg = tk.Label(self.frame_button,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=3, sticky='nsew')

    def show_system_tab(self, parent):
        """ Creates widgets for system tab inputs"""

        for widget in parent.winfo_children():
            widget.destroy()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=0, column=0)      

        self.heading = tk.Label(mode_frame,text="LITESOPH input for Ground State",fg='green')
        self.heading['font'] = myfont15()
        self.heading.grid(row=0, column=0, pady=5)
                
        self.label_proj = tk.Label(mode_frame,text="Mode",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(row=2, column=0, sticky='w', padx=2, pady=4)
        myTip_label_proj = Hovertip(self.label_proj,  self.gs_dict['mode']['tooltipdoc'])   

        

        def pick_box(e):
            if task.get() == "nao" or task.get() == 'pw':
                #check = messagebox.ask(title = 'Message',message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
                self.engine.set('gpaw')
            elif task.get() == "gaussian":
                self.engine.set('nwchem')
            elif task.get() == "fd":
                for widget in self.Frame2_sub.winfo_children():
                    widget.destroy()
                self.show_auto_mode_calc_tab(self.Frame2_sub) 

        task = ttk.Combobox(mode_frame, textvariable = self._var['mode'], values= self.gs_dict['mode']['values'])
        task['font'] = label_design['font']
        task.grid(row=2, column= 1, sticky='w', padx=2, pady=2)
        task.bind("<<ComboboxSelected>>", pick_box)
        task['state'] = 'readonly'

        
        self.basis = tk.Label(mode_frame, text="Basis",bg=label_design['bg'], fg=label_design['fg'])
        self.basis['font'] = label_design['font']
        self.basis.grid(row=4, column=0, sticky='w', padx=2, pady=4)
        # myTip_basis = Hovertip(self.basis, self.gs_dict['mode']['tooltipdoc'])   
        myTip_basis = Hovertip(self.basis, self.gs_dict['basis']['tooltipdoc'])   



        sub_task = ttk.Combobox(mode_frame, textvariable= self._var['basis'], value = self.gs_dict['basis']['values'])
        sub_task['font'] = label_design['font']
        sub_task.grid(row=4, column=1, sticky='w', padx=2, pady=2)
        sub_task['state'] = 'readonly'

        self.charge = tk.Label(mode_frame, text="Charge",bg=label_design['bg'], fg=label_design['fg'])
        self.charge['font'] = label_design['font']
        self.charge.grid(row=6, column=0, sticky='w', padx=2, pady=4)
        myTip_charge = Hovertip(self.charge, self.gs_dict['charge']['tooltipdoc'])   

        

        self.entry_chrg = Onlydigits(mode_frame,textvariable=self._var['charge'])
        self.entry_chrg['font'] = label_design['font']
        self.entry_chrg.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        self.multiplicity_label = tk.Label(mode_frame, text='Multiplicity',bg=label_design['bg'], fg=label_design['fg'])
        self.multiplicity_label['font'] = label_design['font']
        self.multiplicity_label.grid(row=7, column=0, sticky='w', padx=2, pady=4)
        myTip_multiplicity_label = Hovertip(self.multiplicity_label, self.gs_dict['multip']['tooltipdoc'])   

        

        multiplicity_entry = Onlydigits(mode_frame,textvariable= self._var['multip'])
        multiplicity_entry['font'] =label_design['font']
        multiplicity_entry.grid(row=7, column=1, sticky='w', padx=2, pady=2)

    def show_auto_mode_calc_tab(self, parent):
        """ Creates widgets for fd mode in second tab"""

        common_frame = ttk.Frame(parent)
        common_frame.grid(row=0, column=0, sticky='nsew')

        sub_frame = ttk.Frame(parent)
        sub_frame.grid(row=1, column=0, sticky='nsew')

        self.shape = tk.Label(common_frame,text="Box Shape", justify='left', bg=label_design['bg'], fg=label_design['fg'])
        self.shape['font'] = label_design['font']
        self.shape.grid(row=0, column=0, sticky='nsew', padx=10, pady=4)

        def pick_frame(*_):
            if self.box_shape.get() == "parallelepiped":
                check = messagebox.askyesno(title = 'Message',message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
                if check is True:
                    self.engine.set('gpaw')
                elif check is False:
                    self.engine.set('octopus')
                else:
                    return
            elif self.box_shape.get() in ["minimum","sphere","cylinder"] : 
                self.engine.set('octopus')
            
        self.box_shape = ttk.Combobox(common_frame, textvariable= self._var['shape'], value =self.gs_dict['shape']['values'])
        self.box_shape['font'] = label_design['font']
        self.box_shape.bind("<<ComboboxSelected>>", pick_frame)
        self.box_shape['state'] = 'readonly'
        self.box_shape.grid(row=0, column=1, sticky='w', padx=10, pady=2) 

    def back_button(self):
        self.event_generate('<<ShowWorkManagerPage>>')              

    def frame_collection(self):
        self.Frame1_sub = ttk.Frame(self.Frame1, borderwidth=2)
        self.Frame1_sub.grid(row=0, column=0, rowspan=11, columnspan=10, sticky='we')
        self.Frame2_sub = ttk.Frame(self.Frame2, borderwidth=2)
        self.Frame2_sub.grid(row=0, column=0, rowspan=11, columnspan=10, sticky= 'we') 
        self.Frame3_sub = ttk.Frame(self.Frame3, borderwidth=2)
        self.Frame3_sub.grid(row=0, column=0, rowspan=11, columnspan= 10, sticky='we')
        
        self.tab1_button_frame()
        self.tab2_button_frame()

    def get_parameters(self):

        if self.engine.get() == "auto-mode":
            messagebox.showwarning(title='Warning', message='Please choose the engine before proceeding')
            return 
        return self.engine_page.get_parameters()
       
    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)
            
    def save_button(self):
        self.event_generate('<<SaveGroundStateScript>>')          

    def generate_input_button(self):
        self.event_generate('<<GenerateGroundStateScript>>')

    def run_job_button(self):
        self.event_generate('<<SubGroundState>>')

    def refresh_var(self):
        for key, value in self.gs_dict.items():
            try:
                self._var[key].set(value['default_value'])
            except KeyError:
                self._var[key].set('')     

    def read_atoms(self, geom_xyz):
        from ase.io import read
        atoms = read(geom_xyz)
        atom_list = list(atoms.symbols)
        return atom_list

class View1(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #self.controller = controller
        self.parent = parent
        self.job = None

        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.Frame1 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame2 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame3 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        # layout all of the main containers
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_rowconfigure(1, weight=8)
        self.grid_columnconfigure(9, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(5, weight=5)
        #self.grid_rowconfigure(2, weight=3)
        #self.grid_columnconfigure(8, weight=1)

        self.Frame1.grid(row=1,column=0, columnspan=4, rowspan=100, sticky='nsew')
        self.Frame2.grid(row=1, column=5, rowspan=100,columnspan=2, sticky='nsew')
        self.Frame3.grid(row=0, column=5,columnspan=5, sticky='nswe')
        #self.Frame2.grid(row=4,  sticky="nsew")
        # btm_frame.grid(row=3, sticky="ew")
        # btm_frame2.grid(row=4, sticky="ew")
        
        self.frame_button.grid(row=101, column=0,columnspan=5, sticky='nswe')

    def add_job_frame(self, task_name):  
        """  Adds submit job buttons to View1"""

        self.Frame3 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame3.grid(row=1, column=9, sticky='nswe')
        # View_Button1 = tk.Button(self.Frame3, text="View Output", activebackground="#78d6ff", command=lambda: [self.view_button()])
        # View_Button1['font'] = self.myFont
        # View_Button1.grid(row=2, column=1, sticky='nsew')

        self.sublocal_Button2 = tk.Button(self.Frame3, text="Submit Local", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubLocal'+task_name+'>>'))
        self.sublocal_Button2['font'] = myfont()
        self.sublocal_Button2.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
        
        self.subnet_Button3 = tk.Button(self.Frame3, text="Submit Network", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubNetwork'+task_name+'>>'))
        self.subnet_Button3['font'] = myfont()
        self.subnet_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')

    def set_sub_button_state(self,state):
        self.sublocal_Button2.config(state=state)
        self.subnet_Button3.config(state=state)

class TimeDependentPage(View1):

    def __init__(self, parent, engine, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)

        self.parent = parent
        self.engine = engine
        self.job = None

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
          
        self._default_var = {
            'strength': ['float', 1e-5],
            'pol_var' : ['int', 0],
            'dt': ['float'],
            'Nt': ['int'],
            'spectra': ['int', 1],
            'avg_spectra' : ['int', 0],
            'ksd': ['int',0],
            'popln': ['int',0],
            'prop': ['int',0],
            'elec': ['int',0],
            'output_freq': ['int']
        }
        self.gpaw_td_default = {
            'dt': ['float', 10],
            'Nt': ['int', 2000],
            'output_freq': ['int', 1]
        }
        self.oct_td_default = {
            'dt': ['float', 2.4],
            'Nt': ['int', 1500],
            'output_freq': ['int', 50]
        }
        self.nwchem_td_default = {
            'dt': ['float', 2.4],
            'Nt': ['int', 2000],
            'output_freq': ['int', 50]
        }
        self._var = var_define(self._default_var)
        
        self.Frame1_label_path = tk.Label(
            self, text="LITESOPH input for Delta Kick", fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.grid(row=0, column=3)
        # self.Frame1_label_path.place(x=150,y=10)

        self.label_proj = tk.Label(
            self.Frame1, text="Laser strength in a.u", bg="gray", fg="black", justify='left')
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=2, column=0, sticky='w', padx=5, pady=5)
        # self.label_proj.place(x=10,y=60)

        inval = ["1e-5", "1e-4", "1e-3"]
        self.entry_inv = ttk.Combobox(
            self.Frame1, textvariable=self._var['strength'], value=inval)
        self.entry_inv['font'] = myFont
        # self.entry_inv.place(x=280,y=60)
        self.entry_inv.grid(row=2, column=1)
        self.entry_inv['state'] = 'readonly'

        self.label_proj = tk.Label(
            self.Frame1, text="Propagation time step (in attosecond)", bg="gray", fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=3, column=0, sticky='w', padx=2, pady=4)

        #self.entry_proj = tk.Entry(self.Frame1,textvariable= self._var['dt'])
        self.entry_dt = Decimalentry(self.Frame1, textvariable=self._var['dt'])
        self.entry_dt['font'] = myFont
        self.entry_dt.grid(row=3, column=1, ipadx=2, ipady=2)

        self.label_proj = tk.Label(
            self.Frame1, text="Total time steps", bg="gray", fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        #self.entry_proj = tk.Entry(self.Frame1,textvariable= self._var['Nt'])
        self.entry_nt = Onlydigits(self.Frame1, textvariable=self._var['Nt'])
        self.entry_nt['font'] = myFont
        self.entry_nt.grid(row=4, column=1, ipadx=2, ipady=2)

        #################################################################################################

        frame_property = ttk.Frame(self.Frame2)
        frame_property.grid(row=0, column=0)

        frame_additional = ttk.Frame(self.Frame1)
        frame_additional.grid(row=8, column=0, pady=10)

        self.property_note = tk.Label(frame_property, text="Note: Please choose properties to be extracted in post-processing", fg="black")
        self.property_note['font'] = myFont
        self.property_note.grid(row=0, column=0)

        self.checkbox_spectra = tk.Checkbutton(frame_property, text="Absorption Spectrum", variable=self._var['spectra'], font=myFont, onvalue=1)
        self.checkbox_spectra.grid(row=1, column=0, ipady=5, sticky='w')
        
        frame_spec_option = ttk.Frame(frame_property)
        frame_spec_option.grid(row=2, column=0, sticky='w')

        # self.checkbox_specific_spectra = tk.Checkbutton(frame_spec_option, text="Specific Polarisation", font=myFont, onvalue=1, offvalue=0)
        # self.checkbox_specific_spectra.grid(row=0, column=0, ipady=5, sticky='w')

        # self.checkbox_avg_spectra = tk.Checkbutton(frame_spec_option, text="Averaged over (X,Y,Z) direction", variable=self._var['avg_spectra'], font=myFont, onvalue=1, offvalue=0)
        # self.checkbox_avg_spectra.grid(row=0, column=0, sticky='w', padx=20)                  
       
        self.checkbox_ksd = tk.Checkbutton(frame_property, text="Kohn Sham Decomposition", variable=self._var['ksd'], font=myFont, onvalue=1, offvalue=0)
        self.checkbox_ksd.grid(row=3, column=0, ipady=5, sticky='w')
       
        self.checkbox_pc = tk.Checkbutton(frame_property, text="Population Correlation", variable=self._var['popln'], font=myFont, onvalue=1, offvalue=0)
        self.checkbox_pc.grid(row=4, column=0, ipady=5, sticky='w')

        frame_output_freq = ttk.Frame(frame_property)
        frame_output_freq.grid(row=5, column=0, sticky='w')

        self.Frame2_lab = tk.Label(frame_output_freq, text="Frequency of data collection", fg="black")
        self.Frame2_lab['font'] = myFont
        self.Frame2_lab.grid(row=0, column=0,sticky='w')

        self.entry_out_frq = Onlydigits(frame_output_freq, textvariable=self._var['output_freq'], width=5)
        self.entry_out_frq['font'] = myFont
        self.entry_out_frq.grid(row=0, column=1,sticky='w')

        #######################################################################################################

        self.label_select = tk.Label(frame_additional, text="Please select polarization direction:",  bg="gray", fg="black")
        self.label_select['font'] = myFont
        self.label_select.grid(row=0, column=0, sticky='w', padx=2, pady=4)

        frame_pol = ttk.Frame(frame_additional, borderwidth=2)
        frame_pol.grid(row=1, column=0, sticky='w')

        values = {"X": 0, "Y": 1, "Z": 2}
        for (text, value) in values.items():
            tk.Radiobutton(frame_pol, text=text, variable=self._var['pol_var'], font=myfont2(),
             justify='left',value=value).grid(row=0, column=value, ipady=5, sticky='w')
        
        # label_add = tk.Label(frame_pol, text="Please add polarization vectors:", bg="gray", fg="black")
        # label_add['font'] = myFont
        # label_add.grid(row=0, column=1, sticky='w', padx=2, pady=4)

        #######################################################################################################
        
        # label_E = tk.Label(frame_pol, text="E:",  fg="black", font=myFont)
        # label_E.grid(row=1, column =0, sticky='nsew')

        # pol_list = [0, 1]
        # self.entry_pol_x = ttk.Combobox(frame_pol, textvariable=self._var['ex'], value=pol_list, width=3)
        # self.entry_pol_x['font'] = myFont
        # self.entry_pol_x.grid(row=1, column=1, padx=2, pady=2)
        # self.entry_pol_x['state'] = 'readonly'

        # self.entry_pol_y = ttk.Combobox(frame_pol, textvariable=self._var['ey'], value=pol_list, width=3)
        # self.entry_pol_y['font'] = myFont
        # self.entry_pol_y.grid(row=1, column=2, padx=2, pady=2)
        # self.entry_pol_y['state'] = 'readonly'

        # self.entry_pol_z = ttk.Combobox(frame_pol, textvariable=self._var['ez'], value=pol_list, width=3)
        # self.entry_pol_z['font'] = myFont
        # self.entry_pol_z.grid(row=1, column=3, padx=2, pady=2)
        # self.entry_pol_z['state'] = 'readonly'

        ##########################################################################################################    

        # values = {"Specific polarization direction": 2}
        # for (text, value) in values.items():
        #     tk.Radiobutton(self.Frame1, text=text, variable=self._var['var1'], font=myFont, justify='left',
        #                    value=value).grid(row=value+5, column=0, ipady=5, sticky='w')

        # Frame1_Button3 = tk.Button(frame_pol, text="Add",activebackground="#78d6ff",command=lambda:self.add_button())
        # Frame1_Button3['font'] = myFont
        # Frame1_Button3.grid(row =1, column=4, padx =5, pady=2)

        # options = [1,2,3,4]
        # options.append([self._var['ex'].get(),self._var['ez'].get()])
        # E_list = tk.Listbox(frame_pol)
        # E_list.grid(row=2, column=1)
        # for i in range(len(options)):
        #     E_list.insert(i,options[i])

        self.Frame1_Button1 = tk.Button(self.frame_button, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.Frame1_Button1['font'] = myFont
        self.Frame1_Button1.grid(row=0, column=1, sticky='nsew', padx=3, pady=3)
        self.frame_button.grid_columnconfigure(2, weight=1)
        self.frame_button.grid_columnconfigure(4, weight=1)
        self.Frame1_Button2 = tk.Button(self.frame_button, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.Frame1_Button2['font'] = myFont
        self.Frame1_Button2.grid(row=0, column=3, sticky='nsew', padx=3, pady=3)
        
        self.Frame1_Button3 = tk.Button(self.frame_button, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.Frame1_Button3['font'] = myFont
        self.Frame1_Button3.grid(row=0, column=5, sticky='nswe', padx=3, pady=3)

        self.label_msg = tk.Label(self.frame_button,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=4)

    def get_pol_list(self): 
        if self._var['pol_var'].get() == 0:
            pol_list = [1,0,0]         
        elif self._var['pol_var'].get() == 1:
            pol_list = [0,1,0] 
        elif self._var['pol_var'].get() == 2:
            pol_list = [0,0,1]                
        return pol_list

    def read_pol_dir(self):        
        if self.pol_list == [1,0,0]:
            self.pol_dir = (0,'x')
        elif self.pol_list == [0,1,0]:
            self.pol_dir = (1,'y') 
        elif self.pol_list == [0,0,1]:
            self.pol_dir = (2,'z')
        # elif self.pol_list == [1,1,0]:
        #     self.pol_dir = (3,'xy') 
        return self.pol_dir     

    def get_parameters(self):
        self.pol_list = self.get_pol_list()
        kick = [float(self._var['strength'].get())*float(self.pol_list[0]),
                float(self._var['strength'].get())*float(self.pol_list[1]),
                float(self._var['strength'].get())*float(self.pol_list[2])]
        inp_list = [float(self._var['dt'].get()),int(self._var['Nt'].get())]

        td_dict_gp = {
            'absorption_kick':kick,
            'analysis_tools':self.get_property_list(),
            'propagate': tuple(inp_list),
            'pol_dir': self.read_pol_dir(),
            'output_freq': self._var['output_freq'].get()
        }

        td_dict_oct = {
            'max_step' : self._var['Nt'].get() ,
            'time_step' : self._var['dt'].get(),
            'td_propagator' : 'aetrs',
            'strength': self._var['strength'].get(),
            'e_pol': self.pol_list,
            'pol_dir': self.read_pol_dir(),
            'output_freq': self._var['output_freq'].get(),
            'analysis_tools': self.get_property_list()
          }

        td_dict_nwchem = {

            'tmax': self._var['Nt'].get() * self._var['dt'].get(),
            'dt': self._var['dt'].get(),
            'max':self._var['strength'].get(),
            'e_pol': self.pol_list,
            'pol_dir': self.read_pol_dir(),
            'extra_prop':self.extra_prop(),
            'output_freq': self._var['output_freq'].get()
            }

        if self.engine == 'gpaw':
            return td_dict_gp
        elif self.engine == 'nwchem':
            return td_dict_nwchem
        elif self.engine == 'octopus':
            return td_dict_oct

    def get_property_list(self):
        prop_list = []
        if self._var['ksd'].get() == 1:
            prop_list.append("ksd")
        if self._var['popln'].get() == 1:
            prop_list.append("population_correlation")    
        return prop_list       
        
    def extra_prop(self):
        # if self._var['mooc'].get() == 1:
        #     messagebox.showinfo(message="Population Correlation is not implemented yet.")
        #     self.checkbox3.config(state = 'disabled')            
            return("mooc")

        # if self._var['mooc'].get() == 1 and self._var['elec'].get() == 0:
        #     return("moocc")
        # if self._var['elec'].get() == 1 and self._var['mooc'].get() == 0:
        #     return("charge")

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)

    def save_button(self):
        self.event_generate('<<SaveRT_TDDFT_DELTAScript>>')

    def generate_input_button(self):
        self.event_generate('<<GenerateRT_TDDFT_DELTAScript>>')

    def run_job_button(self):
        self.event_generate('<<SubRT_TDDFT_DELTA>>')

    def back_button(self):
        self.event_generate('<<ShowWorkManagerPage>>')

    def update_var(self, default_dict:dict):
        for key, value in default_dict.items():
            try:
                self._var[key].set(value[1])
            except IndexError:
                self._var[key].set('')

    def update_engine_default(self, engn):
        self.engine = engn
        if engn == 'gpaw':
            self.update_var(self.gpaw_td_default)
            self.checkbox_ksd.config(state= 'active')
            self.checkbox_pc.config(state = 'disabled')

        elif engn == 'octopus':
            self.update_var(self.oct_td_default)
            # self._var['ksd'].set(0)
            # self.checkbox_ksd.config(state = 'disabled')
            self.checkbox_pc.config(state = 'disabled')

        elif engn == 'nwchem':            
            self.update_var(self.nwchem_td_default)
            self.checkbox_ksd.config(state='disabled')
            self.checkbox_pc.config(state = 'disabled')            


class LaserDesignPage(ttk.Frame):

    def __init__(self, parent, engine, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.engine = engine
        
        self.job = None
        self.tdpulse_dict = {}
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.strength = tk.DoubleVar()
        self.inval = tk.DoubleVar()
        self.pol_x = tk.StringVar()
        self.pol_y =  tk.StringVar()
        self.pol_z =  tk.StringVar()
        self.fwhm = tk.DoubleVar()
        self.frequency =  tk.DoubleVar()
        self.ts =  tk.DoubleVar()
        self.ns =  tk.IntVar()
        self.tin =  tk.DoubleVar()
        self.pol_var = tk.IntVar(value=0)

        self.frame_title = ttk.Frame(self)
        self.frame_title.grid(row=0, column=0, sticky='nsew')

        self.Frame1 = ttk.Frame(self)
        self.Frame1.grid(row=1, column=0)
        self.Frame1.configure(relief='groove',borderwidth="2", cursor="fleur")

        self.Frame_button = ttk.Frame(self)
        self.Frame_button.grid(row=2, column=0, sticky='nsew')
        self.Frame_button.configure(relief='groove',borderwidth="2", cursor="fleur")        

        self.Frame2 = ttk.Frame(self.Frame1)
        self.Frame2.grid(row=0, column=0)

        self.frame_pol = ttk.Frame(self.Frame1)
        self.frame_pol.grid(row=1, column=0, sticky='w')
   
        self.Frame1_label_path = tk.Label(self.Frame2,text="LITESOPH Input for Laser Design", fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.grid(row=0, column=0, padx=5, pady=10)

        self.label_proj = tk.Label(self.Frame2,text="Time Origin (tin) in attosecond",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        self.entry_tin = Decimalentry(self.Frame2, textvariable= self.tin, max= 10e100)
        self.entry_tin['font'] = myFont
        self.tin.set(0)
        self.entry_tin.grid(row=1, column=1)
        
        self.label_inval = tk.Label(self.Frame2,text="-log((E at tin)/Eo)",bg="gray",fg="black")
        self.label_inval['font'] = myFont
        self.label_inval.grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.entry_inval = Onlydigits(self.Frame2, textvariable= self.inval)
        self.entry_inval['font'] = myFont
        self.inval.set(6)
        self.entry_inval.grid(row=2, column=1)

        self.label_strength = tk.Label(self.Frame2,text="Laser Strength in a.u (Eo)",bg="gray",fg="black")
        self.label_strength['font'] = myFont
        self.label_strength.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    
        instr = ["1e-5","1e-4","1e-3"]
        self.entry_strength = ttk.Combobox(self.Frame2,textvariable= self.strength, value = instr)
        self.entry_strength['font'] = myFont
        self.entry_strength.current(0)
        self.entry_strength.grid(row=3, column=1)
        self.entry_strength['state'] = 'readonly'

        self.label_fwhm = tk.Label(self.Frame2,text="Full Width Half Max (FWHM in eV)",bg="gray",fg="black")
        self.label_fwhm['font'] = myFont
        self.label_fwhm.grid(row=4, column=0, sticky='w', padx=5, pady=5)

        self.entry_fwhm = Decimalentry(self.Frame2, textvariable= self.fwhm, max= 10e100)
        self.fwhm.set("0.01")
        self.entry_fwhm['font'] = myFont
        self.entry_fwhm.grid(row=4, column=1)

        self.label_freq = tk.Label(self.Frame2,text="Frequency in eV",bg="gray",fg="black")
        self.label_freq['font'] = myFont
        self.label_freq.grid(row=5, column=0, sticky='w', padx=5, pady=5)

        self.entry_frq = Decimalentry(self.Frame2,textvariable= self.frequency, max= 10e100)
        self.entry_frq['font'] = myFont
        self.entry_frq.grid(row=5, column=1)

        self.label_proj = tk.Label(self.Frame2,text="Time step in attosecond ",bg="gray",fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=6, column=0, sticky='w', padx=5, pady=5)

        self.entry_ts = Decimalentry(self.Frame2,textvariable= self.ts, max= 10e100)
        self.entry_ts['font'] = myFont
        self.ts.set(10)
        self.entry_ts.grid(row=6, column=1)
        
        self.label_ns = tk.Label(self.Frame2,text="Number of Steps",bg="gray",fg="black")
        self.label_ns['font'] = myFont
        self.label_ns.grid(row=7, column=0, sticky='w', padx=5, pady=5)

        self.entry_ns = Onlydigits(self.Frame2, textvariable= self.ns)
        self.entry_ns['font'] = myFont
        self.ns.set(2000)
        self.entry_ns.grid(row=7, column=1)
 
        Back_Button1 = tk.Button(self.Frame_button, text="Back",activebackground="#78d6ff",command=lambda:self.back_button())
        Back_Button1['font'] = myFont
        Back_Button1.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

        Laser_button = tk.Button(self.Frame_button,text="Laser Design",activebackground="#78d6ff",command=lambda:[self.laser_button()])
        Laser_button['font'] = myFont
        Laser_button.grid(row=0, column=1, sticky='nsew', padx=30, pady=5)

        Next_button = tk.Button(self.Frame_button,text="Next",activebackground="#78d6ff",command=lambda:[self.choose_laser()])
        Next_button['font'] = myFont
        Next_button.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        self.label_pol = tk.Label(self.frame_pol,text="Polarization Direction:",bg="gray",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        values = {"X": 0, "Y": 1, "Z": 2}
        for (text, value) in values.items():
            tk.Radiobutton(self.frame_pol, text=text, variable=self.pol_var, font=myfont2(),
             justify='left',value=value).grid(row=0, column=value+1, sticky='w')

        # self.Frame2_Button1 = tk.Button(self.Frame2, state='disabled', text="Save Input",activebackground="#78d6ff", command=lambda:[self.save_button()])
        # self.Frame2_Button1['font'] = myFont
        # self.Frame2_Button1.place(x=10,y=380)

        # self.label_msg = tk.Label(self.Frame2,text="")
        # self.label_msg['font'] = myFont
        # self.label_msg.place(x=10,y=350)
 
        # self.Frame2_Button2 = tk.Button(self.Frame2, state='disabled', text="View Input",activebackground="#78d6ff", command=lambda:[self.view_button()])
        # self.Frame2_Button2['font'] = myFont
        # self.Frame2_Button2.place(x=170,y=380)
        
        # self.Frame2_Button3 = tk.Button(self.Frame2, state='disabled', text="Run Job",activebackground="#78d6ff",command=lambda:self.run_job_button())
        # self.Frame2_Button3['font'] = myFont
        # self.Frame2_Button3.place(x=350,y=380)
        # self.Frame3 = None


    def show_laser_plot(self, figure):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
        self.Frame3 = ttk.Frame(self)
        self.Frame3.grid(row=1, column=1)
        # self.Frame3.place(relx=0.480, rely=0.01, relheight=0.99, relwidth=0.492)

        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="2")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(cursor="fleur")

        self.Frame3.canvas = FigureCanvasTkAgg(figure, master=self.Frame3)
        self.Frame3.canvas.draw()
        self.Frame3.canvas.get_tk_widget().pack(side =tk.LEFT,fill='both', expand=True)
        self.Frame3.toolbar = NavigationToolbar2Tk(self.Frame3.canvas, self.Frame3)
        self.Frame3.toolbar.update()
        self.Frame3.canvas._tkcanvas.pack(side= tk.TOP,fill ='both')
    
    def laser_button(self):
        self.event_generate('<<DesignLaser>>')
   
    # def activate_td_frame(self):
    #     self.Frame2.tkraise() 
    #     self.Frame2_Button1.config(state='active') 
    #     self.Frame2_Button2.config(state='active') 
    #     self.Frame2_Button3.config(state='active') 
               
    def destroy_plot(self):
        self.Frame3.destroy()

    def choose_laser(self):
        self.event_generate('<<ChooseLaser>>')

    def get_pol_list(self): 
        if self.pol_var.get() == 0:
            pol_list = [1,0,0]         
        elif self.pol_var.get() == 1:
            pol_list = [0,1,0] 
        elif self.pol_var.get() == 2:
            pol_list = [0,0,1]                
        return pol_list

    def get_laser_pulse(self):
        from litesoph.utilities.units import as_to_au
        laser_input = {

        "strength": self.strength.get(),
        "inval" :  self.inval.get(),
        "pol_list": self.get_pol_list(),
        "fwhm" :self.fwhm.get(),
        "frequency" :  self.frequency.get(),
        "time_step" : self.ts.get(),
        "number_of_steps": self.ns.get(),
        "tin" : self.tin.get()*as_to_au
        
        }
        return(laser_input)               

    def set_laser_design_dict(self, l_dict:dict):
        self.laser_design_dict = l_dict

    def get_parameters(self):
        
        from litesoph.utilities.units import au_to_fs,autime_to_eV
        laser_param = self.laser_design_dict 
        self.pol_list = self.get_pol_list()              
        # epol_list = [int(self.pol_x.get()),int(self.pol_y.get()),int(self.pol_z.get())]
       
        if self.engine == 'gpaw':
            abs_x = float(self.strength.get())*float(self.pol_x.get())
            abs_y = float(self.strength.get())*float(self.pol_y.get())
            abs_z = float(self.strength.get())*float(self.pol_z.get())
            abs_list = [abs_x, abs_y, abs_z]
            inp_list = [float(self.ts.get()),int(self.ns.get())]

            l_dict ={
                'frequency':self.frequency.get(),
                'strength':self.strength.get(),
                'sigma': round(autime_to_eV/self.laser_design_dict['sigma'], 2),
                'time0': round(self.laser_design_dict['time0']*au_to_fs, 2)
            }
            laser_param.update(l_dict)
            td_gpaw = {
                        'absorption_kick' :abs_list,
                        'propagate': tuple(inp_list),
                        'electric_pol': self.pol_list,             
                        'td_potential' : True,                     
                        'laser': laser_param}
            # print(td_gpaw)            
            return td_gpaw
            
        elif self.engine == 'octopus':
            td_oct = {  'e_pol' :self.pol_list,
                        'max_step' : self.ns.get(),
                        'time_step': self.ts.get(),
                        'strength' : self.strength.get(),
                        'time0' :laser_param['time0'],
                        'sigma' : laser_param['sigma'],
                        'frequency': self.frequency.get()
                    }
            # print(td_oct)            
            return td_oct        
                      
        elif self.engine == 'nwchem':
            td_nwchem = { 'e_pol' :self.pol_list,
                          'tmax' : self.ns.get() * self.ts.get(),
                          'dt': self.ts.get(),
                          'max' : self.strength.get(),
                          'center' :laser_param['time0'],
                          'width' : laser_param['sigma'],
                          'freq': self.frequency.get()   
                        }
            # print(td_nwchem)
            return td_nwchem

    def save_button(self):
        self.event_generate('<<SaveRT_TDDFT_LASERScript>>')          

    def view_button(self):
        self.event_generate('<<ViewRT_TDDFT_LASERScript>>')

    def run_job_button(self):
        self.event_generate('<<SubRT_TDDFT_LASER>>')

    def back_button(self):
        self.event_generate('<<ShowWorkManagerPage>>')

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg) 

   

class PlotSpectraPage(ttk.Frame):

    def __init__(self, parent, engine, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.engine = engine
        
        self._default_var = {
            'del_e' : ['float', 0.05],
            'e_max' : ['float', 30.0],
            'e_min' : ['float']
        }
        self.gpaw_td_default = {
            'del_e' : ['float'],
            'e_max' : ['float'],
            'e_min' : ['float']
        }
        self.oct_td_default = {
            'del_e' : ['float'],
            'e_max' : ['float'],
            'e_min' : ['float']
        }
        self.nwchem_td_default= {
            'del_e' : ['float'],
            'e_max' : ['float'],
            'e_min' : ['float']
        }
        self._var = var_define(self._default_var)

        self.axis = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.Frame1 = ttk.Frame(self, borderwidth=2, relief='groove')
        # self.grid_columnconfigure(9, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=5)

        self.Frame1.grid(row=0,column=0, sticky='nsew')

        self.add_job_frame(self, "Spectrum", r=0, c=1)        

        self.heading = tk.Label(self.Frame1,text="LITESOPH Spectrum Calculations and Plots", fg='blue')
        self.heading['font'] = myfont()
        self.heading.grid(row=0, column=0, padx=2, pady=4)
        
        self.label_pol = tk.Label(self.Frame1, text= "Calculation of absorption spectrum:",bg= label_design['bg'],fg=label_design['fg'])
        self.label_pol['font'] = label_design['font']
        self.label_pol.grid(row=1, column=0, padx=2, pady=4, sticky='nsew')       

        self.label_estep = tk.Label(self.Frame1,text="Energy step (in eV)",bg= label_design['bg'],fg=label_design['fg'])
        self.label_estep['font'] = label_design['font']
        self.label_estep.grid(row=2, column=0, padx=2, pady=4, sticky='nsew' )

        self.entry_estep = tk.Entry(self.Frame1,textvariable =self._var['del_e'])
        self.entry_estep['font'] = label_design['font']
        self.entry_estep.grid(row=2, column=1, padx=2, pady=4, sticky='nsew')

        self.label_emax = tk.Label(self.Frame1,text="Minimum energy (in eV)",bg= label_design['bg'],fg=label_design['fg'])
        self.label_emax['font'] = label_design['font']
        self.label_emax.grid(row=3, column=0, padx=2, pady=4, sticky='nsew')

        self.entry_emax = tk.Entry(self.Frame1,textvariable =self._var['e_min'])
        self.entry_emax['font'] = label_design['font']
        self.entry_emax.grid(row=3, column=1, padx=2, pady=4, sticky='nsew')

        self.label_emax = tk.Label(self.Frame1,text="Maximum energy (in eV)",bg= label_design['bg'],fg=label_design['fg'])
        self.label_emax['font'] = label_design['font']
        self.label_emax.grid(row=4, column=0, padx=2, pady=4, sticky='nsew')

        self.entry_emax = tk.Entry(self.Frame1,textvariable = self._var['e_max'])
        self.entry_emax['font'] = label_design['font']
        self.entry_emax.grid(row=4, column=1, padx=2, pady=4, sticky='nsew')


        self.button_frame = ttk.Frame(self, borderwidth=2, relief='groove')
        self.button_frame.grid(row=1, column=0, sticky='nsew')

        Frame_Button1 = tk.Button(self.button_frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myfont()
        Frame_Button1.grid(row=0, column=0, padx=3, pady=6)

    def add_job_frame(self, parent, task_name, r:int, c:int):  
        """  Adds submit job buttons to View1"""

        self.Frame3 = ttk.Frame(parent, borderwidth=2, relief='groove')
        self.Frame3.grid(row=r, column=c, sticky='nswe')

        self.Frame1_Button2 = tk.Button(self.Frame3, text="Submit Local", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubLocal'+task_name+'>>'))
        self.Frame1_Button2['font'] = myfont()
        self.Frame1_Button2.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
        
        self.Frame1_Button3 = tk.Button(self.Frame3, text="Submit Network", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubNetwork'+task_name+'>>'))
        self.Frame1_Button3['font'] = myfont()
        self.Frame1_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')
        self.Frame1_Button3.config(state='disabled')
        
        self.plot_button = tk.Button(self.Frame3, text="Plot", activebackground="#78d6ff", command=lambda: self.show_plot())
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=3, column=2,padx=3, pady=15, sticky='nsew')

    def gpaw_specific_spectra(self, parent):
        gpaw_spec_frame = ttk.Frame(parent)  
        gpaw_spec_frame.grid(row=0, column=0)

        self.label_folding = tk.Label(gpaw_spec_frame,text="Folding (in eV)",bg="gray",fg="black")
        self.label_folding['font'] = myfont()
        self.label_folding.grid(row=0, column=0)

        self.entry_folding = tk.Entry(gpaw_spec_frame)
        self.entry_folding['font'] = myfont()
        self.entry_folding.grid(row=0, column=1)

        self.label_width = tk.Label(gpaw_spec_frame,text="Width",bg="gray",fg="black")
        self.label_width['font'] = myfont()
        self.label_emax.grid(row=1, column=0)

        self.entry_emax = tk.Entry(gpaw_spec_frame)
        self.entry_emax['font'] = myfont()
        self.entry_emax.grid(row=1, column=1)

    def oct_specific_spectra(self, parent):
        oct_spec_frame = ttk.Frame(parent)
        oct_spec_frame.grid(row=0, column=0)

        self.label_1 = tk.Label(oct_spec_frame,text="Propagation Spectrum Damp Mode",bg="gray",fg="black")
        self.label_1['font'] = myfont()
        self.label_1.grid(row=0, column=0)

        self.entry_1 = tk.Entry(oct_spec_frame)
        self.entry_1['font'] = myfont()
        self.entry_1.grid(row=0, column=1)

    def show_engine_specific_frame(self, engine):
        if engine=="gpaw":
            self.gpaw_specific_spectra(self)
            self.Frame1_Button3.config(state='active') 
        elif engine== "octopus":
            self.oct_specific_spectra(self) 
            self.Frame1_Button3.config(state='active') 
        elif engine == "nwchem":
            self.Frame1_Button3.config(state='disabled') 
            

    def show_plot(self):
        self.event_generate("<<ShowSpectrumPlot>>")


    def get_parameters(self):
        td_dict_gp = {
            'del_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()       
        }
        
        td_dict_oct = {
            'del_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()
          }

        td_dict_nwchem = {
            'del_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()
            }
        
        if self.engine == 'gpaw':
            return td_dict_gp
        elif self.engine == 'nwchem':
            return td_dict_nwchem
        elif self.engine == 'octopus':
            return td_dict_oct            
    
  

class DmLdPage(ttk.Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        from litesoph.utilities.units import au_to_fs
        self.plot_task = tk.StringVar()
        self.compo = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        j=font.Font(family ='Courier', size=20,weight='bold')
        k=font.Font(family ='Courier', size=40,weight='bold')
        l=font.Font(family ='Courier', size=15,weight='bold')
        
        self.Frame = ttk.Frame(self) 
        
        self.Frame.place(relx=0.01, rely=0.01, relheight=0.98, relwidth=0.978)
        self.Frame.configure(relief='groove')
        self.Frame.configure(borderwidth="2")
        self.Frame.configure(relief="groove")
        self.Frame.configure(cursor="fleur")
        
        self.heading = tk.Label(self.Frame,text="LITESOPH Dipole Moment and laser Design", fg='blue')
        self.heading['font'] = myFont
        self.heading.place(x=350,y=10)
        
        self.label_pol = tk.Label(self.Frame, text= "Plot:",bg= "grey",fg="black")
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

        self.label_pol = tk.Label(self.Frame, text="Select the axis", bg= "grey",fg="black")
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
   
class TcmPage(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
        self.parent = parent
        self.job = None
        
        self.engine_name = tk.StringVar()
        self.min = tk.DoubleVar()
        self.max = tk.DoubleVar()
        self.step = tk.DoubleVar()
        self.freq = tk.DoubleVar()
        self.frequency = tk.StringVar()
        self.ni = tk.IntVar(value=1)
        self.na = tk.IntVar(value=1)
        self.wmin = tk.DoubleVar()
        self.wmax = tk.DoubleVar()
        self.axis_limit = tk.DoubleVar(value=3)

        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.heading = tk.Label(self,text="LITESOPH Kohn Sham Decomposition", fg='blue')
        self.heading['font'] = myfont()
        self.heading.grid(row=0, column=0)

        self.Frame1 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame1.grid(row=1,column=0, sticky='nsew')

        self.grid_rowconfigure(1, weight=5)
        self.grid_rowconfigure(2, weight=1)

        self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button.grid(row=2, column=0, sticky='nsew')

        self.frame_inp = ttk.Frame(self.Frame1, borderwidth=2)
        self.frame_inp.grid(row=1,column=0, sticky='nsew')           

        Frame_Button1 = tk.Button(self.frame_button, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate('<<ShowWorkManagerPage>>'))
        Frame_Button1['font'] = myfont()
        Frame_Button1.grid(row=0, column=0)

        self.engine_name.trace_add(['write'], lambda *_:self.select_ksd_frame(self.frame_inp))
        self.add_job_frame("TCM")

    def add_gpaw_ksd_frame(self, parent):
        """ Creates widgets for gpaw ksd calculation"""    
        
        self.Label_freqs = tk.Label(parent,text="List of Frequencies(eV) (eg: 2.1, 4)",fg="black", justify='left')
        self.Label_freqs['font'] = myfont()
        self.Label_freqs.grid(row=0, column=0)        
        
        self.entry_freq = tk.Entry(parent, textvariable= self.frequency, width=20)
        self.entry_freq['font'] = myfont()
        self.entry_freq.grid(row=0, column=1, columnspan=2)

        self.label_sigma = tk.Label(parent,text="Axis limit",fg="black", justify='left')
        self.label_sigma['font'] = myfont()
        self.label_sigma.grid(row=1, column=0)        
        
        self.entry_sigma = Decimalentry(parent, textvariable= self.axis_limit, width=5)
        self.entry_sigma['font'] = myfont()
        self.entry_sigma.grid(row=1, column=1)

    def add_oct_ksd_frame(self, parent):
        """ Creates widgets for Octopus ksd calculation"""

        self.Label_ni = tk.Label(parent,text="Number of occupied states(HOMO & below)",fg="black", justify='left')
        self.Label_ni['font'] = myfont()
        self.Label_ni.grid(row=1, column=0)        
        
        self.entry_ni = Onlydigits(parent, textvariable= self.ni, width=5)
        self.entry_ni['font'] = myfont()
        self.entry_ni.grid(row=1, column=1)

        self.Label_na = tk.Label(parent,text="Number of unoccupied states(LUMO & above)",fg="black", justify='left')
        self.Label_na['font'] = myfont()
        self.Label_na.grid(row=2, column=0)        
        
        self.entry_na = Onlydigits(parent, textvariable= self.na, width=5)
        self.entry_na['font'] = myfont()
        self.entry_na.grid(row=2, column=1)

        self.label_plot = tk.Label(parent,text="Frequency range for KSD Contour Plots:",fg="black", justify='left')
        self.label_plot['font'] = myfont()
        self.label_plot.grid(row=3, column=0)

        self.Label_wmin = tk.Label(parent,text="Minimum frequency value",fg="black", justify='left')
        self.Label_wmin['font'] = myfont()
        self.Label_wmin.grid(row=4, column=0)        
        
        self.entry_wmin = Decimalentry(parent, textvariable= self.wmin, width=5)
        self.entry_wmin['font'] = myfont()
        self.entry_wmin.grid(row=4, column=1)

        self.Label_wmax = tk.Label(parent,text="Maximum frequency value",fg="black", justify='left')
        self.Label_wmax['font'] = myfont()
        self.Label_wmax.grid(row=5, column=0)        
        
        self.entry_wmin = Decimalentry(parent, textvariable= self.wmax, width=5)
        self.entry_wmin['font'] = myfont()
        self.entry_wmin.grid(row=5, column=1)

        self.label_sigma = tk.Label(parent,text="Axis limit",fg="black", justify='left')
        self.label_sigma['font'] = myfont()
        self.label_sigma.grid(row=6, column=0)        
        
        self.entry_sigma = Decimalentry(parent, textvariable= self.axis_limit, width=5)
        self.entry_sigma['font'] = myfont()
        self.entry_sigma.grid(row=6, column=1)


    def select_ksd_frame(self, parent):
        engine = self.engine_name.get()

        for widget in parent.winfo_children():
            widget.destroy()
        if engine == 'gpaw':
            self.add_gpaw_ksd_frame(parent)
        elif engine == 'octopus':
            self.add_oct_ksd_frame(parent)    


    def add_job_frame(self, task_name):  
        """  Adds submit job buttons"""

        self.Frame3 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame3.grid(row=1, column=1, sticky='nswe')
        
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
        engine = self.engine_name.get()    
       
        if engine == 'gpaw':
            
            self.retrieve_input()

            gpaw_ksd_dict = {
                'frequency_list' : self.freq_list,
                'axis_limit': self.axis_limit.get()
                 } 
            return gpaw_ksd_dict

        elif engine == 'octopus':

            oct_ksd_dict = {
            'ni': self.ni.get(),
            'na': self.na.get(),
            'fmin': self.wmin.get(),
            'fmax': self.wmax.get(),
            'axis_limit': self.axis_limit.get()
        } 

            return oct_ksd_dict                
       
class JobSubPage(ttk.Frame):
    """ Creates widgets for JobSub Page"""

    def __init__(self, parent, task, job_type, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        
        self.parent = parent
        self.task = task
        self.job_type = job_type
        self.runlocal_np =  None
        self.run_script_path = None
        
        self.processors = tk.IntVar()
        self.ip = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.rpath = tk.StringVar()
        self.port = tk.IntVar()
        self.network_job_type = tk.IntVar()
        self.sub_command = tk.StringVar()
        self.sub_job_type = tk.IntVar()

        self.sub_job_type.trace_add(['write'], self._sub_command_option)
        self.sub_command.set('bash')
        self.processors.set(1)
        self.port.set(22)
        self.Frame1 = ttk.Frame(self, borderwidth=2, relief='groove')
        self.Frame1.grid(row=1,column=0, columnspan=4, rowspan=100, sticky='nsew')
        self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button.grid(row=101, column=0,columnspan=5, sticky='nswe')
        self.sub_job_frame = ttk.Frame(self.Frame1)
        self.sub_job_frame.grid(row=0, column=0, sticky='nsew')

        view_option_frame = ttk.Frame(self.Frame1, borderwidth=2 ,relief='groove')
        view_option_frame.grid(row=1,column=0, sticky='nsew', pady=15)
        self.show_job_frame()

        self.Frame_label = tk.Label(self, text="LITESOPH Job Submission", fg='blue')
        self.Frame_label['font'] = myfont1()
        self.Frame_label.grid(row=0, column=3)       

        view_btn = tk.Button(view_option_frame, text="View Output",activebackground="#78d6ff",command=lambda:[self.view_outfile(self.task)])
        view_btn['font'] = myfont()
        view_btn.grid(row=10, column=1)

        self.Frame_label = tk.Label(self, text="LITESOPH Job Submission", fg='blue')
        self.Frame_label['font'] = myfont1()
        self.Frame_label.grid(row=0, column=3)         

        back = tk.Button(self.frame_button, text="Back ",activebackground="#78d6ff",command=lambda:[self.event_generate(f'<<Show{self.task}Page>>')])
        back['font'] = myfont()
        back.pack(side= tk.LEFT)

        back2main = tk.Button(self.frame_button, text="Back to main page",activebackground="#78d6ff",command=lambda:[self.event_generate('<<ShowWorkManagerPage>>')])
        back2main['font'] = myfont()
        back2main.pack(side= tk.RIGHT)

    
    def set_network_profile(self, remote_profile: dict):
        self.username.set(remote_profile['username'])
        self.ip.set(remote_profile['ip'])
        self.port.set(remote_profile['port'])
        self.rpath.set(remote_profile['remote_path'])


    def show_job_frame(self):
        """ Creates Job Sub input widgets"""

        if self.job_type == 'Local':
            self.show_run_local()
            self.text_view_button_frame = None
        elif self.job_type == 'Network':
            self.show_run_network() 

    def show_run_local(self): 
        """ Creates Local JobSub input widgets""" 

        values = {"Command line execution": 0, "Submit through queue": 1}
        for (text, value) in values.items():
            tk.Radiobutton(self.sub_job_frame, text=text, variable=self.sub_job_type, font=myfont2(),
             justify='left',value=value).grid(row=value, column=0, ipady=5, sticky='w')   
        
        self.label_np = tk.Label(self.sub_job_frame, text="Number of processors", bg='gray', fg='black')
        self.label_np['font'] = myfont()
        self.label_np.grid(row=2, column=0,sticky='nsew', padx=5, pady=5)

        entry_np = Onlydigits(self.sub_job_frame, textvariable=self.processors)
        entry_np['font'] = myfont()
        entry_np.grid(row=2, column=1, ipadx=2, ipady=2)

        self.label_command = tk.Label(self.sub_job_frame, text="Submit command", bg='gray', fg='black')
        self.label_command['font'] = myfont()
        self.label_command.grid(row=3, column=0,sticky='nsew', padx=5, pady=5)

        self.entry_command = tk.Entry(self.sub_job_frame, textvariable=self.sub_command)
        self.entry_command['font'] = myfont()
        self.entry_command.grid(row=3, column=1, ipadx=2, ipady=2)

        self.create_button = tk.Button(self.sub_job_frame, text="Generate Job Script",activebackground="#78d6ff",command = self.create_job_script)
        self.create_button['font'] = myfont()
        self.create_button.grid(row=4, column=0, pady=5)   

        save_job_script = tk.Button(self.sub_job_frame, text="Save Job Script",activebackground="#78d6ff",command = self.save_job_script)
        save_job_script['font'] = myfont()
        save_job_script.grid(row=5,column=0,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff",command=lambda:[self.submitjob_local()])
        self.run_button['font'] = myfont()
        self.run_button.grid(row=4, column=1, pady=5)        

    def show_run_network(self):
        """ Creates Network JobSub input widgets""" 

        values = {"Command line execution": 0, "Submit through queue": 1}
        for (text, value) in values.items():
            tk.Radiobutton(self.sub_job_frame, text=text, variable=self.sub_job_type, font=myfont2(),
             justify='left',value=value).grid(row=value, column=0, ipady=5, sticky='w')   

        host_label = tk.Label(self.sub_job_frame, text= "Host IP address", bg='gray', fg='black')
        host_label['font'] = myfont()
        host_label.grid(row=2, column=0, sticky='nsew', padx=2, pady=4)
 
        host_entry = tk.Entry(self.sub_job_frame,textvariable= self.ip, width=20)
        host_entry['font'] =myfont()
        host_entry.grid(row=2, column=1,sticky='nsew', padx=2, pady=4)

        port_label = tk.Label(self.sub_job_frame, text= "Port", bg='gray', fg='black')
        port_label['font'] = myfont()
        port_label.grid(row=3,column=0,sticky='nsew', padx=2, pady=4)

        port_entry = tk.Entry(self.sub_job_frame,textvariable= self.port, width=20)
        port_entry['font'] = myfont()
        port_entry.grid(row=3, column=1,sticky='nsew', padx=2, pady=4)

        user_name_label = tk.Label(self.sub_job_frame, text= "User Name", bg='gray', fg='black')
        user_name_label['font'] = myfont()
        user_name_label.grid(row=4,column=0,sticky='nsew', padx=2, pady=4)

        user_name_entry = tk.Entry(self.sub_job_frame,textvariable= self.username, width=20)
        user_name_entry['font'] = myfont()
        user_name_entry.grid(row=4, column=1,sticky='nsew', padx=2, pady=4)
 
        password_label = tk.Label(self.sub_job_frame, text= "Password", bg='gray', fg='black')
        password_label['font'] = myfont()
        password_label.grid(row=5,column=0,sticky='nsew', padx=2, pady=4)

        password_entry = tk.Entry(self.sub_job_frame,textvariable= self.password, width=20, show = '*')
        password_entry['font'] = myfont()
        password_entry.grid(row=5,column=1,sticky='nsew', padx=2, pady=4)

        remote_path_label = tk.Label(self.sub_job_frame, text= "Remote Path", bg='gray', fg='black')
        remote_path_label['font'] = myfont()
        remote_path_label.grid(row=6,column=0,sticky='nsew', padx=2, pady=4)

        remote_path_entry = tk.Entry(self.sub_job_frame,textvariable= self.rpath, width=20)
        remote_path_entry['font'] = myfont()
        remote_path_entry.grid(row=6,column=1,sticky='nsew', padx=2, pady=4)

        num_processor_label = tk.Label(self.sub_job_frame, text= "Number of Processors", bg='gray', fg='black')
        num_processor_label['font'] = myfont()
        num_processor_label.grid(row=7,column=0,sticky='nsew', padx=2, pady=4)

        num_processor_entry = Onlydigits(self.sub_job_frame,textvariable= self.processors, width=20)
        num_processor_entry['font'] = myfont()
        num_processor_entry.grid(row=7,column=1,sticky='nsew', padx=2, pady=4)

        self.label_command = tk.Label(self.sub_job_frame, text="Submit command", bg='gray', fg='black')
        self.label_command['font'] = myfont()
        self.label_command.grid(row=8, column=0,sticky='nsew', padx=5, pady=5)

        self.entry_command = tk.Entry(self.sub_job_frame, textvariable=self.sub_command)
        self.entry_command['font'] = myfont()
        self.entry_command.grid(row=8, column=1, ipadx=2, ipady=2)
      
        upload_button2 = tk.Button(self.sub_job_frame, text="Generate Job Script",activebackground="#78d6ff",command = self.create_job_script)
        upload_button2['font'] = myfont()
        upload_button2.grid(row=9,column=0,sticky='nsew', padx=2, pady=4)

        save_job_script = tk.Button(self.sub_job_frame, text="Save Job Script",activebackground="#78d6ff",command = self.save_job_script)
        save_job_script['font'] = myfont()
        save_job_script.grid(row=10,column=0,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff", command=lambda:[self.submitjob_network()])
        self.run_button['font'] = myfont()
        self.run_button.grid(row=9,column=1,sticky='nsew', padx=2, pady=4)    

    def _sub_command_option(self, *_):
        if self.sub_job_type.get() == 0:
            self.sub_command.set('bash')
        else:
            self.sub_command.set('')

    def view_outfile(self, task_name ):
        event = '<<View'+task_name+self.job_type+'Outfile>>'
        self.event_generate(event)
        
    def get_processors(self):
        return self.processors.get()

    def submitjob_local(self):
        event = '<<Run'+self.task+'Local>>'
        self.event_generate(event)

    def disable_run_button(self):
        self.run_button.config(state='disabled')

    def activate_run_button(self):
        self.run_button.config(state='active')

    def create_job_script(self):
        event = '<<Create'+self.task+self.job_type+'Script>>'
        self.event_generate(event)
    
    def save_job_script(self):
        event = '<<Save'+self.task+self.job_type+'>>'
        self.event_generate(event)

    def submitjob_network(self):
        event = '<<Run'+self.task+'Network>>'
        self.event_generate(event)
        
    def get_network_dict(self):

        network_job_dict = {
          'ip':self.ip.get(),
          'username':self.username.get(),
          'password':self.password.get(),
          'port' : self.port.get(),
          'remote_path':self.rpath.get(),
            } 
        return network_job_dict