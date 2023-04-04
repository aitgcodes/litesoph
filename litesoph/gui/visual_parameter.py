from tkinter import font
import tkinter as tk
from tkinter import ttk

def myfont1():
    myFont15= font.Font(family='Helvetica', size=15, weight='bold')
    l= font.Font(family ='Courier', size=10,weight='bold') 
    return myFont15  

def myfont():
    myFont = font.Font(family='Helvetica', size=10, weight='bold')
    l= font.Font(family ='Courier', size=15,weight='bold') 
    font5 = font.Font(family='Times New Roman',size=15)
    return font5

def myfont2():
    myfont2= font.Font(family='Helvetica', size=10)
    font3 = font.Font(family='Comic Sans MS', size=10)
    font4 = font.Font(family='Times New Roman',size=15, weight='bold' )
    font5 = font.Font(family='Times New Roman',size=15)
    return myfont2

def myfont15():
    myFont = font.Font(family='Helvetica', size=10, weight='bold')
    l= font.Font(family ='Courier', size=15,weight='bold') 
    font15 = font.Font(family='Helvetica',size=15, weight='bold')
    return font15

def config_widget(widget,config_dict:dict):
    """ config dict : wrt the available parameters of the widget"""
    widget.config(config_dict)

f1=('Noto sans', 15, 'italic')
mygreen = "#d2ffd2"
myred = "#dd0202"   

label_design= {}

work_flow_ui_design = {}

def create_design_feature():

    label_design.update({
    'bg':"navy blue",
    "fg": "white",
    "font": myfont()
    })
    
    work_flow_ui_design.update({'highlightbackground':'red',
                    'background':'light blue',
                    'font': myfont()})
button_design={}


# --------------------------tkinter Style objects-------------------------------

def set_inp_frame_style():
    inp_frame_style = ttk.Style()
    inp_frame_style.theme_use('default')
    # Notebook and tabs
    inp_frame_style.configure(
        'InputFrame.TNotebook', 
    )
    inp_frame_style.configure(
        'InputFrame.TNotebook.Tab', 
        font = ('Helvetica', 10)
    )
    inp_frame_style.map("InputFrame.TNotebook.Tab", 
                        background= [("selected", 'light blue')])

def set_wf_style():
    wf_design_style = ttk.Style()
    wf_design_style.theme_use('default')
    wf_design_style.configure('Wf.TLabel',
    relief='solid', anchor=tk.CENTER,
    font = ('Times New Roman', 15)
            )
    wf_design_style.configure('Default.Wf.TLabel',
                background='light blue',
                )
    wf_design_style.configure('Done.Wf.TLabel',
                background='pale green',
                            )
    wf_design_style.configure('Current.Wf.TLabel',
                background='light yellow',
                            )