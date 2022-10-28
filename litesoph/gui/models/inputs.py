import tkinter as tk
from tkinter import Tk
from tkinter.ttk import Spinbox, Checkbutton, Combobox

gs_input ={"xc family": {
                "tab":"Basic",
                "group": "theory level",
                "text": "Exchange Correlation",
                "help": None,
                "widget": Combobox,
                "values": ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP","CAMY-B3LYP",
                        "PBE96","B3LYP","PW91", "BP86", "BP91","BHLYP","M05","M05-2X",
                        "M06-HF","M08-SO","M011","CAM-B3LYP","LC-BLYP","LC-PBE","LC-wPBE",
                        "HSE03","HSE06"
                        ],
                "default": 'PBE'
                },
        "basis_type:common": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Type",
        "help": None,
        "widget": Combobox,
        "values": ["LCAO","FD","PW","Gaussian"],
        "visible": True,
        "switch_keys": ["xc family"],
        "switch": lambda k:
                k.get("xc family", "") in ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP",
                                                "CAMY-B3LYP","PW91","CAM-B3LYP","LC-wPBE","HSE03","HSE06"]
        },

        "basis_type:extra": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Type",
        "help": None,
        "widget": Combobox,
        "values": ["Gaussian"],
        "visible": False,
        "switch_keys": ["xc family"],
        "switch": lambda k:
                k.get("xc family", "") in ["PBE96", "BP86", "BP91","BHLYP","M05","M05-2X",
                                                "M06-HF","M08-SO","M011","LC-BLYP","LC-PBE"]
        },
        "basis:nao": {
                "tab":"Basic",
                "group": "theory level",
                "text": "Basis Sets",
                "help": None,
                "widget": Combobox,
                "switch_keys": ["basis_type:common"],
                "values": ["dzp","sz","dz","szp","pvalence.dz"],
                "switch": lambda k:
                k.get("basis_type:common", "") == "LCAO"
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
                "switch_keys": ["basis_type:common","basis_type:extra"],
                "switch": lambda k:
                k.get("basis_type:common", "") == "Gaussian" or
                k.get("basis_type:extra","") == "Gaussian"
        },
        "spin": {
               "tab":"Basic",
                "group": "theory level",
                "text": "Spin Polarisation",
                "help": None,
                "widget": Combobox,
                "values": ["polarized","unpolarized"]
        },

        "spacing": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Grid Spacing (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":0.3,
                "switch_keys": ["basis_type:common"],
                "switch": lambda k:
                k.get("basis_type:common", "") in ["LCAO" ,"FD"]
                },

        "box shape": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Box Shape",
                "help": None,
                "widget": Combobox,
                "values": ["parallelepiped", "sphere", "cylinder", "minimum"],
                "switch_keys": ["basis_type:common"],
                "switch": lambda k:
                k.get("basis_type:common", "") in ["LCAO" ,"FD"]
        },

        "vacuum": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Vacuum (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":6,
                "switch_keys": ["select box","basis_type:common"],
                "switch": lambda k:
                # k.get("select box", True) is False and
                k.get("basis_type:common", "") in ["LCAO","FD","PW"],
                "state_switch":lambda k:
                k.get("select box", False) is False
        },

        "select box": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Enter Box Dimension",
                "help": None,
                "widget": Checkbutton,
                "default":False,
                "switch_keys": ["basis_type:common"],
                "switch": lambda k:
                k.get("basis_type:common", "") in ["LCAO","FD"]
        },

        "max itr": {
                "tab":"convergence",
                "group": "",
                "text": "Maximum Iteration",
                "help": None,
                "widget": Spinbox,
                "type": int,
                "default":500,
        },

        "energy conv": {
                "tab":"convergence",
                "group": "",
                "text": "Energy Convergence (in au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":10e-7
        },

        "density conv": {
                "tab":"convergence",
                "group": "",
                "text": "Density Convergence (in au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":10e-6
        },
        "smearing": {
                 "tab":"convergence",
                "group": "",
                "text": "Smearing",
                "help": None,
                "widget": tk.Entry,
                "type":str,               
                "default":0.05
        },
        "mixing": {
                 "tab":"convergence",
                "group": "",
                "text": "Mixing",
                "help": None,
                "widget": tk.Entry,
                "type":str,               
                "default":0.3
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
                "text": "Length in X (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select box","box shape"],
                "switch": lambda k:
                k.get("box shape", "") == "parallelepiped"
                and k.get("select box", False)
        },

        "box length_y": {
                "tab":"Basic",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "text": "Length in Y (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select box","box shape"],
                "switch": lambda k:
                k.get("box shape", "") == "parallelepiped"
                and k.get("select box", False)
        },
        "box length_z": {
                "tab":"Basic",
                "label_grid":{"row":2, "column":0},
                "widget_grid":{"row":2, "column":1},
                "text": "Length in Z (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select box","box shape"],
                "switch": lambda k:
                k.get("box shape", "") == "parallelepiped"
                and k.get("select box", False)
        },
        "radius": {
                "tab":"Basic",
                "label_grid":{"row":0, "column":0},
                "widget_grid":{"row":0, "column":1},
                "text": "Radius (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select box","box shape"],
                "switch": lambda k:
                k.get("box shape", "") in ["sphere","minimum","cylinder"]
                and k.get("select box", False)                
        },
        "cylinder length": {
                "tab":"Basic",
                "add_frame":"dimension",
                "parent":"simulation box",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "group": "simulation box",
                "text": "Length in X (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select box","box shape"],
                "switch": lambda k:
                k.get("box shape", "") == "cylinder"
                and k.get("select box", False)
        },

}

gs_visible_default = { 
        "xc family":True,               
        "basis_type:common": True,  
        "basis_type:extra": False,
        "basis:nao": True,  
        "basis:gaussian": False,
        "spacing": True,
        "spin": True,
        "box shape": True,
        "select box": True,
        "vacuum": True,
        "max itr":True,
        "energy conv": True,
        "density conv": True,
        "smearing": True,
        "mixing": True,
        "bands": True,
}