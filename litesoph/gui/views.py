import copy
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox
from typing import Any, Dict
from  PIL import Image,ImageTk
from tkinter import font

from litesoph.common.data_sturcture.data_types import DataTypes as DT
from litesoph.gui import actions, images
from litesoph.gui.input_validation import EntryPattern, Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15
from litesoph.common.models import AutoModeModel
from litesoph.gui.engine_views import get_gs_engine_page
from litesoph.gui.models import inputs as inp


def show_message(label_name, message):
    """ Shows a update """

    label_name['text'] = message
    label_name['foreground'] = 'black'

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

def add_tabs(parent, *args, **kwargs):
    style = ttk.Style()
    notebook = ttk.Notebook(parent)
    notebook.pack(fill=tk.BOTH, expand=True)
    # notebook.grid(row=0,column=0, sticky='nsew')
    style.configure("TNotebook.Tab",font=('Helvetica','10'))
   
    tabs_dict = kwargs.get('Tabs')        
    if isinstance(tabs_dict, dict):
        for key,value in tabs_dict.items():
            setattr(parent, key, ttk.Frame(notebook))
            notebook.add(getattr(parent,key), text = value) 

def set_state(widget, state):
    if widget.winfo_children():
        for child in widget.winfo_children():        
            if isinstance(child, ttk.Frame):
                set_state(child, state)
            else:
                child.configure(state = state)      
    else:
        widget.configure(state = state)   

