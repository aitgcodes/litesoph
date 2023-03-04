import tkinter as tk
from tkinter import Tk
from tkinter.ttk import Spinbox, Checkbutton, Combobox, Button

gs_input ={
        "xc": {
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
        "basis_type": {
        "tab":"Basic",
        "group": "theory level",
        "text": "Basis Type",
        "help": None,
        "widget": Combobox,
        "values": ["lcao","fd","pw","gaussian"],
        "visible": True,
        "switch_keys": ["xc"],
        # "switch": lambda k:
        #         k.get("xc_family", "") in ["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP",
        #                                         "CAMY-B3LYP","PW91","CAM-B3LYP","LC-wPBE","HSE03","HSE06"]
        },

        # "basis_type:extra": {
        # "tab":"Basic",
        # "group": "theory level",
        # "text": "Basis Type",
        # "help": None,
        # "widget": Combobox,
        # "values": ["gaussian"],
        # "visible": False,
        # "switch_keys": ["xc family"],
        # "switch": lambda k:
        #         k.get("xc family", "") in ["PBE96", "BP86", "BP91","BHLYP","M05","M05-2X",
        #                                         "M06-HF","M08-SO","M011","LC-BLYP","LC-PBE"]
        # },
        "basis:lcao": {
                "tab":"Basic",
                "group": "theory level",
                "text": "Basis Sets",
                "help": None,
                "widget": Combobox,
                "switch_keys": ["basis_type"],
                "values": ["dzp","sz","dz","szp","pvalence.dz"],
                "switch": lambda k:
                k.get("basis_type", "") == "lcao"
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
                "switch_keys": ["basis_type"],
                "switch": lambda k:
                k.get("basis_type", "") == "gaussian" 
                # or k.get("basis_type:extra","") == "gaussian"
        },
        "spin": {
               "tab":"Basic",
                "group": "theory level",
                "text": "Spin Polarisation",
                "help": None,
                "widget": Combobox,
                "values": ["unpolarized", "polarized"]
        },

        "spacing": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Grid Spacing (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":0.3,
                "switch_keys": ["basis_type"],
                "switch": lambda k:
                k.get("basis_type", "") in ["lcao" ,"fd"]
                },

        "boxshape": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Box Shape",
                "help": None,
                "widget": Combobox,
                "values": ["parallelepiped", "sphere", "cylinder", "minimum"],
                "switch_keys": ["basis_type"],
                "switch": lambda k:
                k.get("basis_type", "") in ["lcao" ,"fd"]
        },

        "vacuum": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Vacuum (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":6,
                "switch_keys": ["select_box","basis_type"],
                "switch": lambda k:
                # k.get("select box", True) is False and
                k.get("basis_type", "") in ["lcao","fd","pw"],
                "state_switch":lambda k:
                k.get("select_box", False) is False
        },

        "select_box": {
                "tab":"Basic",
                "group": "simulation box",
                "text": "Enter Box Dimension",
                "help": None,
                "widget": Checkbutton,
                "default":False,
                "switch_keys": ["basis_type"],
                "switch": lambda k:
                k.get("basis_type", "") in ["lcao","fd"]
        },

        "max_itr": {
                "tab":"convergence",
                "group": "",
                "text": "Maximum Iteration",
                "help": None,
                "widget": Spinbox,
                "type": int,
                "default":500,
        },

        "energy_conv": {
                "tab":"convergence",
                "group": "",
                "text": "Energy Convergence (in au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":10e-7
        },

        "density_conv": {
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
        "box_length_x": {
                "tab":"Basic",                   
                "label_grid":{"row":0, "column":0},
                "widget_grid":{"row":0, "column":1},
                "text": "Length in X (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select_box","boxshape"],
                "switch": lambda k:
                k.get("boxshape", "") == "parallelepiped"
                and k.get("select_box", False)
        },

        "box_length_y": {
                "tab":"Basic",
                "label_grid":{"row":1, "column":0},
                "widget_grid":{"row":1, "column":1},
                "text": "Length in Y (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select_box","boxshape"],
                "switch": lambda k:
                k.get("boxshape", "") == "parallelepiped"
                and k.get("select_box", False)
        },
        "box_length_z": {
                "tab":"Basic",
                "label_grid":{"row":2, "column":0},
                "widget_grid":{"row":2, "column":1},
                "text": "Length in Z (in angstrom)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default":12,
                "switch_keys": ["select_box","boxshape"],
                "switch": lambda k:
                k.get("boxshape", "") == "parallelepiped"
                and k.get("select_box", False)
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
                "switch_keys": ["select_box","boxshape"],
                "switch": lambda k:
                k.get("boxshape", "") in ["sphere","minimum","cylinder"]
                and k.get("select_box", False)                
        },
        "cylinder_length": {
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
                "switch_keys": ["select_box","boxshape"],
                "switch": lambda k:
                k.get("boxshape", "") == "cylinder"
                and k.get("select_box", False)
        },

}
gs_visible_default = { 
        "xc":True,               
        "basis_type": True,  
        # "basis_type:extra": False,
        "basis:lcao": True,  
        "basis:gaussian": False,
        "spacing": True,
        "spin": True,
        "boxshape": True,
        "select_box": True,
        "vacuum": True,
        "max_itr":True,
        "energy_conv": True,
        "density_conv": True,
        "smearing": True,
        "mixing": True,
        "bands": True,
}

