from litesoph.test.view_gs import InputFrame
import tkinter as tk
# from tkinter import ttk
from tkinter import Tk
from tkinter.ttk import Spinbox, Checkbutton, Combobox

gs_model ={"xc family": {
                    "tab":"Basic",
                    "group": "theory level",
                    "text": "Exchange Correlation",
                    "help": None,
                    "widget": Combobox,
                    "values": ['LDA', 'PBE'],
                    "default": 'PBE',
        },
        "basis_type": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Type",
        "help": None,
        "widget": Combobox,
        "values": ["nao","fd","pw","gaussian"],
        },

        "basis:nao": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Sets",
        "help": None,
        "widget": Combobox,
        "values": ["dzp","sz","dz","szp","pvalence.dz"],
        "switch": lambda k:k["basis_type"] == "nao"
        },

        "basis:gaussian": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Sets",
        "help": None,
        "widget": Combobox,
        "values": ["6-31G","STO-2G","STO-3G",
                "STO-6G","3-21G","3-21G*","6-31G*",
                "6-31G**","6-311G","6-311G*","6-311G**",
                "cc-pVDZ","aug-cc-pvtz"],
        "switch": lambda k:k["basis_type"] == "gaussian"
        },

        "spacing": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Grid Spacing",
        "help": None,
        "widget": tk.Entry,
        "type": float,
        "switch": lambda k:k["basis_type"] == "nao" 
        or k["basis_type"] == "fd" 
        },

        "box shape": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Box Shape",
                "help": None,
                "widget": Combobox,
                "values": ["parallelepiped", "sphere", "cylinder", "minimum"],
                "switch": lambda k:k["basis_type"] in ["nao","fd" ]
        },

        "vaccum": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Vacuum",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:
                k["select box"] == False
                and k["basis_type"] in ["nao","fd","pw"]
        },

        "select box": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Enter Box Dimension",
                "help": None,
                "widget": Checkbutton,
                "default":False,
                "switch": lambda k:k["basis_type"] in ["nao","fd"]
        },

        "max itr": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Maximum Iteration",
                "help": None,
                "widget": tk.Spinbox,
                "type": int
        },

        "energy conv": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Energy Convergence",
                "help": None,
                "widget": tk.Entry,
                "type": float
        },

        "density conv": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Density Convergence",
                "help": None,
                "widget": tk.Entry,
                "type": float
        },

        "spin": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Spin Polarisation",
                "help": None,
                "widget": Combobox,
                "values": ["polarized","unpolarized"]
        },
        "smearing": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Smearing",
                "help": None,
                "widget": tk.Entry,
                "type":str
        },
        "mixing": {
                "tab":"Basic",
                "group": "dft details",
                "text": "Mixing",
                "help": None,
                "widget": tk.Entry,
                "type":str
        },
        "bands": {
                "tab":"Advanced",
                "text": "Number of Extra States",
                "help": None,
                "widget": tk.Entry,
                "type":int
        },

        }


box_dict = {
        "box length_x": {
                "tab":"Basic",                   
                "label_grid":{"row":0, "column":0},
                "widget_grid":{"row":0, "column":1},
                "text": "X length",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:
                k["box shape"] == "parallelepiped"
                and k["select box"]
        },

        "box length_y": {
                "tab":"Basic",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "text": "y length",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:k["box shape"] == "parallelepiped"
                and k["select box"] == True
        },
        "box length_z": {
                "tab":"Basic",
                "label_grid":{"row":2, "column":0},
                "widget_grid":{"row":2, "column":1},
                "text": "z length",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:k["box shape"] == "parallelepiped"
                and k["select box"] == True
        },
        "sphere radius": {
                "tab":"Basic",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "text": "Sphere Radius",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:
                k["box shape"] == "sphere"
                and k["select box"]
                
        },
          "min radius": {
                "tab":"Basic",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "text": "Min Radius",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:
                k["box shape"] == "minimum" 
                and k["select box"]               
        },

        "cylinder radius": {
                "tab":"Basic",
                "label_grid":{"row":0, "column":0},
                "widget_grid":{"row":0, "column":1},
                "text": "Cylinder Radius",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:
                k["box shape"] == "cylinder"
                and k["select box"]
        },
        "cylinder length": {
                "tab":"Basic",
                "add_frame":"dimension",
                "parent":"simulation box",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "group": "simulation box",
                "text": "X length",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "switch": lambda k:k["box shape"] == "cylinder"
                and k["select box"] == True
        },

}