class StartPage(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        mainframe = ttk.Frame(self)
        mainframe.pack(fill=tk.BOTH)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.BOTH)
        myFont = font.Font(family='Helvetica', size=25, weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')
        
        gui_style = ttk.Style()
        gui_style.configure('TButton', foreground='black',background='gainsboro',font=('Helvetica', 20))

        # create a canvas to show image on
        canvas_for_image = tk.Canvas(mainframe, bg='gray', height=200, width=200, borderwidth=0, highlightthickness=0)
        canvas_for_image.pack(side=tk.LEFT,  anchor='nw', padx=15, pady=50)

        image = Image.open(images.LITESOPH_LOGO_BIG)
        canvas_for_image.image = ImageTk.PhotoImage(image.resize((200, 200), Image.ANTIALIAS))
        canvas_for_image.create_image(0,0,image=canvas_for_image.image, anchor='nw')

        welcome_label = tk.Label(mainframe,text="Welcome to LITESOPH",fg='blue')
        welcome_label['font'] = myFont
        welcome_label.pack(side=tk.TOP,padx=(10,50), pady=(100, 150), anchor='nw')

        explain_label = tk.Label(button_frame,text="Layer Integrated Toolkit \n and Engine for Simulations of Photo-induced Phenomena",fg='blue')
        explain_label['font'] = l
        explain_label.pack(side=tk.TOP, padx=100, pady=(100,20))

        self.button_create_project = tk.Button(button_frame,text="Create LITESOPH Project",  width= 30)
        self.button_create_project['font'] = l
        self.button_create_project.pack(side=tk.TOP)

        self.button_open_project = tk.Button(button_frame,text="Open LITESOPH Project", width= 30)
        self.button_open_project['font'] = l
        self.button_open_project.pack(side=tk.TOP)

        self.button_about_litesoph = tk.Button(button_frame,text="About LITESOPH", width= 30)
        self.button_about_litesoph['font'] = l
        self.button_about_litesoph.pack(side=tk.TOP)

class WorkManagerPage(ttk.Frame):

    MainTask = ["Preprocessing Jobs","Simulations","Postprocessing Jobs"]
    Pre_task = ["Ground State"]
    Sim_task = ["Delta Kick","Gaussian Pulse"]
    Post_task = ["Compute Spectrum","Kohn Sham Decomposition","Population Tracking", "Masking", "Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]
    engine_list = ['auto-mode','gpaw', 'nwchem', 'octopus']

    env_list = ['Gas Phase', 'Solvation Condition']

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)

        self._default_var = {
            'task' : ['str', '--choose job task--'],
            'sub_task' : ['str'],
            'dynamics': ['str','--dynamics type--'],
            'laser': ['str','-- laser type--'],
            'plot':['str', '-- choose option --'],
            'select_wf_option':['int', 1],
            'environment':['str'],
            'workflow':['str'],
            'charge': ['int', 0],
            'multiplicity': ['int', 1]
        }

        self.workflow_list = []
        self.parent = parent
        self.engine = tk.StringVar(value='auto-mode')
        self._var = var_define(self._default_var)
        
        self.plot_option = None

        self.frame_workflow = ttk.Frame(self)
        self.frame_workflow.grid(row=0, column=1, rowspan=3)

        self.Frame2 = ttk.Labelframe(self)
        self.Frame2.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        # self.grid_columnconfigure(1, weight=1)
        self.Frame2.configure(relief='groove',borderwidth="2",cursor="fleur")

        system_frame = ttk.Frame(self.Frame2)
        system_frame.grid(row=0, column=0, sticky='nsew')

        self.task_common_frame = ttk.Frame(self.Frame2)
        self.task_common_frame.grid(row=1, column=0, sticky='nsew')

        #-----------------------------------------------------------------------------------------

        self.label_upload_geom = tk.Label(system_frame, text="Upload Geometry",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_upload_geom['font'] = myfont()
        self.label_upload_geom.grid(row= 0,column=0, sticky='w', padx=5,  pady=5)       

        self.button_select_geom = tk.Button(system_frame,text="Select",width=6,activebackground="#78d6ff",command=self._get_geometry_file)
        self.button_select_geom['font'] = myfont()
        self.button_select_geom.grid(row= 0,column=1, padx=5)       

        self.label_message_upload = tk.Label(system_frame, text='', foreground='red')
        self.label_message_upload['font'] = myfont()
        self.label_message_upload.grid(row= 0,column=2, padx=5,  pady=5)       
        
        self.button_view = tk.Button(system_frame,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.button_view['font'] = myfont()
        self.button_view.grid(row= 0,column=3)

        self.label_charge = tk.Label(system_frame, text="Charge",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_charge['font'] = myfont()
        self.label_charge.grid(row=1,column=0, sticky='w', padx=5,  pady=5)       

        self.entry_charge = tk.Entry(system_frame,width=6, textvariable=self._var['charge'])
        self.entry_charge['font'] = myfont()
        self.entry_charge.grid(row=1, column=1, padx=5,  pady=5)

        self.label_multiplicity = tk.Label(system_frame, text="Multiplicity",  bg=label_design['bg'],fg=label_design['fg'])  
        self.label_multiplicity['font'] = myfont()
        self.label_multiplicity.grid(row=2, column=0, sticky='w', padx=5,  pady=5)       

        self.entry_multiplicity = tk.Entry(system_frame,width=6,  textvariable=self._var['multiplicity'])
        self.entry_multiplicity['font'] = myfont()
        self.entry_multiplicity.grid(row=2, column=1, padx=5,  pady=5)

        # self.engine_source_label = tk.Label(system_frame,text="Source",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        # self.engine_source_label['font'] = myfont()
        # self.engine_source_label.grid(row= 3, column=0,  sticky='w',padx=4, pady=10)       
            
        # self.engine_source = ttk.Combobox(system_frame,width=20, textvariable= self.engine, values= self.engine_list)
        # self.engine_source['font'] = myfont()
        # self.engine_source.grid(row= 3, column=1, columnspan=2, padx=4, pady=10)
        # self.engine_source['state'] = 'readonly'

        self.label_select_option = tk.Label(system_frame, text="Select Option:",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_select_option['font'] = myfont()
        self.label_select_option.grid(row=4, column=0, sticky='w', padx=5,  pady=5)   

        values = [1,2]
        text = ["Workflow mode"," Task mode"]
        command = [lambda:self.show_specific_workflow_frame(self.task_common_frame),
                   lambda:self.show_general_workflow_frame(self.task_common_frame)]        

        for (txt, val, cmd) in zip(text, values, command):
            tk.Radiobutton(system_frame, text=txt, variable=self._var['select_wf_option'], font=myfont2(),
             justify='left',value=val, command=cmd).grid(row=4, column=val, ipady=5, sticky='w')    
        self._var['select_wf_option'].trace_add('write', self.choose_workflow_frame)
        #self.show_specific_workflow_frame(self.task_common_frame)
        self.choose_workflow_frame()
        #--------------------------------Button Frame------------------------------------------------------------------        
       
        # self.Frame3 = ttk.Frame(self)
        # self.Frame3.grid(column=0, row=2,  sticky=(tk.N, tk.W, tk.E, tk.S)) 

        # self.Frame3.configure(relief='groove',borderwidth="2",cursor="fleur")

        # self.button_proceed = tk.Button(self.Frame3, text="Proceed",activebackground="#78d6ff",command=self.proceed_button)
        # self.button_proceed['font'] = myfont()
        # self.button_proceed.pack(side=tk.RIGHT, padx=10)

    def choose_workflow_frame(self, *_):
        if self._var['select_wf_option'].get() == 1:
            self.show_specific_workflow_frame(self.task_common_frame)
        elif self._var['select_wf_option'].get() == 2:
            self.show_general_workflow_frame(self.task_common_frame)

    def show_specific_workflow_frame(self, parent):
        """Creates the specific workflow frame"""

        for widget in parent.winfo_children():
            widget.destroy()

        self.workflow_frame = ttk.Frame(parent)
        self.workflow_frame.grid(row=0, column=0)

        self.label_environment = tk.Label(self.workflow_frame, text="Environment",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_environment['font'] = myfont()
        self.label_environment.grid(row=0, column=0, sticky='w', padx=5,  pady=10)       

        self.entry_environment = ttk.Combobox(self.workflow_frame, textvariable=self._var['environment'], values= self.env_list)
        self.entry_environment['font'] = myfont()
        self.entry_environment.current(0)
        self.entry_environment.config(state='readonly')
        self.entry_environment.grid(row=0, column=1, padx=10, sticky='ew')

        self.label_workflow = tk.Label(self.workflow_frame, text="Work Flow",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_workflow['font'] = myfont()
        self.label_workflow.grid(row=1, column=0, sticky='w', padx=5,  pady=10)       

        self.entry_workflow = ttk.Combobox(self.workflow_frame, textvariable=self._var['workflow'],width=22, values= self.workflow_list)
        self.entry_workflow['font'] = myfont()
        #self.entry_workflow.current(0)
        self.entry_workflow.config(state='readonly')
        self.entry_workflow.grid(row=1, column=1, padx=10, sticky='ew')
    
    def show_general_workflow_frame(self, parent):
        """Creates the general workflow frame"""

        if self.frame_workflow.winfo_children():
            for widget in self.frame_workflow.winfo_children():
                widget.destroy()

        for widget in parent.winfo_children():
            widget.destroy()

        self.workflow_frame = ttk.Frame(parent)
        self.workflow_frame.grid(row=0, column=0)

        _task_frame1 = ttk.Frame(self.workflow_frame)
        _task_frame1.grid(row=0, column=0, sticky='w')

        self._task_frame2 = ttk.Frame(self.workflow_frame)
        self._task_frame2.grid(row=1, column=0, sticky='w')

        # self.engine_source_label = tk.Label(_task_frame1,text="Source",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        # self.engine_source_label['font'] = myfont()
        # self.engine_source_label.grid(row= 1, column=0,  sticky='w',padx=4, pady=10)       
            
        # self.engine_source = ttk.Combobox(_task_frame1,width=20, textvariable= self.engine, values= self.engine_list)
        # self.engine_source['font'] = myfont()
        # self.engine_source.grid(row= 1, column=1, columnspan=2, padx=4, pady=10)
        # self.engine_source['state'] = 'readonly'

        self.label_job_type = tk.Label(_task_frame1,text="Job Type",bg=label_design['bg'],fg=label_design['fg'], justify='left')
        self.label_job_type['font'] = myfont()
        self.label_job_type.grid(row= 2, column=0,  sticky='w', padx=4, pady=10)       
            
        self.entry_job_type = ttk.Combobox(_task_frame1, width=20, textvariable= self._var['task'], values= self.MainTask)
        self.entry_job_type['font'] = myfont()
        self.entry_job_type.grid(row= 2, column=1, columnspan=2, padx=4, pady=10)
       
        self.entry_job_type.bind("<<ComboboxSelected>>", self.pick_task)
        self.entry_job_type['state'] = 'readonly'

        self.show_sub_task_frame(self._task_frame2)


    def show_sub_task_frame(self,parent):
        
        for widget in parent.winfo_children():
            widget.destroy()
  
        common_sub_task_frame = ttk.Frame(parent)       
        common_sub_task_frame.grid(row=0, column=0)  

        self.Frame2_label_3 = tk.Label(common_sub_task_frame, text="Sub Task",bg=label_design['bg'],fg=label_design['fg'])
        self.Frame2_label_3['font'] = myfont()
        self.Frame2_label_3.grid( row= 0,column=0, sticky='w', padx=4, pady=10) 
        
        self.entry_sub_task = ttk.Combobox(common_sub_task_frame, width= 20, textvariable=self._var['sub_task'], value = [''])
        self.entry_sub_task['font'] = myfont()
        self.entry_sub_task.current(0)
        self.entry_sub_task.grid(row= 0, column=1,  pady=10, padx=4)     
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
        self.sub_task_label.grid(column=0, row= 0, sticky='w', padx=4, pady=10)        
          
        self.dynamics_type = ttk.Combobox(sim_sub_task_frame, width= 15, textvariable=self._var['dynamics'], value = ['electrons', 'electron+ion','ions'])
        self.dynamics_type['font'] = myfont()
        self.dynamics_type.set('--dynamics type--')
        self.dynamics_type.grid(column=1, row= 0,  pady=10, padx=4)       
        self.dynamics_type['state'] = 'readonly'  

        self.laser_type = ttk.Combobox(sim_sub_task_frame, width= 13, textvariable=self._var['laser'], value = ['None', 'Delta Pulse', 'Gaussian Pulse', 'Customised Pulse'])
        self.laser_type['font'] = myfont()
        self.laser_type.set('-- laser type--')
        self.laser_type.grid(column=2, row= 0, sticky='nsew',  pady=10, padx=10)       
        self.laser_type['state'] = 'readonly'       

    def show_plot_option_frame(self, parent):
        
        self.plot_option = ttk.Combobox(parent, width= 15, textvariable=self._var['plot'], value = ['Spectrum', 'Dipole Moment', 'Laser'])
        self.plot_option['font'] = myfont()
        self.plot_option.set('--choose option--')
        self.plot_option.grid(column=1, row= 0, sticky='nsew', pady=10, padx=3)       
        self.plot_option['state'] = 'readonly'

    def pick_task(self, *_):
        if self._var['task'].get() == "Preprocessing Jobs":
            self.show_sub_task_frame(self._task_frame2)
            self.entry_sub_task.config(value = self.Pre_task)
            self.entry_sub_task.current(0)
        elif self._var['task'].get() == "Simulations":
            self.show_sim_task_frame(self._task_frame2)
        elif self._var['task'].get() == "Postprocessing Jobs":
            self.show_sub_task_frame(self._task_frame2)
            self.entry_sub_task.config(value = self.Post_task)
            self.entry_sub_task.current(0)                

    def pick_sub_task(self,*_):
        if self._var['sub_task'].get() == "Plot":
            self.show_plot_option_frame(self._task_frame2)
        else:
            if self.plot_option:
                self.plot_option.destroy()    
            
    def _get_geometry_file(self):
        self.event_generate(actions.GET_MOLECULE)
        
    def _geom_visual(self):
        self.event_generate(actions.VISUALIZE_MOLECULE)

    def proceed_button(self):
        """ event generate on proceed button"""

        self.event_generate(actions.ON_PROCEED)   

    def show_upload_label(self):
        show_message(self.label_message_upload,"Uploaded")

    def get_value(self, key):
        return self._var[key].get()

    def set_value(self,key,value):
        self._var[key].set(value)

    def get_parameters(self) -> Dict[str, Any]:
        param = {}
        for key in self._var.keys():
            param[key] = self._var[key].get()
        param['engine'] = self.engine.get()
        return param
        
    def refresh_var(self):
        for key, value in self._default_var.items():
            try:
                self._var[key].set(value[1])
            except IndexError:
                self._var[key].set('')    

class SystemInfoPage(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._default_var = {
                'charge': ['int', 0],
                'multiplicity': ['int', 1]
            }
        
        system_frame = ttk.Frame(self)
        system_frame.grid(row=0, column=0, sticky='nsew')

        self.label_upload_geom = tk.Label(system_frame, text="Upload Geometry",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_upload_geom['font'] = myfont()
        self.label_upload_geom.grid(row= 0,column=0, sticky='w', padx=5,  pady=5)       

        self.button_select_geom = tk.Button(system_frame,text="Select",width=6,activebackground="#78d6ff",command=self._get_geometry_file)
        self.button_select_geom['font'] = myfont()
        self.button_select_geom.grid(row= 0,column=1, padx=5)       

        self.label_message_upload = tk.Label(system_frame, text='', foreground='red')
        self.label_message_upload['font'] = myfont()
        self.label_message_upload.grid(row= 0,column=2, padx=5,  pady=5)       
        
        self.button_view = tk.Button(system_frame,text="View",activebackground="#78d6ff",command=self._geom_visual)
        self.button_view['font'] = myfont()
        self.button_view.grid(row= 0,column=3)

        self.label_charge = tk.Label(system_frame, text="Charge",bg=label_design['bg'],fg=label_design['fg'])  
        self.label_charge['font'] = myfont()
        self.label_charge.grid(row=1,column=0, sticky='w', padx=5,  pady=5)       

        self.entry_charge = tk.Entry(system_frame,width=6, textvariable=self._var['charge'])
        self.entry_charge['font'] = myfont()
        self.entry_charge.grid(row=1, column=1, padx=5,  pady=5)

        self.label_multiplicity = tk.Label(system_frame, text="Multiplicity",  bg=label_design['bg'],fg=label_design['fg'])  
        self.label_multiplicity['font'] = myfont()
        self.label_multiplicity.grid(row=2, column=0, sticky='w', padx=5,  pady=5)       

        self.entry_multiplicity = tk.Entry(system_frame,width=6,  textvariable=self._var['multiplicity'])
        self.entry_multiplicity['font'] = myfont()
        self.entry_multiplicity.grid(row=2, column=1, padx=5,  pady=5)

    def _get_geometry_file(self):
        self.event_generate(actions.GET_MOLECULE)
        
    def _geom_visual(self):
        self.event_generate(actions.VISUALIZE_MOLECULE)

    def show_upload_label(self):
        show_message(self.label_message_upload,"Uploaded")

    def get_parameters(self):
        pass

    def set_parameters(self):
        pass
    
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

class JobSubPage(ttk.Frame):
    """ Creates widgets for JobSub Page"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        
        self.parent = parent
        self.runlocal_np =  None
        self.run_script_path = None
        
        self.processors = tk.IntVar()
        self.ip = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.pkey_file = tk.StringVar()
        self.rpath = tk.StringVar()
        self.port = tk.IntVar()
        self.network_job_type = tk.IntVar()
        self.sub_command = tk.StringVar()
        self.sub_job_type = tk.IntVar()
        self.password_option = tk.IntVar()

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

        self.Frame_label = tk.Label(self.Frame1, text="LITESOPH Job Submission", fg='blue')
        self.Frame_label['font'] = myfont1()
        self.Frame_label.grid(row=0, column=0)       

        self.view_output_button = tk.Button(self.Frame1, text="View Output",activebackground="#78d6ff",command=lambda:[self.view_outfile(self.task)])
        self.view_output_button['font'] = myfont()
        self.view_output_button.grid(row=2, column=0, sticky='e', pady=5)

        self.back2task = tk.Button(self.frame_button, text="Back ",activebackground="#78d6ff")
        self.back2task['font'] = myfont()
        self.back2task.pack(side= tk.LEFT)

        self.back2main = tk.Button(self.frame_button, text="Back to main page",activebackground="#78d6ff")
        self.back2main['font'] = myfont()
        self.back2main.pack(side= tk.RIGHT)

    
    def set_network_profile(self, remote_profile: dict):
        self.username.set(remote_profile['username'])
        self.ip.set(remote_profile['ip'])
        self.port.set(remote_profile['port'])
        self.rpath.set(remote_profile['remote_path'])


    def show_run_local(self,
                        generate_job_script: callable,
                        save_job_script: callable,
                        submit_job: callable):

        """ Creates Local JobSub input widgets""" 
        
        for widget in self.sub_job_frame.winfo_children():
            widget.destroy()
        
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

        self.generate_job_button = tk.Button(self.sub_job_frame, text="Generate Job Script",activebackground="#78d6ff",command = generate_job_script)
        self.generate_job_button['font'] = myfont()
        self.generate_job_button.grid(row=4, column=0, pady=5)   

        self.save_job_button = tk.Button(self.sub_job_frame, text="Save Job Script",activebackground="#78d6ff",command = save_job_script)
        self.save_job_button['font'] = myfont()
        self.save_job_button.grid(row=4,column=1,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff",command= submit_job)
        self.run_button['font'] = myfont()
        self.run_button.grid(row=5, column=0,sticky='nsew', pady=5)        

    def show_run_network(self,
                        generate_job_script: callable,
                        save_job_script: callable,
                        submit_job: callable):

        """ Creates Network JobSub input widgets""" 
        for widget in self.sub_job_frame.winfo_children():
            widget.destroy()

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

        values = [0, 1]
        txt=["With Password", "Password-less ssh"]
        command = [lambda:[set_state(self.password_entry, 'normal')],
                lambda:[set_state(self.password_entry, 'disabled')]]
                
        for (text, value, cmd) in zip(txt,values,command):            
            tk.Radiobutton(self.sub_job_frame,  text=text,  variable=self.password_option, font=myfont2(),
             justify='left',value=value,command=cmd).grid(row=value+5, column=0, ipady=5, sticky='w')
 
        # password_label = tk.Label(self.sub_job_frame, text= "Password", bg='gray', fg='black')
        # password_label['font'] = myfont()
        # password_label.grid(row=5,column=0,sticky='nsew', padx=2, pady=4)

        self.password_entry = tk.Entry(self.sub_job_frame,textvariable= self.password, width=20, show = '*')
        self.password_entry['font'] = myfont()
        self.password_entry.grid(row=5,column=1,sticky='nsew', padx=2, pady=4)

        self.pkey_file_entry = tk.Entry(self.sub_job_frame,textvariable= self.pkey_file, width=20, show = '*')
        self.pkey_file_entry['font'] = myfont()
        self.pkey_file_entry.grid(row=6,column=1,sticky='nsew', padx=2, pady=4)

        remote_path_label = tk.Label(self.sub_job_frame, text= "Remote Path", bg='gray', fg='black')
        remote_path_label['font'] = myfont()
        remote_path_label.grid(row=7,column=0,sticky='nsew', padx=2, pady=4)

        remote_path_entry = tk.Entry(self.sub_job_frame,textvariable= self.rpath, width=20)
        remote_path_entry['font'] = myfont()
        remote_path_entry.grid(row=7,column=1,sticky='nsew', padx=2, pady=4)

        num_processor_label = tk.Label(self.sub_job_frame, text= "Number of Processors", bg='gray', fg='black')
        num_processor_label['font'] = myfont()
        num_processor_label.grid(row=8,column=0,sticky='nsew', padx=2, pady=4)

        num_processor_entry = Onlydigits(self.sub_job_frame,textvariable= self.processors, width=20)
        num_processor_entry['font'] = myfont()
        num_processor_entry.grid(row=8,column=1,sticky='nsew', padx=2, pady=4)

        self.label_command = tk.Label(self.sub_job_frame, text="Submit command", bg='gray', fg='black')
        self.label_command['font'] = myfont()
        self.label_command.grid(row=9, column=0,sticky='nsew', padx=5, pady=5)

        self.entry_command = tk.Entry(self.sub_job_frame, textvariable=self.sub_command)
        self.entry_command['font'] = myfont()
        self.entry_command.grid(row=9, column=1, ipadx=2, ipady=2)
      
        self.generate_job_button = tk.Button(self.sub_job_frame, text="Generate Job Script",activebackground="#78d6ff",command = generate_job_script)
        self.generate_job_button['font'] = myfont()
        self.generate_job_button.grid(row=10,column=0,sticky='nsew', padx=2, pady=4)

        self.save_job_button = tk.Button(self.sub_job_frame, text="Save Job Script",activebackground="#78d6ff",command = save_job_script)
        self.save_job_button['font'] = myfont()
        self.save_job_button.grid(row=10,column=1,sticky='nsew', padx=2, pady=4)

        self.run_button = tk.Button(self.sub_job_frame, text="Run Job",activebackground="#78d6ff", command= submit_job)
        self.run_button['font'] = myfont()
        self.run_button.grid(row=11,column=0,sticky='nsew', padx=2, pady=4)    

    def _sub_command_option(self, *_):
        if self.sub_job_type.get() == 0:
            self.sub_command.set('bash')
        else:
            self.sub_command.set('')

    def get_processors(self):
        return self.processors.get()

    def set_run_button_state(self, state):
        self.run_button.config(state=state)

    def get_password_option(self):
        if self.password_option.get() == 1:
            return True
        return False

    def get_network_dict(self):

        network_job_dict = {
          'ip':self.ip.get(),
          'username':self.username.get(),
          'password':self.password.get(),
          'pkey_file':self.pkey_file.get(),
          'port' : self.port.get(),
          'remote_path':self.rpath.get(),
          'passwordless_ssh':self.get_password_option()
            } 
        return network_job_dict

####### popup filemenu #########

class CreateProjectPage(tk.Toplevel):

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
        self.label_proj = tk.Label(self,text="Project Name",bg=label_design['bg'],fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(column=0, row= 3, sticky=tk.W,  pady=10, padx=10)  

        self.entry_proj = tk.Entry(self,textvariable=self._var['proj_name'])
        self.entry_proj['font'] = myfont()
        self.entry_proj.grid(column=1, row= 3, sticky=tk.W)
        self.entry_proj.delete(0, tk.END)

        self.button_project = tk.Button(self,text="Create New Project",width=18, activebackground="#78d6ff")
        self.button_project['font'] = myfont()
        self.button_project.grid(column=2, row= 3, sticky=tk.W, padx= 10, pady=10)  
            
    def get_value(self, key):
        return self._var[key].get()

class CreateWorkflowPage(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._default_var = {
              'workflow_name' : ['str'],
              
          }

        self._var = var_define(self._default_var)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self.title("Create New Workflow")     
        self.geometry("550x200")
        self.label_proj = tk.Label(self,text="Workflow Name",bg=label_design['bg'],fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(column=0, row= 3, sticky=tk.W,  pady=10, padx=10)  

        self.entry_proj = tk.Entry(self,textvariable=self._var['workflow_name'])
        self.entry_proj['font'] = myfont()
        self.entry_proj.grid(column=1, row= 3, sticky=tk.W)
        self.entry_proj.delete(0, tk.END)

        self.create_button = tk.Button(self,text="Create",width=18, activebackground="#78d6ff")
        self.create_button['font'] = myfont()
        self.create_button.grid(column=2, row= 3, sticky=tk.W, padx= 10, pady=10)  
            
    def get_value(self, key):
        return self._var[key].get()
    
class GroundStatePage(View):
    
    def __init__(self, parent, engine, task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from litesoph.gui.view_gs import InputFrame
        from litesoph.gui.models.inputs import gs_input, gs_visible_default

        self.parent = parent
        self.task_name = task_name
        self.engine = tk.StringVar(value=engine)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.inp = InputFrame(self.input_param_frame,fields=gs_input,visible_state=gs_visible_default, padx=5, pady=5)
        self.inp.grid(row=0, column=0)
        self.trace_variables()
        
        add_job_frame(self, self.submit_button_frame, task_name, column=1)
        self.button_back = tk.Button(self.save_button_frame, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.button_back['font'] = myFont
        self.button_back.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        # self.button_clear = tk.Button(self.save_button_frame, text="Clear", activebackground="#78d6ff", command=lambda: self.clear_button())
        # self.button_clear['font'] = myFont
        # self.button_clear.grid(row=0, column=2, padx=3, pady=3,sticky='nsew')

        self.button_view = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.button_view['font'] = myFont
        self.button_view.grid(row=0, column=3,padx=3, pady=3,sticky='nsew')
        # self.button_view.grid(row=0, column=2,padx=3, pady=3,sticky='nsew')
        
        self.button_save = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.button_save['font'] = myFont
        self.button_save.grid(row=0, column=5, padx=3, pady=3,sticky='nsew')
        # self.button_save.grid(row=0, column=4, padx=3, pady=3,sticky='nsew')

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=4, sticky='nsew')
        # self.label_msg.grid(row=0, column=3, sticky='nsew')

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)
        
    def back_button(self):
        return
        self.event_generate(actions.SHOW_WORK_MANAGER_PAGE)
    
    def clear_button(self):
        self.event_generate(f'<<Clear{self.task_name}Script>>')
    
    def generate_input_button(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def save_button(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')  

    #---------------------------------View Specific trace functions----------------------------------------------------------------    

    def trace_select_box(self, *_):
        import copy
        from litesoph.gui.models.inputs import box_dict
        box_copy = copy.deepcopy(box_dict)
        if self.inp.variable["select_box"].get():
            self.inp.frame_template(parent_frame=self.inp.group["simulation box"],row=10, column=0, padx=2, pady=2,fields=box_copy) 
            self.inp.update_widgets()            
        else:
            self.inp.update_widgets()
            if hasattr (self.inp.group["simulation box"],'group'):
                self.inp.group["simulation box"].group.grid_remove()
            
    def grid_sim_box_frame(self,*_):
        for name in ["basis_type"]:
            if self.inp.fields[name]["visible"]:
                basis = self.inp.variable[name].get()
                if basis == "gaussian":
                    self.inp.group["simulation box"].grid_remove()  
                else:
                    self.inp.group["simulation box"].grid()          
                self.inp.update_widgets()

    def trace_xc(self,*_):
        self.inp.update_widgets()
        self.grid_sim_box_frame()
        
    def trace_variables(self, *_):
        for name, var in self.inp.variable.items():
            if name == "xc":
                self.inp.update_widgets()
                var.trace_add('write', self.trace_xc)
            elif name ==  "select_box":
                var.trace_add('write', self.trace_select_box)
            elif name in ["basis_type"]:
                    var.trace_add('write', self.grid_sim_box_frame)            
            else:
                var.trace("w", self.inp.update_widgets)

    def get_parameters(self):
        gui_dict = self.inp.get_values()
        
        key = "basis_type"
        type = gui_dict.get(key)
        if type :
            assert type in ["lcao","fd","pw","gaussian"]
            basis_type = type

            lcao = (basis_type == "lcao")
            gaussian = (basis_type == "gaussian")

            if lcao:
                basis = gui_dict.get("basis:lcao")
            elif gaussian:
                basis = gui_dict.get("basis:gaussian") 
            else:
                basis = None
        
        select_box = gui_dict.get("select_box")
        boxshape = gui_dict.get("boxshape")

        if boxshape is not None and select_box is True:
            if boxshape == "parallelepiped":
                dim_dict = {
                    "box_length_x":gui_dict.get("box_length_x"),
                    "box_length_y":gui_dict.get("box_length_y"),
                    "box_length_z":gui_dict.get("box_length_z")
                    }
            elif boxshape == "cylinder":
                dim_dict = {
                    "radius":gui_dict.get("radius"),
                    "cylinder_length":gui_dict.get("cylinder_length"),
                    }
            elif boxshape in ["sphere", "minimum"]:
                dim_dict = {
                    "radius":gui_dict.get("radius"),
                    }  
            else:
                dim_dict = None            
        else:
            dim_dict = None
        
        gs_input = {
            "xc":gui_dict.get('xc'),  
            "basis_type": basis_type,                                   
            "basis": basis,               
            "spin": gui_dict.get('spin'),
            "spacing": gui_dict.get('spacing'),
            "boxshape": boxshape,    
            "box_dim" : dim_dict, 
            "vacuum": gui_dict.get('vacuum'),
            "max_iter":gui_dict.get('max_itr'),
            "energy_conv": gui_dict.get('energy_conv'),
            "density_conv": gui_dict.get('density_conv'),
            "smearing": gui_dict.get('smearing'),
            "mixing": gui_dict.get('mixing'),
            "bands": gui_dict.get('bands'),
        }        
        return gs_input

    def set_parameters(self,default_param_dict:dict):
        from litesoph.gui.defaults_handler import update_gs_defaults
        default_gui_dict = update_gs_defaults(default_param_dict)
        self.inp.init_widgets(fields=self.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)
           
class TimeDependentPage(View):           
    def __init__(self, parent, engine, task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from litesoph.gui.view_gs import InputFrame
        from litesoph.gui.models.inputs import td_delta_input

        self.parent = parent
        self.task_name = task_name
        self.engine = tk.StringVar(value=engine)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.inp = InputFrame(self.input_param_frame,fields=td_delta_input, padx=5, pady=5)
        self.inp.grid(row=0, column=0)
        self.trace_variables()

        add_job_frame(self, self.submit_button_frame, task_name, column=1)

        self.button_back = tk.Button(self.save_button_frame, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.button_back['font'] = myFont
        self.button_back.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        self.button_view = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.button_view['font'] = myFont
        self.button_view.grid(row=0, column=2,padx=3, pady=3,sticky='nsew')
        
        self.button_save = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.button_save['font'] = myFont
        self.button_save.grid(row=0, column=4, padx=3, pady=3,sticky='nsew')

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=3, sticky='nsew')

    def trace_variables(self,*_):
        for name, var in self.inp.variable.items():
            var.trace("w", self.inp.update_widgets)

    def set_label_msg(self,msg):
        show_message(self.label_msg, msg)

    def get_pol_list(self, pol_var:str):
        assert pol_var in ["X", "Y", "Z"] 
        if pol_var == "X":
            pol_list = [1,0,0]         
        elif pol_var == "Y":
            pol_list = [0,1,0] 
        elif pol_var == "Z":
            pol_list = [0,0,1]                
        return pol_list

    def get_property_list(self, gui_values:dict):
        prop_list = ['spectrum']
               
        if gui_values.get("ksd") is True:
            prop_list.append("ksd")
        if gui_values.get("mo_population") is True:
            prop_list.append("mo_population")    
        return prop_list   

    def get_parameters(self):
        gui_dict = self.inp.get_values()
        self.pol_list = self.get_pol_list(gui_dict.get("pol_dir"))

        td_input = {
            'strength': gui_dict.get("laser_strength"),
            'polarization' : self.pol_list,
            'time_step' : gui_dict.get("time_step"),
            'number_of_steps' : gui_dict.get("number_of_steps"),
            'output_freq': gui_dict.get("output_freq"),
            'properties' : self.get_property_list(gui_dict)
        }
        return td_input
    
    def set_parameters(self, default_param_dict:dict):
        from litesoph.gui.defaults_handler import update_td_delta_defaults
        default_gui_dict = update_td_delta_defaults(default_param_dict)
        self.inp.init_widgets(fields=self.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)
    
    def generate_input_button(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def save_button(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')    

class TDPage(View):

    def __init__(self, parent, task_name, *args, **kwargs):
        super().__init__(parent, *args)
        from litesoph.gui.view_gs import InputFrame        

        self.parent = parent
        self.task_name = task_name
        self.laser_defined = False
        self.delay_value = tk.DoubleVar()
        self.delay_options = []

        self.input_widget_dict = kwargs.get('input_widget_dict', None)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.add_widgets(self.input_widget_dict)
        add_job_frame(self, self.submit_button_frame, task_name, column=1)

        self.button_back = tk.Button(self.save_button_frame, text="Back to main page", activebackground="#78d6ff", command=lambda: self.back_button())
        self.button_back['font'] = myFont
        self.button_back.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        self.button_view = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.button_view['font'] = myFont
        self.button_view.grid(row=0, column=2,padx=3, pady=3,sticky='nsew')
        self.button_view.config(state='disabled')
        
        self.button_save = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.button_save['font'] = myFont
        self.button_save.grid(row=0, column=4, padx=3, pady=3,sticky='nsew')
        self.button_save.config(state='disabled')

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=3, sticky='nsew')

        self.trace_variables()

    def add_widgets(self, input_widget_dict:dict):
        """ Adds widgets to TD Page"""
        from litesoph.gui.view_gs import InputFrame
        for widget in self.input_param_frame.winfo_children():
            widget.destroy()
        
        if input_widget_dict is None:
            input_widget_dict = inp.laser_td_input

        copy_input_widget_dict = copy.deepcopy(input_widget_dict)
        self.inp = InputFrame(self.input_param_frame,fields=copy_input_widget_dict, padx=5, pady=5)        
        self.inp.grid(row=0, column=0) 

        self.label_delay_entry = tk.Label(self.inp.tab["External Fields"], text="Delay Entries should be separated by ' ' or ','")
        self.label_delay_entry.grid(column=1,padx=3)

        self.button_laser_design = tk.Button(self.inp.tab["External Fields"], text="Design/Edit Laser", activebackground="#78d6ff", command=self.laser_button)
        self.button_laser_design['font'] = self.myFont
        self.button_laser_design.grid(column=1,padx=3)

        self.button_show_lasers = tk.Button(self.inp.tab["External Fields"], text="Laser Details", activebackground="#78d6ff", command=self.show_laser_summary)
        self.button_show_lasers['font'] = self.myFont
        self.button_show_lasers.grid(column=1,padx=3)  
    
    def back_button(self):
        self.event_generate('<<BackonTDPage>>')

    def generate_input_button(self):
        self.event_generate(f'<<Generate{self.task_name}Script>>')

    def save_button(self):
        self.event_generate(f'<<Save{self.task_name}Script>>')

    def show_laser_summary(self):
        self.event_generate('<<ViewLaserSummary>>')

    def trace_variables(self,*_):
        for name, var in self.inp.variable.items():
            if name == "field_type":
                var.trace("w", self.trace_field)

            if name == "exp_type":
                var.trace("w", self.trace_exp)
            var.trace("w", self.inp.update_widgets)

    def trace_field(self, *_):
        if self.inp.variable["field_type"].get() == "None":
            self.laser_defined = True
            self.button_view.config(state='active')
            self.button_save.config(state='active')
            self.button_laser_design.config(state='disabled')
            self.inp.update_widgets()
        else:
            self.laser_defined = False
            self.button_view.config(state='disabled')
            self.button_save.config(state='disabled')
            self.button_laser_design.config(state='active')
            self.inp.update_widgets()

    def trace_exp(self, *_):
        if self.inp.variable["exp_type"].get() == "State Preparation":
            if self.label_delay_entry:
                self.label_delay_entry.grid_remove()
        if self.inp.variable["exp_type"].get() == "Pump-Probe":
            if self.label_delay_entry:
                self.label_delay_entry.grid()

        self.inp.update_widgets()

    def laser_button(self):
        self.event_generate('<<Design&EditLaser>>')

    def set_label_msg(self,msg):
        self.label_msg.grid()
        show_message(self.label_msg, msg)
    
    def get_property_list(self, gui_values:dict):
        prop_list = ['spectrum']
        if gui_values.get("ksd") is True:
            prop_list.append("ksd")
        if gui_values.get("mo_population") is True:
            prop_list.append("mo_population")    
        return prop_list  

    def get_delay_list(self, delay_str:str):
        delay_values = str(delay_str)
        delay_list = []
        try:
            delays = delay_values.split()
        except:
            delays = delay_values.split(sep=',') 

        for delay in delays:
            delay_list.append(float(delay))
        return delay_list

    def check_expt_type(self):
        gui_dict = self.inp.get_values()
        if gui_dict.get("exp_type" ) == "Pump-Probe":
            return True
        else:
            return False
    
    def set_laser_design_dict(self, laser_calc_list:list):  
        """ laser_calc_list: list of laser calc param"""
        import copy

        self.laser_calc_list = copy.deepcopy(laser_calc_list)
        return self.laser_calc_list
    
    def get_td_gui_inp(self):
        gui_dict = copy.deepcopy(self.inp.get_values())

        # TODO: Check
        # Updating delay_list key-value as a list of delays
        if gui_dict.get('delay_list') is not None:
            gui_dict.update({'delay_list': self.get_delay_list(gui_dict.get('delay_list'))})
        return gui_dict

    def get_parameters(self):
        gui_dict = copy.deepcopy(self.inp.get_values())

        td_input = {
            'time_step' : gui_dict.get("time_step"),
            'number_of_steps' : gui_dict.get("number_of_steps"),
            'output_freq': gui_dict.get("output_freq"),
            'properties' : self.get_property_list(gui_dict),
        }       

        # TODO: Add delay and list of lasers
       
        # if gui_dict.get("masking"):
        #     td_input.update({"masking": self.get_mask(gui_dict)})
        return td_input

    def set_parameters(self, default_param_dict:dict):
        """To update parameters of laser-td page"""
        from litesoph.gui.defaults_handler import update_td_laser_defaults
        default_gui_dict = update_td_laser_defaults(default_param_dict)
        self.inp.init_widgets(fields=self.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)

class LaserDesignPage(View):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args)
        from litesoph.gui.view_gs import InputFrame        

        self.parent = parent

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        copy_laser_design_input = copy.deepcopy(inp.laser_design_input)        
        self.inp = InputFrame(self.input_param_frame,fields=copy_laser_design_input, padx=5, pady=5)       
        self.inp.grid(row=0, column=0)

        set_state(self.inp.group["Masking Inputs"],'disabled')

        self.tree = self.create_laser_tree_view(parent=self.input_param_frame)      
        self.tree.bind('<<TreeviewSelect>>', self.OnSingleClick)

        self.button_back = tk.Button(self.property_frame, text="Back", activebackground="#78d6ff", command=lambda: self.back_button())
        self.button_back['font'] = myFont
        self.button_back.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        self.button_plot = tk.Button(self.property_frame, text="Plot", activebackground="#78d6ff", command=lambda: self.plot_button())
        self.button_plot['font'] = myFont
        self.button_plot.grid(row=0, column=5, padx=3, pady=3,sticky='nsew')

        self.button_next = tk.Button(self.property_frame, text="Finalise", activebackground="#78d6ff", command=lambda: self.next_button())
        self.button_next['font'] = myFont
        self.button_next.grid(row=0, column=7, padx=3, pady=3,sticky='nsew')

        self.button_reset = tk.Button(self.property_frame, text="Reset", activebackground="#78d6ff", command=lambda: self.reset_button())
        self.button_reset['font'] = myFont
        self.button_reset.grid(row=0, column=8, padx=3, pady=3,sticky='nsew')

        self.trace_variables()

    def trace_variables(self,*_):
        for name, var in self.inp.variable.items():
            if name in ["masking"]:
                var.trace("w", self.trace_masking_option)             
            else:
                var.trace("w", self.inp.update_widgets)

    def trace_masking_option(self, *_):
        if self.inp.variable["masking"].get():
            set_state(self.inp.group["Masking Inputs"],'normal' )
        else:
            set_state(self.inp.group["Masking Inputs"],'disabled')

    def create_laser_tree_view(self, parent):
        self.count = 0
        columns = ('lasers')
        tree = ttk.Treeview(parent, 
        # columns=columns, 
        # show='headings'
        )

        # define headings
        tree.heading('#0', text='Lasers Added')
        tree.grid(row=0, column=1,columnspan=3, sticky=tk.NSEW)

        self.button_add = tk.Button(parent, text="Add", activebackground="#78d6ff", command=lambda: self.add_button())
        self.button_add['font'] = self.myFont
        self.button_add.grid(row=1, column=1, padx=3, pady=3,sticky='nsew')

        self.button_edit = tk.Button(parent, text="Save", activebackground="#78d6ff", command=lambda: self.edit_laser())
        self.button_edit['font'] = self.myFont
        self.button_edit.grid(row=1, column=2, padx=3, pady=3,sticky='nsew')

        self.button_del = tk.Button(parent, text="Remove", activebackground="#78d6ff", command=lambda: self.remove_button())
        self.button_del['font'] = self.myFont
        self.button_del.grid(row=1, column=3, padx=3, pady=3,sticky='nsew')

        # add a scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=4, sticky='ns')
        return tree

    def OnSingleClick(self, *_):
        self.event_generate('<<SelectLaser&UpdateView>>')       

    def laser_selected(self, *_):
        pass
    
    def reset_button(self):
        self.inp.init_widgets(ignore_state=True)

    def back_button(self):
        self.event_generate('<<BackOnLaserDesignPage>>')

    def add_button(self):
        self.event_generate('<<AddLaser>>')

    def edit_laser(self):
        self.event_generate('<<EditLaser>>')

    def save_button(self):
        self.event_generate('<<SaveLaser>>')

    def remove_button(self):
        self.event_generate('<<RemoveLaser>>')

    def next_button(self):
        self.event_generate('<<NextonLaserDesignPage>>')

    def plot_button(self):
        self.event_generate('<<PlotLaser>>')
    
    def select_button(self):
        self.event_generate('<<SelectLaser>>')
 
    def get_laser_parameters(self, input_dict:dict):
        """Gets the laser parameters from widgets in LaserDesign tab"""
        from litesoph.utilities.units import as_to_au 

        laser_type = input_dict.get('laser_type')
        tag_var =  input_dict.get("pump-probe_tag")
        pol_var = input_dict.get("pol_dir")
        if laser_type == "Gaussian Pulse":
            l_type = "gaussian"
        elif laser_type == "Delta Pulse":
            l_type = "delta"
        
        laser_input = {
            "type": l_type,
            "inval" :  input_dict.get("log_val"),
            "strength": input_dict.get("laser_strength"),  
            "fwhm" :input_dict.get("fwhm"),
            "frequency" :  input_dict.get("freq"),
            'polarization': pol_var
        }

        if tag_var is not None:
            laser_input["tag"] = tag_var
            if tag_var == "Probe":
                laser_input.update({
                    "tin" : input_dict.get("time_origin:probe")*as_to_au,
                })
            else:
                laser_input.update({
                    "tin" : input_dict.get("time_origin")*as_to_au,
                }) 
        else:
           laser_input.update({
                    "tin" : input_dict.get("time_origin")*as_to_au,
                }) 
        return laser_input

    def get_masking_parameters(self, input_dict:dict):
        """Gets the masking parameters from widgets in Masking tab"""
        
        axis_name_var_map = {
            "X": 0,
            "Y": 1,
            "Z": 2}

        if input_dict.get('masking', False) is False:
            mask_input = None
        else:
            mask_input = {
            "Type": input_dict.get("mask_type"),            
            "Boundary": input_dict.get("boundary_type")
            }
            
            if input_dict.get("mask_type") == 'Plane':
                axis_name = input_dict.get("mask_plane:axis")
                mask_input.update({"Axis": axis_name_var_map.get(axis_name),
                                    "X0"  : input_dict.get("mask_plane:origin")})
            else:
                mask_input.update({"Radius" : input_dict.get("mask_sphere:radius"),
                                "Centre":[input_dict.get("mask_sphere:origin_x"),
                                        input_dict.get("mask_sphere:origin_y"),
                                        input_dict.get("mask_sphere:origin_z")]})
            if input_dict.get("boundary_type") == 'Smooth':
                mask_input.update({"Rsig" : input_dict.get("r_sig")})
        return mask_input


    def get_parameters(self):            
        """Gets combined parameters for both laser design and masking"""

        gui_dict = copy.deepcopy(self.inp.get_values())
        # Collecting the laser and masking params
        laser_dict = self.get_laser_parameters(input_dict=gui_dict)
        if gui_dict.get('masking') is True:
            masking_dict = self.get_masking_parameters(input_dict=gui_dict)
            laser_dict.update({'mask': masking_dict})       
        else:
            laser_dict.update({'mask': None})   
        return laser_dict    

    def set_parameters(self, default_param_dict:dict):
        """To update parameters of laser-design page"""
        
        from litesoph.gui.defaults_handler import update_laser_defaults
        default_gui_dict = update_laser_defaults(default_param_dict)
        self.inp.init_widgets(fields=self.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)

class LaserPlotPage(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._default_var = {
              'delay' : ['float'],
              'pol' : ['str']
              
          }
        self.delay_list = [0]
        self.laser_list = ['laser 1']
        self.laser_systems = []

        self._var = var_define(self._default_var)
        self.attributes("-topmost", True)
        self.grab_set()
        self.lift()
        self.title("Laser Plot Page")     
        self.geometry("550x400")

        self.tree_frame = tk.Frame(self)
        self.tree_frame.grid(row=0, column=0)

        self.widget_frame = tk.Frame(self)
        self.widget_frame.grid(row=1, column=0)

        # Create a treeview to list existing laser systems
        self.tree = self.create_laser_tree_view(parent= self.tree_frame)

        # self.cb_pol = ttk.Combobox(self,textvariable=self._var['pol'], values = ['X', 'Y', 'Z'])
        # self.cb_pol['font'] = myfont()
        # self.cb_pol.grid(row=1, column=1, sticky=tk.W)         

        self.label_delay = tk.Label(self.widget_frame,text="Delay to consider (in fs):",bg=label_design['bg'],fg=label_design['fg'])
        self.label_delay['font'] = label_design['font']
        self.label_delay.grid(row=1, column=0,sticky=tk.W,  pady=10, padx=10) 

        self.entry_delay = ttk.Entry(self.widget_frame,textvariable=self._var['delay'])
        self.entry_delay['font'] = myfont()
        self.entry_delay.grid(row=1, column=1, sticky=tk.W)

        self.button_plot = tk.Button(self.widget_frame,text="Plot",width=18, activebackground="#78d6ff", command=lambda: self.plot_button())
        self.button_plot['font'] = myfont()
        self.button_plot.grid(row=1, column=3, sticky=tk.W, padx= 10, pady=10) 

        # self.button_plot_w_delay = tk.Button(self.widget_frame,text="Plot with delay",width=18, activebackground="#78d6ff", command=lambda: self.plot_w_delay())
        # self.button_plot_w_delay['font'] = myfont()
        # self.button_plot_w_delay.grid(row=1, column=2, sticky=tk.W, padx= 10, pady=10) 
            
    def create_laser_tree_view(self, parent):
        tree = ttk.Treeview(parent)

        # define headings
        tree.heading('#0', text='Lasers Added')
        # tree.bind('<<TreeviewSelect>>', self.laser_selected)
        tree.grid(row=0, column=1,columnspan=2, sticky=tk.NSEW)

        # add a scrollbar
        # scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        # tree.configure(yscroll=scrollbar.set)
        # scrollbar.grid(row=0, column=2, sticky='ns')
        return tree
    
    def plot_button(self):
        self.event_generate('<<PlotLasers>>')

    # def plot_w_delay(self):
    #     self.event_generate('<<PlotwithDelay>>')

    def laser_selected(self, *_):
        items = self.tree.selection()
        _list_of_lasers = []
        for item in items:
            laser = str(self.tree.item(item,"text"))
            _list_of_lasers.append(laser)
        return _list_of_lasers
                
    def get_value(self, key):
        return self._var[key].get()

class TreeView(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args) 
        self.frame1= ttk.Frame(self, borderwidth=2, relief='groove')
        self.frame2= ttk.Frame(self, borderwidth=2, relief='groove')

        self.frame1.pack(fill=tk.BOTH, anchor='n', expand=True)
        self.frame2.pack(fill=tk.BOTH, anchor='n', expand=True)
               
        self.tree = create_tree_and_scroll(parent= self.frame1)

        self.button_add = tk.Button(self.frame2, text="Add", activebackground="#78d6ff", command=lambda: self.add_button())
        self.button_add['font'] = self.myFont
        self.button_add.grid(row=1, column=1, padx=3, pady=3,sticky='nsew')

        self.button_del = tk.Button(self.frame2, text="Remove", activebackground="#78d6ff", command=lambda: self.remove_button())
        self.button_del['font'] = self.myFont
        self.button_del.grid(row=1, column=2, padx=3, pady=3,sticky='nsew')

    def add_button(self):
        # adds data and updates tree
        pass

    def remove_button(self):
        # removes data and updates tree
        pass

def create_tree_and_scroll(parent):
    tree = ttk.Treeview(parent)
    tree.grid(row=0, column=1,columnspan=3, sticky=tk.NSEW)

    # add a scrollbar
    scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=4, sticky='ns')
    return tree

def add_columns(tree:ttk.Treeview, tree_data:list, column_map:dict= {}):

    # Get the columns
    data_sample = tree_data[0]
    assert isinstance(data_sample, dict) 
    columns = tuple(data_sample.keys())   
    tree['columns'] = columns

    # Defining columns
    tree.column("#0", width=0, stretch=0)
    for c in columns:
        tree.column(column=c, anchor=tk.W, width=140)

    # Adding headings
    tree.heading("#0", text="", anchor=tk.W)
    for c in columns:
        column_name = column_map.get(c, c)
        tree.heading(column= c, text=column_name, anchor=tk.W)

def update_tree_data(tree:ttk.Treeview, tree_data:list):
    """ Updates tree from tree_data"""

    # Adding data
    for i, set in enumerate(tree_data):        
        assert isinstance(set, dict)      
        _entries = tuple(set.values()) 
        tree.insert(parent='', index='end', iid=i, values=_entries) 

def get_pol_list(pol_var:str):
    assert pol_var in ["X", "Y", "Z"] 
    if pol_var == "X":
        pol_list = [1,0,0]         
    elif pol_var == "Y":
        pol_list = [0,1,0] 
    elif pol_var == "Z":
        pol_list = [0,0,1]                
    return pol_list

def get_pol_var(pol_list:list):
    if pol_list == [1,0,0]:
        pol_var = "X"          
    elif pol_list == [0,1,0]:
        pol_var = "Y" 
    elif pol_list == [0,0,1]    :
        pol_var = "Z"                
    return pol_var

class PlotSpectraPage(View):

    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.engine = engine
        self.task_name = task_name
        
        self._default_var = {
            'del_e' : ['float', 0.05],
            'e_max' : ['float', 30.0],
            'e_min' : ['float']
        }

        self._var = var_define(self._default_var)

        self.axis = tk.StringVar()

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.Frame1 = self.input_param_frame #ttk.Frame(self, borderwidth=2, relief='groove')
        # self.grid_columnconfigure(9, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=5)

        #self.Frame1.grid(row=0,column=0, sticky='nsew')

        self.add_job_frame(self.submit_button_frame, self.task_name)        

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


        #self.button_frame = ttk.Frame(self, borderwidth=2, relief='groove')
        #self.button_frame.grid(row=1, column=0, sticky='nsew')

        self.back_button = tk.Button(self.save_button_frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0, padx=3, pady=6)

    def add_job_frame(self, parent, task_name, r:int=0, c:int=0):  
        """  Adds submit job buttons to View1"""

        self.Frame3 = ttk.Frame(parent, borderwidth=2, relief='groove')
        self.Frame3.grid(row=r, column=c, sticky='nswe')

        self.submit_button = tk.Button(self.Frame3, text="Submit Local", activebackground="#78d6ff")
        self.submit_button['font'] = myfont()
        self.submit_button.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
        
        self.Frame1_Button3 = tk.Button(self.Frame3, text="Submit Network", activebackground="#78d6ff")
        self.Frame1_Button3['font'] = myfont()
        self.Frame1_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')
        self.Frame1_Button3.config(state='disabled')
        
        self.plot_button = tk.Button(self.Frame3, text="Plot", activebackground="#78d6ff")
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=3, column=2,padx=3, pady=15, sticky='nsew')

    def show_plot(self):
        self.event_generate(f"<<Show{self.task_name}Plot>>")

    def get_parameters(self):
        
        plot_dict = {
            'delta_e':self._var['del_e'].get(),
            'e_max':self._var['e_max'].get(),
            'e_min': self._var['e_min'].get()       
        }
        return plot_dict            

class TcmPage(View):

    def __init__(self, parent, engine, task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
        self.parent = parent
        self.job = None
        self.task_name = task_name
        self.engine = engine

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

        self.heading = tk.Label(self.input_param_frame,text="LITESOPH Kohn Sham Decomposition", fg='blue')
        self.heading['font'] = myfont()
        self.heading.grid(row=0, column=0)

        self.frame_inp = ttk.Frame(self.input_param_frame, borderwidth=2, relief='groove')
        self.frame_inp.grid(row=1,column=0, sticky='nsew')

        self.grid_rowconfigure(1, weight=5)
        self.grid_rowconfigure(2, weight=1)

        # self.frame_button = ttk.Frame(self, borderwidth=2, relief='groove')
        # self.frame_button.grid(row=2, column=0, sticky='nsew')

        # self.frame_inp = ttk.Frame(self.Frame1, borderwidth=2)
        # self.frame_inp.grid(row=1,column=0, sticky='nsew')           

        self.back_button = tk.Button(self.save_button_frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0)

        #self.engine_name.trace_add(['write'], lambda *_:self.select_ksd_frame(self.frame_inp))
        self.select_ksd_frame(self.frame_inp)
        self.add_job_frame(self.submit_button_frame, self.task_name)

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
        # engine = self.engine_name.get()
        #TODO: The engine information should be abstracted from this module.
        for widget in parent.winfo_children():
            widget.destroy()
        if self.engine == 'gpaw':
            self.add_gpaw_ksd_frame(parent)
        elif self.engine == 'octopus':
            self.add_oct_ksd_frame(parent)    


    def add_job_frame(self,parent, task_name):  
        """  Adds submit job buttons"""

        # self.Frame3 = ttk.Frame(self, borderwidth=2, relief='groove')
        # self.Frame3.grid(row=1, column=1, sticky='nswe')
        
        self.submit_button = tk.Button(parent, text="Submit Local", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubLocal'+task_name+'>>'))
        self.submit_button['font'] =myfont()
        self.submit_button.grid(row=1, column=2,padx=3, pady=6, sticky='nsew')
        
        self.Frame1_Button3 = tk.Button(parent, text="Submit Network", activebackground="#78d6ff", command=lambda: self.event_generate('<<SubNetwork'+task_name+'>>'))
        self.Frame1_Button3['font'] = myfont()
        self.Frame1_Button3.grid(row=2, column=2, padx=3, pady=6, sticky='nsew')    

        self.plot_button = tk.Button(parent, text="Plot", activebackground="#78d6ff", command=lambda: self.event_generate(f"<<Show{task_name}Plot>>"))
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=3, column=2,padx=3, pady=15, sticky='nsew')

    def retrieve_input(self):
        inputValues = self.frequency.get()  #TextBox_freqs.get("1.0", "end-1c")
        freqs = inputValues.split(',')

        self.freq_list = []
        for freq in freqs[0:]:
            freq = freq.strip()
            self.freq_list.append(float(freq))
        return(self.freq_list)   
    
    def get_parameters(self):
        engine = self.engine_name.get()    
       #TODO: The engine information should be abstracted from this module.
        if self.engine == 'gpaw':
            
            self.retrieve_input()

            gpaw_ksd_dict = {
                'frequency_list' : self.freq_list,
                'axis_limit': self.axis_limit.get()
                 } 
            return gpaw_ksd_dict

        elif self.engine == 'octopus':
            oct_ksd_dict = {
            'task': 'tcm',
            'num_occupied_mo': self.ni.get(),
            'num_unoccupied_mo': self.na.get()
        } 
            return oct_ksd_dict                

    def get_plot_parameters(self):
        oct_ksd_plot_dict ={
        'fmin': self.wmin.get(),
        'fmax': self.wmax.get(),
        'axis_limit': self.axis_limit.get()}
        return oct_ksd_plot_dict

class PopulationPage(View):
    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.engine = engine
        self.task_name = task_name
        
        self.bandpass = tk.IntVar(value=100)
        self.hanning = tk.IntVar(value= 50)
        self.occupied_mo = tk.IntVar(value=1)
        self.unoccupied_mo = tk.IntVar(value=1)
        self.plot_option = tk.IntVar(value=1)
        self.occupied_mo_plot = tk.IntVar(value=1)
        self.unoccupied_mo_plot = tk.IntVar(value=1)
        self.ngrid = tk.IntVar(value=100)
        self.broadening = tk.DoubleVar(value= 0.5)

        self.SubFrame1 = self.input_param_frame 

        self.SubFrame2 = self.property_frame 

        self.SubFrame3 = self.submit_button_frame 

        self.Frame_button1 = self.save_button_frame 

        self.Frame1_label_path = tk.Label(self.SubFrame1,text="LITESOPH Input for Population Tracking", fg='blue')
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

        # self.label_bandpass = tk.Label(self.SubFrame1,text="Bandpass",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        # self.label_bandpass['font'] = myfont()
        # self.label_bandpass.grid(row=3, column=0, sticky='w', padx=5, pady=5)

        # self.entry_bandpass = Onlydigits(self.SubFrame1, textvariable= self.bandpass, width=5)
        # self.entry_bandpass['font'] = myfont()
        # self.entry_bandpass.grid(row=3, column=1)
        
        # self.label_hanning = tk.Label(self.SubFrame1,text="Hanning",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        # self.label_hanning['font'] = myfont()
        # self.label_hanning.grid(row=4, column=0, sticky='w', padx=5, pady=5)

        # self.entry_hanning = Onlydigits(self.SubFrame1, textvariable= self.hanning, width=5)
        # self.entry_hanning['font'] = myfont()
        # self.entry_hanning.grid(row=4, column=1)

        self.label_plot = tk.Label(self.SubFrame2,text="Plotting Parameters", fg='blue')
        self.label_plot['font'] = myfont()
        self.label_plot.grid(row=0, column=0, padx=5, pady=10)

        # self.Label_grid = tk.Label(self.SubFrame2,text="Number of mesh grids",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        # self.Label_grid['font'] = myfont()
        # self.Label_grid.grid(row=1, column=0, sticky='w', padx=5, pady=5)        
        
        # self.entry_grid = Onlydigits(self.SubFrame2, textvariable= self.ngrid, width=5)
        # self.entry_grid['font'] = myfont()
        # self.entry_grid.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # self.Label_width = tk.Label(self.SubFrame2,text="Broadening width",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        # self.Label_width['font'] = myfont()
        # self.Label_width.grid(row=2, column=0, sticky='w', padx=5, pady=5)        
        
        # self.entry_width = Onlydigits(self.SubFrame2, textvariable= self.broadening, width=5)
        # self.entry_width['font'] = myfont()
        # self.entry_width.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        values = {"All States": 0, "Select the states": 1}
        for (text, value) in values.items():
            tk.Radiobutton(self.SubFrame2, text=text, variable=self.plot_option, font=myfont2(),
             justify='left',value=value).grid(row=value+1, column=0, ipady=5, sticky='w')   

        self.Label_ni_to_plot = tk.Label(self.SubFrame2,text="Number of occupied states(HOMO & below)",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_ni_to_plot['font'] = myfont()
        self.Label_ni_to_plot.grid(row=3, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_ni_to_plot = Onlydigits(self.SubFrame2, textvariable= self.occupied_mo_plot, width=5)
        self.entry_ni_to_plot['font'] = myfont()
        self.entry_ni_to_plot.grid(row=3, column=1)

        self.Label_na_to_plot = tk.Label(self.SubFrame2,text="Number of unoccupied states(LUMO & above)",bg= label_design['bg'],fg=label_design['fg'], justify='left')
        self.Label_na_to_plot['font'] = myfont()
        self.Label_na_to_plot.grid(row=4, column=0, sticky='w', padx=5, pady=5)        
        
        self.entry_na_to_plot = Onlydigits(self.SubFrame2, textvariable= self.unoccupied_mo_plot, width=5)
        self.entry_na_to_plot['font'] = myfont()
        self.entry_na_to_plot.grid(row=4, column=1)

        self.submit_button = tk.Button(self.SubFrame1, text="Submit",activebackground="#78d6ff", command=self._on_submit)
        self.submit_button['font'] = myfont()
        self.submit_button.grid(row=4, column=2, sticky='we', padx=5)

        self.plot_button = tk.Button(self.SubFrame2, text="Plot",activebackground="#78d6ff", command=self._on_plot)
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=4, column=2, sticky='we', padx=25)

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
            'num_unoccupied_mo': self.unoccupied_mo.get(),
            # 'bandpass_window': self.bandpass.get(),
            # 'hanning_window' : self.hanning.get()
        }

        return pop_dict

    def get_plot_parameters(self):
       
        plot_param = {
            'num_occupied_mo_plot': self.occupied_mo_plot.get(),
            'num_unoccupied_mo_plot': self.unoccupied_mo_plot.get(),
            # 'ngrid' : self.ngrid.get(),
            # 'broadening' : self.broadening.get()
        } 
        return plot_param

class MaskingPage(View):
    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.engine = engine
        self.task_name = task_name

        self.SubFrame1 = self.input_param_frame 

        self.SubFrame2 = self.property_frame 

        self.SubFrame3 = self.submit_button_frame 

        self.Frame_button1 = self.save_button_frame 

        self.axis_var = tk.IntVar(value=0)
        self.region_var = tk.IntVar(value=0)
        self.plot_region = tk.StringVar()
        self.envelope_var = tk.IntVar(value=0)

        self.Frame_dm = ttk.Frame(self.SubFrame1)
        self.Frame_dm.grid(row=0, column=0, sticky='nsew')

        self.Frame_energy_coupling = ttk.Frame(self.SubFrame1)
        self.Frame_energy_coupling.grid(row=1, column=0, sticky='nsew')

        self.label_title_dm = tk.Label(self.Frame_dm,text="Parameters for Region Specific Dipole Moment", fg='blue')
        self.label_title_dm['font'] = myfont()
        self.label_title_dm.grid(row=0, column=0, sticky='w', padx=5, pady=10)

        self.region_frame = ttk.Frame(self.Frame_dm) 
        self.region_frame.grid(row=1, column=0, sticky='nsew')

        self.label_region = tk.Label(self.region_frame,text="Select the region:", fg='black')
        self.label_region['font'] = myfont()
        self.label_region.grid(row=0, column=0,sticky='w', padx=5, pady=5)

        region_list = ["Unmasked", "Masked", "Total"]
        self.entry_plot_region = ttk.Combobox(self.region_frame,textvariable= self.plot_region, value = region_list, width=30)
        self.entry_plot_region['font'] = myfont()
        self.entry_plot_region.current(0)
        self.entry_plot_region.grid(row=0, column=1)
        self.entry_plot_region['state'] = 'readonly'
        self.entry_plot_region.bind('<<ComboboxSelected>>', self.select_region)  
                
        self.axis_frame = ttk.Frame(self.Frame_dm)
        self.axis_frame.grid(row=2, column=0,columnspan=4, sticky='news')

        self.label_axis = tk.Label(self.axis_frame,text="Axis to Plot:", fg='black')
        self.label_axis['font'] = myfont()
        self.label_axis.grid(row=0, column=0, padx=10, pady=10) 

        axis_list = {"X":0, "Y":1, "Z":2}
        for (text, value) in axis_list.items():
            tk.Radiobutton(self.axis_frame, text=text, variable=self.axis_var, font=myfont2(),
                justify='left',value=value).grid(row=0, column=value+1, ipady=5, sticky='w')

        self.checkbox_envelope = tk.Checkbutton(self.Frame_dm, text="With envelope from Hilbert Transform", variable= self.envelope_var, font=myfont(), onvalue=1)
        self.checkbox_envelope.grid(row=3, column=0, ipady=5, sticky='w')

        self.plot_button = tk.Button(self.Frame_dm, text="Plot", activebackground="#78d6ff", command= lambda : self.event_generate(f'<<Plot{self.task_name}>>'))
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=3, column=1) 

        self.label_title_energy_coupling = tk.Label(self.Frame_energy_coupling,text="Calculation of Energy Transfer Coupling Constant", fg='blue')
        self.label_title_energy_coupling['font'] = myfont()
        self.label_title_energy_coupling.grid(row=0, column=0, padx=5, pady=10)   

        self.energy_coupling_button = tk.Button(self.Frame_energy_coupling, text="Compute", activebackground="#78d6ff", command= lambda : self.event_generate(f'<<SubLocal{self.task_name}>>'))
        self.energy_coupling_button['font'] = myfont()
        self.energy_coupling_button.grid(row=3, column=2) 

        self.back_button = tk.Button(self.Frame_button1, text="Back",activebackground="#78d6ff", command=lambda : self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0, padx=10, sticky='nswe') 

    def select_region(self, event):
        if self.plot_region.get()== "Total":
            self.checkbox_envelope.config(state='disabled')
            self.envelope_var.set(0)
            self.energy_coupling_button.config(state='disabled')
        else:
            self.checkbox_envelope.config(state='normal')
            self.energy_coupling_button.config(state='normal')

    def get_parameters(self):
        pol =  self.axis_var.get()
        if pol == 0:
            direction = [1, 0, 0]
        elif pol == 1:
            direction = [0, 1, 0]
        else:
            direction = [0, 0, 1]

        mask = {
            'region': self.plot_region.get(),
            'direction': direction,
            'envelope': True if self.envelope_var.get() == 1 else False
        }
        return mask

class PumpProbePostProcessPage(View):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self._default_var = {
            'damping' : ['float', 0],
            'padding' : ['int', 0],
            'delay_min' : ['float'],
            'delay_max' :['float'],
            'freq_min':['float'],
            'freq_max':['float'],
        }

        self._var = var_define(self._default_var)

        self.strength_frame = self.input_param_frame 
        self.contour_frame = self.property_frame
        self.button_frame = self.save_button_frame

        # self.add_job_frame(self.submit_button_frame, self.task_name)        

        self.heading = tk.Label(self.strength_frame,text="LITESOPH Pump-Probe Post-Processing", fg='blue')
        self.heading['font'] = myfont()
        # self.heading.pack()
        self.heading.grid(row=0, column=0, padx=2, pady=4)
        
        self.label_calc_strength = tk.Label(self.strength_frame, text= "Calculation of Oscillator Strength:",bg= label_design['bg'],fg=label_design['fg'])
        self.label_calc_strength['font'] = label_design['font']
        self.label_calc_strength.grid(row=1, column=0, padx=2, pady=4, sticky='w')   

        self.sub_frame_strength = ttk.Frame(self.strength_frame)
        self.sub_frame_strength.grid(row=2, column=0, sticky='nsew', columnspan=4)     

        self.label_damp = tk.Label(self.sub_frame_strength,text="Damping:",fg="black")
        self.label_damp['font'] = label_design['font']
        self.label_damp.grid(row=2, column=0, padx=2, pady=4, sticky='we' )

        self.entry_damp = tk.Entry(self.sub_frame_strength,textvariable =self._var['damping'])
        self.entry_damp['font'] = label_design['font']
        self.entry_damp.grid(row=2, column=1, padx=2, pady=4, sticky='we')

        self.label_pad = tk.Label(self.sub_frame_strength,text="Padding:",fg="black")
        self.label_pad['font'] = label_design['font']
        self.label_pad.grid(row=3, column=0, padx=2, pady=4, sticky='we')

        self.entry_pad = tk.Entry(self.sub_frame_strength,textvariable =self._var['padding'])
        self.entry_pad['font'] = label_design['font']
        self.entry_pad.grid(row=3, column=1, padx=2, pady=4, sticky='we')

        self.button_compute = tk.Button(self.sub_frame_strength,text="Compute")
        self.button_compute['font'] = label_design['font']
        self.button_compute.grid(row=3, column=2, padx=2, pady=4, sticky='we')

        #---------------------------------------------------------------------------------------------------
        self.label_contour = tk.Label(self.contour_frame, text= "2D Contour Plot Parameters:",bg= label_design['bg'],fg=label_design['fg'])
        self.label_contour['font'] = label_design['font']
        self.label_contour.grid(row=0, column=0, padx=2, pady=4, sticky='w')  

        self.frame_limit = ttk.Frame(self.contour_frame)
        self.frame_limit.grid(row=1, column=0, sticky='nsew', columnspan=4)

        self.label_min = tk.Label(self.frame_limit,text="Minimum",fg="black")
        self.label_min['font'] = label_design['font']
        self.label_min.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        self.label_max = tk.Label(self.frame_limit,text="Maximum",fg="black")
        self.label_max['font'] = label_design['font']
        self.label_max.grid(row=0, column=2, sticky='w', padx=5, pady=5)        

        # Delay range inputs
        self.label_delay = tk.Label(self.frame_limit,text="Delay Time range(in fs):",fg="black")
        self.label_delay['font'] = label_design['font']
        self.label_delay.grid(row=1, column=0, sticky='w', padx=5, pady=5)        

        self.entry_delay_min = ttk.Spinbox(self.frame_limit, width=5, textvariable=self._var['delay_min'], from_=0, to=1, increment=0.01)
        self.entry_delay_min['font'] = label_design['font']
        self.entry_delay_min.grid(row=1, column=1, padx=5, pady=5) 

        self.entry_delay_max = ttk.Spinbox(self.frame_limit, width=5, textvariable=self._var['delay_max'], from_=0, to=1, increment=0.01)
        self.entry_delay_max['font'] = label_design['font']
        self.entry_delay_max.grid(row=1, column=2, padx=5, pady=5) 
        
        # Frequency range inputs
        self.label_freq = tk.Label(self.frame_limit,text="Frequency range (in eV):",fg="black")
        self.label_freq['font'] = label_design['font']
        self.label_freq.grid(row=2, column=0, sticky='w', padx=5, pady=5)        

        self.entry_freq_min = ttk.Spinbox(self.frame_limit, width=5, textvariable=self._var['freq_min'], from_=0, to=1, increment=0.01)
        self.entry_freq_min['font'] = label_design['font']
        self.entry_freq_min.grid(row=2, column=1, padx=5, pady=5) 

        self.entry_freq_max = ttk.Spinbox(self.frame_limit, width=5, textvariable=self._var['freq_max'], from_=0, to=1, increment=0.01)
        self.entry_freq_max['font'] = label_design['font']
        self.entry_freq_max.grid(row=2, column=2, padx=5, pady=5) 

        self.button_plot = tk.Button(self.frame_limit, text="Plot")
        self.button_plot['font'] = myfont()
        self.button_plot.grid(row=2, column=3, padx=3, pady=6)       
        
        # Adding Buttons
        self.back_button = tk.Button(self.button_frame, text="Back",activebackground="#78d6ff",command=lambda:self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0, padx=3, pady=6)  
    
    def set_parameters(self, default_values:dict):
        for key, value in self._var.items():
            if key in default_values.keys():
                self._var[key].set(value)


    def get_parameters(self):
        return {'damping': self._var['damping'].get(),
                'padding': self._var['padding'].get()}

    def get_plot_parameters(self):
        return {'delay_min': self._var['delay_min'].get(),
                'delay_max': self._var['delay_max'].get(),
                'freq_min' : self._var['freq_min'].get(),
                'freq_max' : self._var['freq_max'].get()}