td_delta_input ={
        "laser_strength": {
                "tab":"Delta Kick Input",
                # "group": "laser details",
                "text": "Laser Strength in a.u (Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                # "switch": lambda k:
                # k.get("pump_probe", False) is False
                },
       
        "time_step": {
                "tab":"Delta Kick Input",
                # "group": "simulation ",
                "text": "Time step (in attosecond)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 10,
                }, 
        "number_of_steps": {
                "tab":"Delta Kick Input",
                # "group": "simulation ",
                "text": "Number of Steps",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 2000
                },
        "output_freq": {
                "tab":"Delta Kick Input",
                # "group": "simulation ",
                "text": "Frequency of data collection",
                "help": None,
                "widget": tk.Entry,
                "type": int,
                "default": 10
                },
        "pol_dir": {
                "tab":"Delta Kick Input",
                # "group": "simulation ",
                "text": "Polarization Direction",
                "help": None,
                "widget": Combobox,
                "values": ["X","Y", "Z"],
                "type": str
                },
        
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
                "text": "Population Correlation",
                "help": None,
                "widget": Checkbutton,
                "default": False
                },
        }

td_laser_input ={
        "pump_probe":{
                "tab":"External Fields",
                "group": "Choose Options",
                "text": "Pump-Probe setup",
                "help": None,
                "widget": Checkbutton,
                "default": False
                },
        "probe_options": {
                "tab":"External Fields",
                "group": "Choose Options",
                "text": "Probe Options",
                "help": None,
                "widget": Combobox,
                "default": "Delta Probe",
                "values": ["Delta Probe","Gaussian Probe"],
                "switch": lambda k:
                k.get("pump_probe", False) 
                },       
        "time_origin": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "Time Origin (tin) in attosecond",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                },
        "log_val": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "-log((E at tin)/Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 6,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                },
        "laser_strength": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "Laser Strength in a.u (Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                },
        "fwhm": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "Full Width Half Max (FWHM in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                },
        "freq": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "Frequency (in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.0,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                },
        "laser_time": {
                "tab":"External Fields",
                "group": "laser details",
                "text": "Laser profile time (in femtosecond)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 10,
                "switch": lambda k:
                k.get("pump_probe", False) is False
                }, 
        "time_step": {
                "tab":"Simulation Parameters",
                "group": "simulation ",
                "text": "Time step (in attosecond)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 10,
                }, 
        "num_steps": {
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
        "pol_dir": {
                "tab":"Simulation Parameters",
                "group": "simulation ",
                "text": "Polarization Direction",
                "help": None,
                "widget": Combobox,
                "values": ["X","Y", "Z"],
                "type": str
                },
        
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
        "population": {
                "tab":"Properties",
                "group": "Observables to extract",
                "text": "Population Correlation",
                "help": None,
                "widget": Checkbutton,
                "default": False
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
                k.get("boundary_type")=="Abrupt"                  
                
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
                "text": "Radius (in angstrom)",
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

pump_input = {
        "pump:time_origin": {
                "tab":"External Fields",
                "group": "pump laser details",
                "text": "Time Origin (tin) in attosecond",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0, 
                },
        "pump:log_val": {
                "tab":"External Fields",
                "group": "pump laser details",
                "text": "-log((E at tin)/Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 6,
                },
        "pump:laser_strength": {
                "tab":"External Fields",
                "group": "pump laser details",
                "text": "Laser Strength in a.u (Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                },
        "pump:fwhm": {
                "tab":"External Fields",
                "group": "pump laser details",
                "text": "Full Width Half Max (FWHM in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1,
                },
        "pump:freq": {
                "tab":"External Fields",
                "group": "pump laser details",
                "text": "Frequency (in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.0,
                },
        }

probe_delta_input = {
        "probe:delta strength": {
                "tab":"External Fields",
                "group": "probe laser details",
                "text": "Delta Kick Strength (in au)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                },
        }

probe_gaussian_input ={
        # "probe:time_origin": {
        #         "tab":"External Fields",
        #         "group": "probe laser details",
        #         "text": "Time Origin (tin) in attosecond",
        #         "help": None,
        #         "widget": tk.Entry,
        #         "type": float,
        #         "default": 0,
        #         },
        "probe:log_val": {
                "tab":"External Fields",
                "group": "probe laser details",
                "text": "-log((E at tin)/Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 6,
                },
        "probe:laser_strength": {
                "tab":"External Fields",
                "group": "probe laser details",
                "text": "Laser Strength in a.u (Eo)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1e-05,
                },
        "probe:fwhm": {
                "tab":"External Fields",
                "group": "probe laser details",
                "text": "Full Width Half Max (FWHM in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 1,
                },
        "probe:freq": {
                "tab":"External Fields",
                "group": "probe laser details",
                "text": "Frequency (in eV)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0.0,
                },
        }

pump_probe_extra_input = {
        "pump_probe:laser_time": {
                "tab":"External Fields",
                "group": "extra details",
                "text": "Laser profile time (in femtosecond)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 10,
                }, 
        "pump_probe:delay_time": {
                "tab":"External Fields",
                "group": "extra details",
                "text": "Delay time (in femtosecond)",
                "help": None,
                "widget": tk.Entry,
                "type": float,
                "default": 0,
                },
       
        }

button_frame_input = {
        "laser_design": {
                "tab":"External Fields",
                "group": " details",
                "text": "Laser Design",
                "help": None,
                "widget": Button,
                "type": str,
                },

}        
