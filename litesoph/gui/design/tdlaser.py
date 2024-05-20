import copy
import tkinter as tk
from tkinter import font
from tkinter.ttk import Spinbox, Checkbutton, Combobox, Button

from litesoph.gui.design.template import View, InputFrame, add_job_frame
from litesoph.gui.design.tools import hide_message, show_message
from litesoph.gui.defaults_handler import update_td_laser_defaults

laser_td_input = {
        "restart": {
                "tab":"External Fields",
                "text": "Restart Option",
                "help": None,
                "widget": Checkbutton,
                "default": False
        },
        
        "field_type":{
                "tab":"External Fields",
                "group": "Choose Options",
                "text": "Type of fields",
                "help": None,
                "widget": Combobox,
                "default": "Electric Field",
                "values": ["None","Electric Field"],
                },
              
        "exp_type": {
                "tab":"External Fields",
                "group": "Choose Options",
                "text": "Type of Experiment",
                "help": None,
                "widget": Combobox,
                "default": "Pump-Probe",
                "values": ["State Preparation", "Pump-Probe"],
                },

        "delay_list": {
                "tab":"External Fields",
                "group": "Choose Options",
                "text": "Delay time list (fs)",
                "help": None,
                "widget": tk.Entry,
                "type": str,
                "default": "0",
                "switch": lambda k:
                k.get("exp_type") == "Pump-Probe"
                },
        "time_step": {
                "tab":"Simulation Parameters",
                "group": "simulation ",
                "text": "Time step (as)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 10,
                }, 
        "number_of_steps": {
                "tab":"Simulation Parameters",
                "group": "simulation ",
                "text": "Number of Steps",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 2000
                },
        "output_freq": {
                "tab":"Simulation Parameters",
                "group": "simulation ",
                "text": "Frequency of data collection",
                "help": None,
                "widget": tk.Entry,
                "type": int,
                "default": 10
                },
        # "restart_steps": {
        #         "tab":"Simulation Parameters",
        #         "group": "Execution Details",
        #         "text": "Restart Write Interval",
        #         "help": None,
        #         "widget": tk.Entry,
        #         "default": 1,
        # },
        "spectrum": {
                "tab":"Properties",
                "group": "Observables to extract",
                "text": "Absorption Spectrum",
                "help": None,
                "widget": Checkbutton,
                "default": True
                },
        "ksd": {
                "tab":"Properties",
                "group": "Observables to extract",
                "text": "Kohn Sham Decomposition",
                "help": None,
                "widget": Checkbutton,
                "default": False
                }, 
        "mo_population": {
                "tab":"Properties",
                "group": "Observables to extract",
                "text": "Population Tracking",
                "help": None,
                "widget": Checkbutton,
                "default": False
                },
        # "induced_density": {
        #         "tab":"Properties",
        #         "group": "Observables to extract",
        #         "text": "Induced Density",
        #         "help": None,
        #         "widget": Checkbutton,
        #         "default": False
        #         },
        # TODO: Implement Induced Density
        }

def get_td_laser_w_delay():
        copy_laser_td = copy.deepcopy(laser_td_input)
        copy_laser_td.update(
                {"delay_values": {
                        "tab":"External Fields",
                        "group": "Choose Options",
                        "text": "Delay time (fs)",
                        "help": None,
                        "widget": Combobox,
                        "type": float,
                        "switch": lambda k:
                        k.get("exp_type") == "Pump-Probe"
                        }})
        copy_laser_td.pop("delay_list")
        return copy_laser_td 

class TDPage(View):

    def __init__(self, parent, task_name, *args, **kwargs):
        super().__init__(parent, *args)     

        self.parent = parent
        self.task_name = task_name
        self.laser_defined = False
        self.delay_value = tk.DoubleVar()
        self.delay_options = []

        self.input_widget_dict = kwargs.get('input_widget_dict', None)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.add_widgets(self.input_widget_dict)

        # self.laser_details = tk.Label(self.input_param_frame, text='None')
        # self.laser_details.grid(row=1, column=0, sticky='we')

        add_job_frame(self, self.submit_button_frame, task_name, column=1)

        #self.button_back = tk.Button(self.save_button_frame, text="Back to main page", activebackground="#78d6ff", state="disabled")
        #self.button_back = tk.Button(self.save_button_frame, text="Back to main page", activebackground="#78d6ff", command=lambda: self.back_button())
        #self.button_back['font'] = myFont
        #self.button_back.grid(row=0, column=1, padx=3, pady=3,sticky='nsew')

        self.button_view = tk.Button(self.save_button_frame, text="Generate Input", activebackground="#78d6ff", command=lambda: self.generate_input_button())
        self.button_view['font'] = myFont
        self.button_view.grid(row=0, column=3,padx=3, pady=3,sticky='nsew')
        self.button_view.config(state='disabled')
        
        self.button_save = tk.Button(self.save_button_frame, text="Save Input", activebackground="#78d6ff", command=lambda: self.save_button())
        self.button_save['font'] = myFont
        self.button_save.grid(row=0, column=5, padx=3, pady=3,sticky='nsew')
        self.button_save.config(state='disabled')

        self.label_msg = tk.Label(self.save_button_frame,text="")
        self.label_msg['font'] = myFont
        self.label_msg.grid(row=0, column=7, sticky='nsew')

        self.trace_variables()

    def add_widgets(self, input_widget_dict:dict):
        """ Adds widgets to TD Page"""

        for widget in self.input_param_frame.winfo_children():
            widget.destroy()
        
        if input_widget_dict is None:
            input_widget_dict = laser_td_input

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
        self.event_generate('<<Save'+self.task_name+'Script>>')

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
        show_message(self.label_msg, msg)

    def unset_label_msg(self):
        hide_message(self.label_msg)
    
    def get_property_list(self, gui_values:dict):
        prop_list = ['spectrum']
        if gui_values.get("ksd") is True:
            prop_list.append("ksd")
        if gui_values.get("mo_population") is True:
            prop_list.append("mo_population") 
        if gui_values.get("induced_density") is True:
            prop_list.append("induced_density")   
        return prop_list  

    def get_delay_list(self, delay_str:str):
        """Converts delay string value entries and returns list of float values """
        from litesoph.gui.design.tools import get_input_list
        delay_values = str(delay_str)
        try:
            delay_list = get_input_list(input_str= delay_values)
            return delay_list
        except ValueError as e:
            raise e

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
        """
        Updates TD-gui input parameters from the widgets,
        Updates pump-probe delay list with validation
        """
        gui_dict = copy.deepcopy(self.inp.get_values())

        if gui_dict.get('delay_list') is not None:
            try:
                gui_dict.update({'delay_list': self.get_delay_list(gui_dict.get('delay_list'))})
                return gui_dict
            except ValueError:
                raise ValueError('Error with input delay values!')
        else:
            return gui_dict

    def get_parameters(self):
        gui_dict = copy.deepcopy(self.inp.get_values())

        td_input = {
            'time_step' : gui_dict.get("time_step"),
            'number_of_steps' : gui_dict.get("number_of_steps"),
            'output_freq': gui_dict.get("output_freq"),
            'properties' : self.get_property_list(gui_dict),
            'restart': gui_dict.get("restart"),
            # 'restart_steps': gui_dict.get("restart_steps")
        }
        return td_input

    def set_parameters(self, default_param_dict:dict):
        """To update parameters of laser-td page"""
        
        default_gui_dict = update_td_laser_defaults(default_param_dict)
        self.inp.init_widgets(fields=self.inp.fields,
                        ignore_state=False,var_values=default_gui_dict)

