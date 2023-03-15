import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import TclError

from litesoph.gui.input_validation import Onlydigits
from litesoph.gui.visual_parameter import myfont, config_widget
from litesoph.gui import visual_parameter as v

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


class View(ttk.Frame):
    """Tkinter Frame template for generic LITESOPH page.
    Defines a parent frame to hold multiple sub-frames."""

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


class InputFrame(ttk.Frame):
    """ 
    Tkinter Frame template for Input collecting.
    Parameters:
        master: (ttk.Frame) Parent tkinter frame
        fields: (dict) Nested dictionary for inputs defined by 
        example dictionary 
        padx: (int)
        pady: (int)
        column_minsize: (int)

    example_dict =
        {    'variable assigned for the input parameter':    
                    {
                    "tab": Tab name assigned for the input key(default: Main),
                    "group": Group name under the tab if applicable,
                    "text": Text to display,
                    "help": Additional details to the input key,
                    "widget": type of tkinter widget,
                    "default_value": default value,
                    "values": list of values (for Combobox widget type),
                    "type": variable type (assigned from default_value/values if not explicitly defined),
                    "visible": boolean for show/hide the input on default view,
                    "switch_keys": toggle condition for dependencies with preceeding keys defined
                    }
        }
    """
    def __init__(
    self,
    master=None,
    fields=None,
    visible_state = None,
    padx=1,
    pady=2,
    column_minsize=200,
            ):
        """Construct object."""
        super().__init__(master)
        self.padx = padx
        self.pady = pady
        self.column_minsize = column_minsize
        self.master = master
        self.fields = fields
        self.visible_state = visible_state
        v.set_inp_frame_style()
        self.tab_template()

    def tab_template(self):
        self.variable = {}      # tkinter variables
        self.label = {}         # Label widgets
        self.widget = {}        # widgets
        self.tab = {}           # tabs
        self.group = {}         # labelframes
        self.add_frame = {}
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.configure(style='InputFrame.TNotebook')

        if self.fields is None:
            return
        
        for i, (name, desc) in enumerate(self.fields.items()):
            if "tab" not in desc:
                desc["tab"] = "main"
            if desc["tab"] not in self.tab:
                parent = ttk.Frame(self.notebook)
                parent.columnconfigure(
                    [0, 1], weight=1, minsize=self.column_minsize
                )
                self.notebook.add(parent, text=desc["tab"].capitalize())
                self.tab[desc["tab"]] = parent   
            else:
                parent = self.tab[desc["tab"]]  

            if "group" in desc:
                if desc["group"] not in self.group:
                    group = ttk.LabelFrame(parent, text=desc["group"].capitalize())
                    group.columnconfigure(
                        [0, 1], weight=1, minsize=self.column_minsize
                    )
                    group.grid(         
                        row=i,
                        column=0,
                        columnspan=2,
                        sticky="ew",
                        padx=self.padx,
                        pady=1.5* self.pady,
                    )
                    self.group[desc["group"]] = group
                else:
                    group = self.group[desc["group"]]
                parent = group

            if "add_frame" in desc:
                if desc["add_frame"] not in self.add_frame:
                    _parent = desc["parent"]
                    add_frame = ttk.LabelFrame(self.group[_parent], text=desc["add_frame"].capitalize())
                    # group.columnconfigure(
                    #     [0, 1], weight=1, minsize=self.column_minsize
                    # )
                    add_frame.grid(         
                        row=i,
                        column=0,
                        columnspan=2,
                        sticky="ew",
                        padx=self.padx,
                        pady=self.pady,
                    )
                    self.add_frame[desc["add_frame"]] = add_frame
                else:
                    add_frame = self.add_frame[desc["add_frame"]]
                parent = add_frame

            if "values" in desc:
                values = list(desc["values"])
            if "type" not in desc:
                # if no type is given, first guess it based on a default value,
                # or infer from the first valid value.
                if "default" in desc and desc["default"] is not None:
                    desc["type"] = type(desc["default"])
                elif "values" in desc:
                    desc["type"] = type(
                        [v for v in values if v is not None][0]
                    )
                else:
                    raise ValueError(
                        f"could not infer type, please specify: {desc}"
                    )

            if "default" not in desc:
                # if no default is given, use the first value (even if None),
                # or infer from type.
                if "values" in desc:
                    desc["default"] = [v for v in values][0]
                elif "type" in desc:
                    desc["default"] = desc["type"]()
                else:
                    raise ValueError(
                        f"could not infer default, please specify: {desc}"
                    )
            if desc["type"] is int :
                self.variable[name] = tk.IntVar(self)
            elif desc["type"] is bool:
                self.variable[name] = tk.BooleanVar(self)
            elif desc["type"] is str:
                self.variable[name] = tk.StringVar(self)
            elif desc["type"] is float:
                self.variable[name] = tk.DoubleVar(self)
            else:
                raise ValueError(f"unknown type '{desc['type']}' for '{name}'")
            if "text" in desc:
                text = desc["text"]
            else:
                text = name.capitalize()
            if "widget" not in desc:
                desc["widget"] = ttk.Combobox

            if desc["widget"] is ttk.Checkbutton:
                self.widget[name] = desc["widget"](
                    parent, variable=self.variable[name], text=text
                )
            
            elif "values" in desc:
                self.widget[name] = desc["widget"](
                    parent, textvariable=self.variable[name], values=values
                )
                config_widget(self.widget[name], config_dict={'state':'readonly','font':v.label_design['font']})
            else:
                self.widget[name] = desc["widget"](
                    parent, textvariable=self.variable[name]
                )
                config_widget(self.widget[name], config_dict={'font':v.label_design['font']})
            if "widget_grid" in desc:
                self.widget[name].grid(
                row=desc["widget_grid"]["row"], column=desc["widget_grid"]["column"], sticky="ew", padx=self.padx, pady=self.pady)
            else:
                self.widget[name].grid(
                    row=i, column=1, sticky="ew", padx=self.padx, pady=self.pady
                )
            
