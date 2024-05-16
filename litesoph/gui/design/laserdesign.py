import copy
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.ttk import Spinbox, Checkbutton, Combobox, Button

from litesoph.gui.design.template import View, InputFrame
from litesoph.gui.design.tools import set_state, var_define
from litesoph.gui.visual_parameter import myfont, label_design
from litesoph.utilities.units import as_to_au 

laser_design_input = {
        "laser_type":{
                "tab":"Laser Design",
                "group": "Choose Options",
                "text": "Type of laser",
                "help": None,
                "widget": Combobox,
                "default": "Gaussian Pulse",
                "values": ["Delta Pulse","Gaussian Pulse"],
                },
        "pump-probe_tag":{
                "tab":"Laser Design",
                "group": "Choose Options",
                "text": "Laser Tag",
                "help": None,
                "widget": Combobox,
                "default": "Pump",
                "values": ["Pump", "Probe"],
                },
        "time_origin": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Time Origin (as)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0,
                "switch": lambda k:
                k.get("pump-probe_tag") in ["Pump", None]
                },
        "time_origin:probe": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Time Origin w.r.t. probe 1 (as)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0,
                "switch": lambda k:
                k.get("pump-probe_tag") == "Probe"
                },
        "log_val": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Relative strength at time origin,10e-",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 6,
                "switch": lambda k:
                k.get("laser_type") == "Gaussian Pulse"
                },
        "laser_strength": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Peak Strength (au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                "switch": lambda k:
                k.get("laser_type") == "Gaussian Pulse"
                },
        "fwhm": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Full Width Half Max (eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1,
                "switch": lambda k:
                k.get("laser_type") == "Gaussian Pulse"
                },
        "freq": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Frequency (eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.0,
                "switch": lambda k:
                k.get("laser_type") == "Gaussian Pulse"
                },
        "pol_dir": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Polarization Direction",
                "help": None,
                "widget": Combobox,
                "values": ["X","Y", "Z"],
                "type": str
                },

        "delta_strength": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Delta Kick Strength (au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                "switch": lambda k:
                k.get("laser_type") == "Delta Pulse"
                },
        "masking":{
                "tab":"Masking",
                "group": "Choose Masking",
                "text": "Masked Electric Field",
                "help": None,
                "widget": Checkbutton,
                "default": False
                },
        "mask_type": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Mask Type",
                "help": None,
                "widget": Combobox,
                "values": ["Plane","Sphere"],
                },
        "boundary_type": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Boundary Type",
                "help": None,
                "widget": Combobox,
                "values": ["Abrupt", "Smooth"],
                },
        "r_sig": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "RSig",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.1,
                "switch": lambda k:
                k.get("boundary_type")=="Smooth"                  
                
                },
        "mask_plane:axis": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Axis",
                "help": None,
                "widget": Combobox,
                "values": ["X","Y", "Z"],
                "switch": lambda k:
                k.get("mask_type", '') == "Plane"
                
                },
        "mask_plane:origin": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Origin",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.5,
                "switch": lambda k:
                k.get("mask_type", '') == "Plane"
                },        
       
        "mask_sphere:radius": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Radius (angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.5,
                "switch": lambda k:
                k.get("mask_type", '') == "Sphere"
                },
        "mask_sphere:origin": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Origin",
                "help": None,
                "widget": tk.Label,
                "type": str,
                "switch": lambda k:
                k.get("mask_type", '') == "Sphere"
                },

        "mask_sphere:origin_x": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "X",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.5,
                "switch": lambda k:
                k.get("mask_type", '') == "Sphere"
                },
        "mask_sphere:origin_y": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Y",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.5,
                "switch": lambda k:
                k.get("mask_type", '') == "Sphere"
                },
        "mask_sphere:origin_z": {
                "tab":"Masking",
                "group": "Masking Inputs",
                "text": "Z",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.5,
                "switch": lambda k:
                k.get("mask_type", '') == "Sphere"
                },
}


class LaserDesignPage(View):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args)
        self.parent = parent
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        copy_laser_design_input = copy.deepcopy(laser_design_input)        
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
        

        laser_type = input_dict.get('laser_type')
        tag_var =  input_dict.get("pump-probe_tag")
        pol_var = input_dict.get("pol_dir")
        if laser_type == "Gaussian Pulse":
            l_type = "gaussian"
        elif laser_type == "Delta Pulse":
            l_type = "delta"
        
        if l_type == 'gaussian':
            laser_input = {
                "type": l_type,
                "inval" :  input_dict.get("log_val"),
                "strength": input_dict.get("laser_strength"),  
                "fwhm" :input_dict.get("fwhm"),
                "frequency" :  input_dict.get("freq"),
                'polarization': pol_var
            }
        
        else:  #only for delta_pulse 
            laser_input = {
                "type": l_type,
                "inval" :  input_dict.get("log_val"),
                "strength": input_dict.get("delta_strength"),  
                "fwhm" :2000,
                "frequency" :  0.002,
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
