import tkinter as tk
from tkinter import ttk

from litesoph.common.data_sturcture.data_types import DataTypes as DT

def show_message(label_name, message):
    """ Shows a update """

    label_name.grid()
    label_name['text'] = message
    label_name['foreground'] = 'black'

def hide_message(label_name):
    """ Hides a tkinter widget"""
    label_name.grid_remove()

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
    elif pol_list == [0,0,1]:
        pol_var = "Z"                
    return pol_var

def get_input_list(input_str:str):
    """Converts the input string values(separated by whitespace or ',') 
    to list of float values"""

    inp_values = str(input_str)
    try:
        _values = inp_values.split(sep=',')
        _list = get_float_list(_values)
    except ValueError:      
        _values = inp_values.split() 
        _list = get_float_list(_values)
    return _list

def get_float_list(inp_str:list):
    """Converts list of strings to list of floats and returns, 
    else raises ValueError"""

    inp_list = []
    try:
        for inp in inp_str:
            inp_list.append(float(inp))
        return inp_list
    except ValueError as e:
        raise e