##--------------hovering option
            # if "help" in desc:
            #     create_tooltip(self.widget[name], desc["help"])

            if desc["widget"] is not ttk.Checkbutton:
                self.label[name] = tk.Label(parent, text=text + ":")
                if "label_grid" in desc:
                    self.label[name].grid(
                    row=desc["label_grid"]["row"], column=desc["label_grid"]["column"], sticky="w", padx=self.padx, pady=self.pady)
                else:
                    self.label[name].grid(
                    row=i,
                    column=0,
                    sticky="w",
                    padx=self.padx,
                    pady=self.pady,
                )                
                config_widget(self.label[name],config_dict=v.label_design)

            if self.visible_state is None:
                if "visible" not in desc:
                    desc["visible"] = True

        self.init_widgets()
        if self.visible_state is None:
            self.update_widgets()
        else:
            self.update_widgets(var_state=self.visible_state)

    def frame_template(self, parent_frame,row, column, padx, pady, fields:dict):
        """
        Method to add additional frame to the default view designed by fields.
        Required in case of displaying new frames bound with some tkinter events 
        which can not be handled by switch_keys condition
        """
        obj = parent_frame
        obj.variable = {}     
        obj.label = {}      
        obj.widget = {}     
                
        if fields is None:
            return
        else:
            obj.fields = fields

        group = ttk.LabelFrame(parent_frame)
        group.columnconfigure(
            [0, 1], weight=1
        )
        group.grid(         
            row=row,
            column=column,
            columnspan=2,
            sticky="ew",
            padx=padx,
            pady=1.5* pady,
        )
        obj.group = group
        parent = group
        for i, (name, desc) in enumerate(fields.items()):

            if "values" in desc:
                values = list(desc["values"])
            if "type" not in desc:
                if "default" in desc and desc["default"] is not None:
                    desc["type"] = type(desc["default"])
                elif "values" in desc:
                    desc["type"] = type(
                        [v for v in values if v is not None][0]
                    )
                else:
                    raise ValueError(
                        f"could not infer type, please specify: {desc}"
                    )

            if "default" not in desc:
                if "values" in desc:
                    desc["default"] = [v for v in values][0]
                elif "type" in desc:
                    desc["default"] = desc["type"]()
                else:
                    raise ValueError(
                        f"could not infer default, please specify: {desc}"
                    )
            if desc["type"] is int :
                obj.variable[name] = tk.IntVar(self)
            elif desc["type"] is bool:
                obj.variable[name] = tk.BooleanVar(self)
            elif desc["type"] is str:
                obj.variable[name] = tk.StringVar(self)
            elif desc["type"] is float:
                obj.variable[name] = tk.DoubleVar(self)
            else:
                raise ValueError(f"unknown type '{desc['type']}' for '{name}'")
            if "text" in desc:
                text = desc["text"]
            else:
                text = name.capitalize()

            if "widget" not in desc:
                desc["widget"] = ttk.Combobox

            if desc["widget"] is ttk.Checkbutton:
                obj.widget[name] = desc["widget"](
                    parent, variable=obj.variable[name], text=text)

            elif "values" in desc:
                obj.widget[name] = desc["widget"](
                    parent, textvariable=obj.variable[name], values=values
                )
                config_widget(obj.widget[name], config_dict={'state':'readonly','font':v.label_design['font']})
            else:
                obj.widget[name] = desc["widget"](
                    parent, textvariable=obj.variable[name]
                )
                config_widget(obj.widget[name], config_dict={'font':v.label_design['font']})
            if "widget_grid" in desc:
                obj.widget[name].grid(
                row=desc["widget_grid"]["row"], column=desc["widget_grid"]["column"], sticky="ew", padx=padx, pady=pady)
            else:

                obj.widget[name].grid(
                    row=i, column=1, sticky="ew", padx=padx, pady=pady
                )
            if desc["widget"] is not ttk.Checkbutton:
                obj.label[name] = tk.Label(parent, text=text + ":")
                if "label_grid" in desc:
                    obj.label[name].grid(
                    row=desc["label_grid"]["row"], column=desc["label_grid"]["column"], sticky="w", padx=padx, pady=pady)
                else:
                    obj.label[name].grid(
                    row=i,
                    column=0,
                    sticky="w",
                    padx=padx,
                    pady=pady,
                )
                
                config_widget(obj.label[name],config_dict=v.label_design)

            if "visible" not in desc:
                desc["visible"] = True
                
        self.variable.update(obj.variable)     
        self.label.update(obj.label)        
        self.widget.update(obj.widget)       
        self.fields.update(fields)

        self.init_widgets(fields= fields)

    def enable(self, name):
        """Show a widget by name."""
        if self.fields[name]["visible"]:
            return
        self.toggle(name)

    def disable(self, name):
        """Hide a widget by name."""
        if not self.fields[name]["visible"]:
            return
        self.toggle(name)

    def toggle(self, name):
        """Hide or show a widget by name."""
        if not self.fields[name]["visible"]: 
            self.widget[name].grid()
            if name in self.label:
                self.label[name].grid()
        else:
            self.widget[name].grid_remove()
            if name in self.label:
                self.label[name].grid_remove()
        self.fields[name]["visible"] = not self.fields[name]["visible"]

    def update_widgets(self, check_switch=True,*args,var_state:dict=None, **kwargs):

            """enable/disable widgets from switch if check_switch is True, 
            else from variable_state dict"""
            
            if self.fields is None:
                return
            
            if var_state is None:
                check_switch = True
            else:
                check_switch = False
                for name, desc in self.fields.items():
                    try:
                        if var_state[name]:
                            desc["visible"] = True
                        else:
                            desc["visible"] = False
                            self.widget[name].grid_remove()
                            if name in self.label:
                                self.label[name].grid_remove()
                    except:
                        raise KeyError("Key not found")  

            visible_options = {}
            if check_switch:                
                for name in self.variable:                                       
                    if self.fields[name]["visible"]:
                        try:
                            visible_options[name] = self.variable[name].get()
                        except TclError:
                            visible_options[name] = self.fields[name]["default"]
            
            if check_switch and visible_options is not None:
                for name, desc in self.fields.items():
                        if "switch" in desc:
                            if desc["switch"](visible_options):                                
                                self.enable(name)
                                if "state_switch" in desc:
                                    if desc["state_switch"](visible_options) is not None:
                                        if desc["state_switch"](visible_options) is False:
                                            self.widget[name].config(state = 'disabled')
                                        else:
                                            self.widget[name].config(state = 'normal')
                            else:
                                self.disable(name)    

    def init_widgets(self, fields=None, ignore_state=False, var_values:dict=None, **kwargs):
        """
        Method to handle defaults.
        Sets the default values from fields option, by default.
        Updates defaults from var_values if ignore_state is False
        Parameters:
            fields: dictionary with key and default values
            ignore_state: boolean to check whether to update the assigned defaults or not
            var_values: dictionary to update required set of input defaults
        """

        init_values = {}   

        if not fields:
            fields = self.fields
        default_values = {
            name: desc["default"] for name, desc in fields.items()
        }
        init_values.update(default_values) 

        if var_values and not ignore_state:
            init_values.update(var_values)

        for name, value in init_values.items():
            try:
                self.variable[name].set(value)
            except:
                raise KeyError("Key missing")
    
    def get_values(self, *_):
        """Return a dictionary of selected fields values."""

        values = {}
        for name in self.variable:
            if not self.fields[name]["visible"]:
                values[name] = None
                continue

            try:
                values[name] = self.variable[name].get()
            except TclError:
                values[name] = self.fields[name]["default"]

            if values[name] == "None":
                values[name] = None

            if "values" in self.fields[name]:
                translator = self.fields[name]["values"]
                if isinstance(translator, dict):
                    try:
                        values[name] = translator[values[name]]
                    except KeyError:
                        values[name] = translator[self.fields[name]["default"]]

            if values[name] == "None":
                values[name] = None
        return values

    def trace_variables(self, *_):
        """
        Method to trace the events on any update of widgets using switch_keys defined with fields.
        Needs modification for cases beyond simple switch conditions
        """
        for name, var in self.variable.items():
            var.trace("w", self.update_widgets) 
