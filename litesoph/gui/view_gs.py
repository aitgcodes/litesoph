from tkinter import ttk
import tkinter as tk
from tkinter import TclError

from litesoph.test.workflow import config_widget
from litesoph.gui import visual_parameter as v

class InputFrame(ttk.Frame):
    
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
                        columnspan=4,
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
            # if desc["type"] is int or desc["type"] is np.int64:
            #     self.variable[name] = tk.IntVar(self)
            if desc["type"] is int :
                self.variable[name] = tk.IntVar(self)
            elif desc["type"] is bool:
                self.variable[name] = tk.BooleanVar(self)
            elif desc["type"] is str:
                self.variable[name] = tk.StringVar(self)
            elif desc["type"] is float:
                self.variable[name] = tk.DoubleVar(self)
                # if "values" in desc:
                #     values = [np.round(v, 2) for v in values]
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
            else:
                self.widget[name] = desc["widget"](
                    parent, textvariable=self.variable[name]
                )
            if "widget_grid" in desc:
                self.widget[name].grid(
                row=desc["widget_grid"]["row"], column=desc["widget_grid"]["column"], sticky="ew", padx=self.padx, pady=self.pady)
            else:
                self.widget[name].grid(
                    row=i, column=1, sticky="ew", padx=self.padx, pady=self.pady
                )
            # config_widget(self.widget[name], config_dict={'font':v.label_design['font']})
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
                # if "values" in desc:
                #     values = [np.round(v, 2) for v in values]
            else:
                raise ValueError(f"unknown type '{desc['type']}' for '{name}'")
            if "text" in desc:
                text = desc["text"]
            else:
                text = name.capitalize()
            # if "visible" in desc:
            #     pass
            # else:
            if "widget" not in desc:
                desc["widget"] = ttk.Combobox

            if desc["widget"] is ttk.Checkbutton:
                obj.widget[name] = desc["widget"](
                    parent, variable=obj.variable[name], text=text)

            elif "values" in desc:
                obj.widget[name] = desc["widget"](
                    parent, textvariable=obj.variable[name], values=values
                )
            else:
                obj.widget[name] = desc["widget"](
                    parent, textvariable=obj.variable[name]
                )
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

 