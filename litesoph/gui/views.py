import tkinter as tk
from tkinter import *                    # importing tkinter, a standart python interface for GUI.

from tkinter import ttk
from tkinter import messagebox
from  PIL import Image,ImageTk
from tkinter import font

import pathlib

from numpy import append

from litesoph.gui import actions, images
from litesoph.simulations.project_status import show_message
from litesoph.gui.input_validation import EntryPattern, Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15
from litesoph.simulations.models import AutoModeModel
from litesoph.gui.engine_views import get_gs_engine_page


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

        button_create_project = tk.Button(mainframe,text="Start LITESOPH Project", activebackground="#78d6ff",command=lambda: self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
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
    Post_task = ["Compute Spectrum","Kohn Sham Decomposition","Population Correlation","Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]
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

        self.Frame2_Button_1 = tk.Button(common_frame,text="Select",activebackground="#78d6ff",command=self._get_geometry_file)
        self.Frame2_Button_1['font'] = myfont()
        self.Frame2_Button_1.grid(column=1, row= 0, padx=10,  pady=10)       

        self.message_label = tk.Label(common_frame, text='', foreground='red')
        self.message_label['font'] = myfont()
        self.message_label.grid(column=2, row= 0, padx=10,  pady=10)       
        
        self.Frame2_Button_1 = tk.Button(common_frame,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.Frame2_Button_1['font'] = myfont()
        self.Frame2_Button_1.grid(column=3, row= 0, padx=10,  pady=10)

        self.engine_source_label = tk.Label(common_frame,text="Source",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        self.engine_source_label['font'] = myfont()
        self.engine_source_label.grid(row= 1, column=0,  sticky='w',padx=4, pady=10)       
            
        self.engine_source = ttk.Combobox(common_frame,width=20, textvariable= self.engine, values= self.engine_list)
        self.engine_source['font'] = myfont()
        self.engine_source.grid(row= 1, column=1, columnspan=2, padx=4, pady=10)
        self.engine_source['state'] = 'readonly'

        self.label_proj = tk.Label(common_frame,text="Job Type",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        self.label_proj['font'] = myfont()
        self.label_proj.grid(row= 2, column=0,  sticky='w', padx=4, pady=10)       
            
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
        self.event_generate(actions.OPEN_PROJECT)

    def _create_project(self):
        self.event_generate(actions.CREATE_NEW_PROJECT)

    def _get_geometry_file(self):
        self.event_generate(actions.GET_MOLECULE)
        
    def _geom_visual(self):
        self.event_generate(actions.VISUALIZE_MOLECULE)

    def proceed_button(self):
        """ event generate on proceed button"""

        self.event_generate(actions.ON_PROCEED)   

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
        
class View(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.job = None

        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.input_param_frame= ttk.Frame(self, borderwidth=2, relief='groove')
        self.property_frame = ttk.Frame(self, borderwidth=2, relief='groove')
        self.submit_button_frame = ttk.Frame(self, borderwidth=2, relief='groove')
        self.save_button_frame = ttk.Frame(self, borderwidth=2, relief='groove')

        self.input_param_frame.pack(fill=tk.BOTH, anchor='n', expand=True)
        self.property_frame.pack(fill=tk.BOTH, anchor='n', expand=True)
        self.save_button_frame.pack( fill=tk.BOTH, anchor='n')
        self.submit_button_frame.pack(side=tk.BOTTOM, anchor='e')

    def clear_widgets(self):
        f_list = [self.input_param_frame.winfo_children, 
                self.property_frame.winfo_children,
                self.submit_button_frame.winfo_children,
                self.save_button_frame.winfo_children]

        for frame in f_list:
            for widget in frame():
                widget.destroy()

    def set_sub_button_state(self,state):
        self.sublocal_Button.config(state=state)
        self.subnet_Button.config(state=state)

def add_job_frame(obj, parent, task_name, row:int=0, column:int=0):  
    """  Adds submit job buttons """

    submit_frame = ttk.Frame(parent,borderwidth=2, relief='groove')
    submit_frame.grid(row=row, column=column, sticky='nswe')

    obj.sublocal_Button = tk.Button(submit_frame, text="Submit Local", activebackground="#78d6ff", command=lambda: obj.event_generate('<<SubLocal'+task_name+'>>'))
    obj.sublocal_Button['font'] = myfont()
    obj.sublocal_Button.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
    
    obj.subnet_Button = tk.Button(submit_frame, text="Submit Network", activebackground="#78d6ff", command=lambda: obj.event_generate('<<SubNetwork'+task_name+'>>'))
    obj.subnet_Button['font'] = myfont()
    obj.subnet_Button.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')

class GroundStatePage(View):
    
    def __init__(self, parent,engine, task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clear_widgets()
        self.myFont = font.Font(family='Helvetica', size=10, weight='bold')
        style = ttk.Style()
        notebook = ttk.Notebook(self.input_param_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        style.configure("TNotebook.Tab", font=('Helvetica','10'))
        #style.map("TNotebook.Tab", background=[('selected')])
        
        self.system_frame = ttk.Frame(notebook)
        self.calculation_frame = ttk.Frame(notebook)
        self.advanced_info_frame = ttk.Frame(notebook)

        notebook.add(self.system_frame, text='System')
        notebook.add(self.calculation_frame, text='Calculation Details')
        notebook.add(self.advanced_info_frame, text='Advanced Info')

        self.parent = parent
        self.task_name = task_name
        self.engine = tk.StringVar(value=engine)
        self.engine.trace_add('write', self.on_engine_change)
        self.job = None
        self.property_frame.destroy()

        add_job_frame(self, self.submit_button_frame, task_name, column=1)
        self.add_save_button_frame()
        self.on_engine_change()
        
    def on_engine_change(self, *_):
    
        f_list = [self.system_frame.winfo_children, 
                self.calculation_frame.winfo_children,
                self.advanced_info_frame.winfo_children]

        for frame in f_list:
            for widget in frame():
                widget.destroy()

        if self.engine.get() == 'auto-mode':
            self.gs_dict = AutoModeModel.ground_state
            self._var = define_tk_var(self.gs_dict)
            self.show_system_tab(self.system_frame)
            return

        self.engine_page = get_gs_engine_page(self.engine.get(), self)
        self.gs_dict = self.engine_page.default_para
        self._var = self.engine_page._var = define_tk_var(self.gs_dict)
        self.engine_page.create_input_widgets()


    def add_save_button_frame(self):
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.Frame1_Button1 = tk.Button(self.save_button_frame, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.Frame1_Button1['font'] = myFont
        self.Frame1_Button1.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        self.view_Button2 = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.view_Button2['font'] = myFont
        self.view_Button2.grid(row=0, column=2,padx=3, pady=3,sticky='nsew')
        
        self.save_Button3 = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.save_Button3['font'] = myFont
        self.save_Button3.grid(row=0, column=4, padx=3, pady=3,sticky='nsew')

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=3, sticky='nsew')

    def show_system_tab(self, parent):
        """ Creates widgets for system tab inputs"""

        for widget in parent.winfo_children():
            widget.destroy()

        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=0, column=0)      

        self.heading = tk.Label(mode_frame,text="LITESOPH input for Ground State",fg='green')
        self.heading['font'] = myfont15()
        self.heading.grid(row=0, column=0, pady=5)
                
        self.label_proj = tk.Label(mode_frame,text="Mode",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        def pick_box(e):
            if task.get() == "nao" or task.get() == 'pw':
                #check = messagebox.ask(title = 'Message',message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
                self.engine.set('gpaw')
            elif task.get() == "gaussian":
                self.engine.set('nwchem')
            elif task.get() == "fd":
                for widget in self.calculation_frame.winfo_children():
                    widget.destroy()
                self.show_auto_mode_calc_tab(self.calculation_frame) 

        task = ttk.Combobox(mode_frame, textvariable = self._var['mode'], values= self.gs_dict['mode']['values'])
        task['font'] = label_design['font']
        task.grid(row=2, column= 1, sticky='w', padx=2, pady=2)
        task.bind("<<ComboboxSelected>>", pick_box)
        task['state'] = 'readonly'

        
        self.basis = tk.Label(mode_frame, text="Basis",bg=label_design['bg'], fg=label_design['fg'])
        self.basis['font'] = label_design['font']
        self.basis.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        sub_task = ttk.Combobox(mode_frame, textvariable= self._var['basis'], value = self.gs_dict['basis']['values'])
        sub_task['font'] = label_design['font']
        sub_task.grid(row=4, column=1, sticky='w', padx=2, pady=2)
        sub_task['state'] = 'readonly'

        self.charge = tk.Label(mode_frame, text="Charge",bg=label_design['bg'], fg=label_design['fg'])
        self.charge['font'] = label_design['font']
        self.charge.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_chrg = Onlydigits(mode_frame,textvariable=self._var['charge'])
        self.entry_chrg['font'] = label_design['font']
        self.entry_chrg.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        multiplicity_label = tk.Label(mode_frame, text='Multiplicity',bg=label_design['bg'], fg=label_design['fg'])
        multiplicity_label['font'] = label_design['font']
        multiplicity_label.grid(row=7, column=0, sticky='w', padx=2, pady=4)

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
        self.event_generate(actions.SHOW_WORK_MANAGER_PAGE)              

    def get_parameters(self):

        if self.engine.get() == "auto-mode":
            messagebox.showwarning(title='Warning', message='Please choose the engine before proceeding')
            return 
        return self.engine_page.get_parameters()
       
    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)
            
    def save_button(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')          

    def generate_input_button(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def refresh_var(self):
        for key, value in self.gs_dict.items():
            try:
                self._var[key].set(value['default_value'])
            except KeyError:
                self._var[key].set('')     

def property_frame(obj, parent, myFont, spectra_var, ksd_var, pop_var, output_freq_var, row=0, column=0):

    frame_property = ttk.Frame(parent)
    frame_property.grid(row=0, column=0)

    obj.property_note = tk.Label(frame_property, text="Note: Please choose properties to be extracted in post-processing", fg="black")
    obj.property_note['font'] = myFont
    obj.property_note.grid(row=0, column=0)

    obj.checkbox_spectra = tk.Checkbutton(frame_property, text="Absorption Spectrum", variable= spectra_var, font=myFont, onvalue=1)
    obj.checkbox_spectra.grid(row=1, column=0, ipady=5, sticky='w')
    
    frame_spec_option = ttk.Frame(frame_property)
    frame_spec_option.grid(row=2, column=0, sticky='w')

    obj.checkbox_ksd = tk.Checkbutton(frame_property, text="Kohn Sham Decomposition", variable=ksd_var, font=myFont, onvalue=1, offvalue=0)
    obj.checkbox_ksd.grid(row=3, column=0, ipady=5, sticky='w')
    
    obj.checkbox_pc = tk.Checkbutton(frame_property, text="Population Correlation", variable=pop_var, font=myFont, onvalue=1, offvalue=0)
    obj.checkbox_pc.grid(row=4, column=0, ipady=5, sticky='w')

    frame_output_freq = ttk.Frame(frame_property)
    frame_output_freq.grid(row=5, column=0, sticky='w')

    obj.Frame2_lab = tk.Label(frame_output_freq, text="Frequency of data collection", fg="black")
    obj.Frame2_lab['font'] = myFont
    obj.Frame2_lab.grid(row=0, column=0,sticky='w')

    obj.entry_out_frq = Onlydigits(frame_output_freq, textvariable=output_freq_var, width=5)
    obj.entry_out_frq['font'] = myFont
    obj.entry_out_frq.grid(row=0, column=1,sticky='w')


class TimeDependentPage(View):

    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)

        self.parent = parent
        self.engine = engine
        self.task_name = task_name
        self.job = None

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
          
        self._default_var = {
            'strength': ['float'],
            'pol_var' : ['int', 1],
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
            self.input_param_frame, text="LITESOPH input for Delta Kick", fg='blue')
        self.Frame1_label_path['font'] = myFont
        self.Frame1_label_path.grid(row=0, column=0)

        self.label_proj = tk.Label(
            self.input_param_frame, text="Laser strength in a.u", bg="gray", fg="black", justify='left')
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.entry_strength = EntryPattern(self.input_param_frame, textvariable=self._var['strength'])
        self.entry_strength['font'] = myFont
        self.entry_strength.grid(row=2, column=1)
        self._var['strength'].set('01e-05')

        # inval = ["1e-5", "1e-4", "1e-3"]
        # self.entry_inv = ttk.Combobox(
        #     self.input_param_frame, textvariable=self._var['strength'], value=inval)
        # self.entry_inv['font'] = myFont
        # self.entry_inv.grid(row=2, column=1)
        # self.entry_inv['state'] = 'readonly'

        self.label_proj = tk.Label(
            self.input_param_frame, text="Propagation time step (in attosecond)", bg="gray", fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=3, column=0, sticky='w', padx=2, pady=4)

        self.entry_dt = Decimalentry(self.input_param_frame, textvariable=self._var['dt'])
        self.entry_dt['font'] = myFont
        self.entry_dt.grid(row=3, column=1, ipadx=2, ipady=2)

        self.label_proj = tk.Label(
            self.input_param_frame, text="Total time steps", bg="gray", fg="black")
        self.label_proj['font'] = myFont
        self.label_proj.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        self.entry_nt = Onlydigits(self.input_param_frame, textvariable=self._var['Nt'])
        self.entry_nt['font'] = myFont
        self.entry_nt.grid(row=4, column=1, ipadx=2, ipady=2)

        property_frame(self, self.property_frame, myFont, spectra_var= self._var['spectra'],
                                ksd_var=self._var['ksd'], pop_var=self._var['popln'],
                                output_freq_var=self._var['output_freq'],
                                row=1)

        frame_additional = ttk.Frame(self.input_param_frame)
        frame_additional.grid(row=8, column=0, pady=10)

        self.label_select = tk.Label(frame_additional, text="Please select polarization direction:",  bg="gray", fg="black")
        self.label_select['font'] = myFont
        self.label_select.grid(row=0, column=0, sticky='w', padx=2, pady=4)

        frame_pol = ttk.Frame(frame_additional, borderwidth=2)
        frame_pol.grid(row=1, column=0, sticky='w')

        values = {"X": 1, "Y": 2, "Z": 3}
        for (text, value) in values.items():
            tk.Radiobutton(frame_pol, text=text, variable=self._var['pol_var'], font=myfont2(),
             justify='left',value=value).grid(row=0, column=value, ipady=5, sticky='w')
        
        self.Frame1_Button1 = tk.Button(self.save_button_frame, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.Frame1_Button1['font'] = myFont
        self.Frame1_Button1.grid(row=0, column=1, sticky='nsew', padx=3, pady=3)
        self.save_button_frame.grid_columnconfigure(2, weight=1)
        self.save_button_frame.grid_columnconfigure(4, weight=1)
        self.Frame1_Button2 = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.Frame1_Button2['font'] = myFont
        self.Frame1_Button2.grid(row=0, column=3, sticky='nsew', padx=3, pady=3)
        
        self.Frame1_Button3 = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.Frame1_Button3['font'] = myFont
        self.Frame1_Button3.grid(row=0, column=5, sticky='nswe', padx=3, pady=3)

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=4)
        add_job_frame(self, self.submit_button_frame, task_name, row=1, column=9)

    def get_pol_list(self): 
        if self._var['pol_var'].get() == 1:
            pol_list = [1,0,0]         
        elif self._var['pol_var'].get() == 2:
            pol_list = [0,1,0] 
        elif self._var['pol_var'].get() == 3:
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
        from litesoph.utilities.units import as_to_au
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

        # td_dict_oct = {
        #     'max_step' : self._var['Nt'].get() ,
        #     'time_step' : self._var['dt'].get(),
        #     'td_propagator' : 'aetrs',
        #     'strength': self._var['strength'].get(),
        #     'e_pol': self.pol_list,
        #     'pol_dir': self.read_pol_dir(),
        #     'output_freq': self._var['output_freq'].get(),
        #     'analysis_tools': self.get_property_list()
        #   }
        td_dict_oct = {
            "CalculationMode": 'td',
            "TDMaxSteps" : self._var['Nt'].get() ,
            "TDTimeStep" : round(self._var['dt'].get()*as_to_au, 2),
            "TDPropagator" : 'aetrs',
            "TDDeltaStrength": self._var['strength'].get(),
            "TDPolarizationDirection": self._var['pol_var'].get(),
            "TDOutputComputeInterval": self._var['output_freq'].get(),
            "TDOutput": self.get_td_out()
          }

        if self.engine == 'gpaw':
            return td_dict_gp
        elif self.engine == 'nwchem':
            td_dict_nwchem = {
            'task':'rt_tddft_delta',
            'rt_tddft':{'tmax': round(self._var['Nt'].get() * self._var['dt'].get() * as_to_au,2),
                        'dt': round(self._var['dt'].get() * as_to_au, 2),
                        'field':{'name': 'kick_' + self.read_pol_dir()[1],
                                'type': 'delta',
                                'polarization':self.read_pol_dir()[1],
                                'max':self._var['strength'].get()},
            'print':self.out_print()}}
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

    def get_td_out(self):

        ksd = (self._var['ksd'].get() == 1)
        population = (self._var['popln'].get() == 1)
        td_occup = [ksd, population]

        td_out_list = []
        if any(td_occup):
            td_out_list.append(["td_occup"])
        return td_out_list
        
    def out_print(self):
        p_list = ['dipole'] 
        if self._var['popln'].get() == 1 :
            p_list.append('moocc')
        return p_list

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)

    def save_button(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')

    def generate_input_button(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def back_button(self):
        self.event_generate(actions.SHOW_WORK_MANAGER_PAGE)

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


class LaserDesignPage(View):

    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.engine = engine
        self.task_name = task_name

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
        self.spec_var = tk.IntVar()
        self.ksd_var = tk.IntVar()
        self.popln_var = tk.IntVar()
        self.output_freq = tk.IntVar()


        self.SubFrame1 = self.input_param_frame 

        self.SubFrame2 = self.property_frame 

        self.SubFrame3 = self.submit_button_frame 

        self.Frame_button1 = self.save_button_frame 

        self.Frame2 = ttk.Frame(self.SubFrame1)
        self.Frame2.grid(row=0, column=0)

        self.frame_pol = ttk.Frame(self.SubFrame1)
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

        self.entry_strength = EntryPattern(self.Frame2,textvariable= self.strength)
        self.entry_strength['font'] = myFont
        self.entry_strength.grid(row=3, column=1)
        self.strength.set('01e-05')
        
        # print(self.strength.get())
        # self.entry_strength['state'] = 'readonly'
    
        # instr = ["1e-5","1e-4","1e-3"]
        # self.entry_strength = ttk.Combobox(self.Frame2,textvariable= self.strength, value = instr)
        # self.entry_strength['font'] = myFont
        # self.entry_strength.current(0)
        # self.entry_strength.grid(row=3, column=1)
        # self.entry_strength['state'] = 'readonly'

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

        Laser_button = tk.Button(self.Frame2,text="Laser Design",activebackground="#78d6ff",command=lambda:[self.laser_button()])
        Laser_button['font'] = myFont
        Laser_button.grid(row=8, column=10, sticky='nsew', padx=30, pady=5)

        self.label_pol = tk.Label(self.frame_pol,text="Polarization Direction:",bg="gray",fg="black")
        self.label_pol['font'] = myFont
        self.label_pol.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        values = {"X": 0, "Y": 1, "Z": 2}
        for (text, value) in values.items():
            tk.Radiobutton(self.frame_pol, text=text, variable=self.pol_var, font=myfont2(),
             justify='left',value=value).grid(row=0, column=value+1, sticky='w')

        property_frame(self, self.property_frame, myFont, spectra_var= self.spec_var,
                                ksd_var=self.ksd_var, pop_var=self.popln_var,
                                output_freq_var=self.output_freq)
        
        Back_Button1 = tk.Button(self.Frame_button1, text="Back",activebackground="#78d6ff",command=lambda:self.back_button())
        Back_Button1['font'] = myFont
        Back_Button1.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

        Generate_button = tk.Button(self.Frame_button1,text="Generate Input",activebackground="#78d6ff", command= self.generate_input)
        Generate_button['font'] = myFont
        Generate_button.grid(row=0, column=1, sticky='nsew', padx=30, pady=5)

        Save_button = tk.Button(self.Frame_button1,text="Save Input",activebackground="#78d6ff", command=self.save_input)
        Save_button['font'] = myFont
        Save_button.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        self.label_msg = tk.Label(self.Frame_button1,text="",fg="black")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=3, sticky='nsew', padx=5, pady=5)

        add_job_frame(self, self.SubFrame3,self.task_name, row= 0, column=0)
        
      
    def laser_button(self):
        self.event_generate('<<DesignLaser>>')
   
    def generate_input(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def save_input(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')

    def get_pol_list(self): 
        if self.pol_var.get() == 0:
            pol_list = [1,0,0]
            pol = 'x'        
        elif self.pol_var.get() == 1:
            pol_list = [0,1,0]
            pol = 'y' 
        elif self.pol_var.get() == 2:
            pol_list = [0,0,1]
            pol = 'z'                
        return pol_list, pol

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
        
        from litesoph.utilities.units import au_to_fs,autime_to_eV, as_to_au
        laser_param = self.laser_design_dict 
        self.pol_list, pol = self.get_pol_list()              
        # epol_list = [int(self.pol_x.get()),int(self.pol_y.get()),int(self.pol_z.get())]
       
        if self.engine == 'gpaw':
            abs_x = float(self.strength.get())*float(self.pol_list[0])
            abs_y = float(self.strength.get())*float(self.pol_list[1])
            abs_z = float(self.strength.get())*float(self.pol_list[2])
            abs_list = [abs_x, abs_y, abs_z]
            inp_list = [float(self.ts.get()),int(self.ns.get())]
            analysis_tools= ['dipole']
            if self.ksd_var.get() == 1:
                analysis_tools.append('wavefunction')
            if self.popln_var.get() == 1:
                analysis_tools.append('population')

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
                        'laser': laser_param,
                        'analysis_tools': analysis_tools,
                        'output_freq': self.output_freq.get()}
            # print(td_gpaw)            
            return td_gpaw
            
        elif self.engine == 'octopus':
            # td_oct = {  'e_pol' :self.pol_list,
            #             'max_step' : self.ns.get(),
            #             'time_step': self.ts.get(),
            #             'strength' : self.strength.get(),
            #             'time0' :laser_param['time0'],
            #             'sigma' : laser_param['sigma'],
            #             'frequency': self.frequency.get()
            #         }
            td_oct = { 
                'CalculationMode': 'td', 
                'TDPropagator': 'aetrs',
                'TDMaxSteps' : self.ns.get(),
                'TDTimeStep': round(self.ts.get()*as_to_au, 2),
                'TDFunctions': [[str('"'+"envelope_gauss"+'"'),'tdf_gaussian',
                                self.strength.get(),
                                laser_param['sigma'],laser_param['time0']
                                ]],                
                'TDExternalFields': [['electric_field',
                                    self.pol_list[0],self.pol_list[1],self.pol_list[2],
                                    str(self.frequency.get())+"*eV",
                                    str('"'+"envelope_gauss"+'"')
                                    ]]
                    }
            # print(td_oct)            
            return td_oct        
                      
        elif self.engine == 'nwchem':
            from litesoph.utilities.units import as_to_au
            
            td_nwchem = {
            'task':'rt_tddft_delta',
            'rt_tddft':{'tmax': round(self.ns.get() * self.ts.get() * as_to_au,2),
                        'dt': round(self.ts.get() * as_to_au, 2),
                        'field':{'name': 'gpulse_' + pol,
                                'type': 'gaussian',
                                'frequency' : self.frequency.get(),
                                'center': laser_param['time0'],
                                'width': laser_param['sigma'],
                                'polarization':pol,
                                'max':self.strength.get()},
            'print': ['dipole', 'moocc' if self.popln_var.get() == 1 else '']}}
            return td_nwchem

    def back_button(self):
        self.event_generate(actions.SHOW_WORK_MANAGER_PAGE)

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg) 

   

class PlotSpectraPage(ttk.Frame):

    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.engine = engine
        self.task_name = task_name
        
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

        self.add_job_frame(self, self.task_name, r=0, c=1)        

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

        Frame_Button1 = tk.Button(self.button_frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
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
        self.event_generate(f"<<Show{self.task_name}Plot>>")


    def get_parameters(self):
        td_dict_gp = {
            'del_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()       
        }
        
        # td_dict_oct = {
        #     'del_e':self._var['del_e'].get(),
        #     'e_max':self._var['e_max'].get(),
        #     'e_min': self._var['e_min'].get()
        #   }
        
        td_dict_oct = {
            "UnitsOutput": 'eV_angstrom',
            "PropagationSpectrumEnergyStep": str(self._var['del_e'].get())+"*eV",
            "PropagationSpectrumMaxEnergy": str(self._var['e_max'].get())+"*eV",
            "PropagationSpectrumMinEnergy": str(self._var['e_min'].get())+"*eV"
          }
        
        if self.engine == 'gpaw':
            return td_dict_gp
        elif self.engine == 'nwchem':
            td_dict_nwchem = {
            'task': 'spectrum',
            'del_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()
            }
            return td_dict_nwchem
        elif self.engine == 'octopus':
            return td_dict_oct            

class TcmPage(ttk.Frame):

    def __init__(self, parent,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
        self.parent = parent
        self.job = None
        self.task_name = task_name

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

        Frame_Button1 = tk.Button(self.frame_button, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        Frame_Button1['font'] = myfont()
        Frame_Button1.grid(row=0, column=0)

        self.engine_name.trace_add(['write'], lambda *_:self.select_ksd_frame(self.frame_inp))
        self.add_job_frame(task_name)

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

        self.plot_button = tk.Button(self.Frame3, text="Plot", activebackground="#78d6ff", command=lambda: self.event_generate(f"<<Show{task_name}Plot>>"))
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

class PopulationPage(View):
    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.engine = engine
        self.task_name = task_name
        
        self.bandpass = tk.IntVar(value=100)
        self.hanning = tk.IntVar(value= 50)
        self.occupied_mo = tk.IntVar()
        self.unoccupied_mo = tk.IntVar()
        self.ngrid = tk.IntVar(value=100)
        self.broadening = tk.DoubleVar(value= 0.5)

        self.SubFrame1 = self.input_param_frame 

        self.SubFrame2 = self.property_frame 

        self.SubFrame3 = self.submit_button_frame 

        self.Frame_button1 = self.save_button_frame 

        self.Frame1_label_path = tk.Label(self.SubFrame1,text="LITESOPH Input for Population Correlation", fg='blue')
        self.Frame1_label_path['font'] = myfont()
        self.Frame1_label_path.grid(row=0, column=0, padx=5, pady=10)

        self.Label_ni = tk.Label(self.SubFrame1,text="Number of occupied states(HOMO & below)",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_ni['font'] = myfont()
        self.Label_ni.grid(row=1, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_ni = Onlydigits(self.SubFrame1, textvariable= self.occupied_mo, width=5)
        self.entry_ni['font'] = myfont()
        self.entry_ni.grid(row=1, column=1)

        self.Label_na = tk.Label(self.SubFrame1,text="Number of unoccupied states(LUMO & above)",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_na['font'] = myfont()
        self.Label_na.grid(row=2, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_na = Onlydigits(self.SubFrame1, textvariable= self.unoccupied_mo, width=5)
        self.entry_na['font'] = myfont()
        self.entry_na.grid(row=2, column=1)

        self.label_bandpass = tk.Label(self.SubFrame1,text="Bandpass",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.label_bandpass['font'] = myfont()
        self.label_bandpass.grid(row=3, column=0, sticky='w', padx=5, pady=5)

        self.entry_bandpass = Onlydigits(self.SubFrame1, textvariable= self.bandpass, width=5)
        self.entry_bandpass['font'] = myfont()
        self.entry_bandpass.grid(row=3, column=1)
        
        self.label_hanning = tk.Label(self.SubFrame1,text="Hanning",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.label_hanning['font'] = myfont()
        self.label_hanning.grid(row=4, column=0, sticky='w', padx=5, pady=5)

        self.entry_hanning = Onlydigits(self.SubFrame1, textvariable= self.hanning, width=5)
        self.entry_hanning['font'] = myfont()
        self.entry_hanning.grid(row=4, column=1)

        self.label_plot = tk.Label(self.SubFrame2,text="Plotting Parameters", fg='blue')
        self.label_plot['font'] = myfont()
        self.label_plot.grid(row=0, column=0, padx=5, pady=10)

        self.Label_grid = tk.Label(self.SubFrame2,text="Number of mesh grids",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_grid['font'] = myfont()
        self.Label_grid.grid(row=1, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_grid = Onlydigits(self.SubFrame2, textvariable= self.ngrid, width=5)
        self.entry_grid['font'] = myfont()
        self.entry_grid.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        self.Label_width = tk.Label(self.SubFrame2,text="Broadening width",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_width['font'] = myfont()
        self.Label_width.grid(row=2, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_width = Onlydigits(self.SubFrame2, textvariable= self.broadening, width=5)
        self.entry_width['font'] = myfont()
        self.entry_width.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        self.submit_button = tk.Button(self.SubFrame1, text="Submit",activebackground="#78d6ff", command=self._on_submit)
        self.submit_button['font'] = myfont()
        self.submit_button.grid(row=4, column=2, sticky='we', padx=5)

        self.plot_button = tk.Button(self.SubFrame2, text="Plot",activebackground="#78d6ff", command=self._on_plot)
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=2, column=2, sticky='we', padx=25)

        self.back_button = tk.Button(self.Frame_button1, text="Back ",activebackground="#78d6ff", command=lambda : self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0, padx=10, sticky='nswe')

        # add_job_frame(self, self.SubFrame3,self.task_name, row= 0, column=1)
    def _on_submit(self):
        self.event_generate(f"<<SubLocal{self.task_name}>>")

    def _on_plot(self):
        self.event_generate(f"<<Plot{self.task_name}>>")

    def get_parameters(self):
        pop_dict = {
            'task': self.task_name,
            'num_occupied_mo': self.occupied_mo.get(),
            'num_unoccpied_mo': self.unoccupied_mo.get(),
            'bandpass_window': self.bandpass.get(),
            'hanning_window' : self.hanning.get()
        }

        return pop_dict

    def get_plot_parameters(self):
        plot_param = {
            'ngrid' : self.ngrid.get(),
            'broadening' : self.broadening.get()
        }
        return plot_param

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
        self.Frame1.pack(fill=tk.BOTH)
        self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame_button.pack(fill=tk.BOTH)

        self.sub_job_frame = ttk.Frame(self.Frame1)
        self.sub_job_frame.grid(row=1, column=0, sticky='nsew')

        self.show_job_frame()

        self.Frame_label = tk.Label(self.Frame1, text="LITESOPH Job Submission", fg='blue')
        self.Frame_label['font'] = myfont1()
        self.Frame_label.grid(row=0, column=0)       

        view_btn = tk.Button(self.Frame1, text="View Output",activebackground="#78d6ff",command=lambda:[self.view_outfile(self.task)])
        view_btn['font'] = myfont()
        view_btn.grid(row=2, column=0, sticky='e', pady=5)

        back = tk.Button(self.frame_button, text="Back ",activebackground="#78d6ff",command=lambda:[self.event_generate(f'<<Show{self.task}Page>>')])
        back['font'] = myfont()
        back.pack(side= tk.LEFT)

        back2main = tk.Button(self.frame_button, text="Back to main page",activebackground="#78d6ff",command=lambda:[self.event_generate(actions.SHOW_WORK_MANAGER_PAGE)])
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
        save_job_script.grid(row=4,column=1,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff",command=lambda:[self.submitjob_local()])
        self.run_button['font'] = myfont()
        self.run_button.grid(row=5, column=0,sticky='nsew', pady=5)        

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
        save_job_script.grid(row=9,column=1,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff", command=lambda:[self.submitjob_network()])
        self.run_button['font'] = myfont()
        self.run_button.grid(row=10,column=0,sticky='nsew', padx=2, pady=4)    

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

    def set_run_button_state(self, state):
        self.run_button.config(state=state)

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


####### popup filemenu #########

class CreateProjectPage(Toplevel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._default_var = {
              'proj_path' : ['str'],
              'proj_name' : ['str'],
              
          }

        self._var = var_define(self._default_var)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self.title("Create New Project")     
        self.geometry("550x200")

        self.label_proj = Label(self,text="Project Name",bg=label_design['bg'],fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(column=0, row= 3, sticky=tk.W,  pady=10, padx=10)  

        self.entry_proj = Entry(self,textvariable=self._var['proj_name'])
        self.entry_proj['font'] = myfont()
        self.entry_proj.grid(column=1, row= 3, sticky=tk.W)
        self.entry_proj.delete(0, tk.END)

        self.button_project = Button(self,text="Create New Project",width=18, activebackground="#78d6ff",command= lambda :self.event_generate('<<CreateNewProject>>'))
        self.button_project['font'] = myfont()
        self.button_project.grid(column=2, row= 3, sticky=tk.W, padx= 10, pady=10)  
            
    def get_value(self, key):
        return self._var[key].get()

    
