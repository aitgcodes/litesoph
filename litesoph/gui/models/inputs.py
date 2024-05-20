import copy
import tkinter as tk
from tkinter import Tk
from tkinter.ttk import Entry, Spinbox, Checkbutton, Combobox, Button

gs_input ={
        "restart": {
                "tab":"Basic",
                "text": "Restart Option",
                "help": None,
                "widget": Checkbutton,
                "default": False
        },
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
                # TODO: Polarization temporarily blocked
                # "values": ["unpolarized", "polarized"],
                "values": ["unpolarized"],
                "default": "unpolarized"
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
        # "restart_steps": {
        #         "tab":"Advanced",
        #         "group": "Execution Details",
        #         "text": "Restart Write Interval",
        #         "help": None,
        #         "widget": Entry,
        #         "default": 50,
        # },
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
        "restart": True,
        # "restart_steps": True
}

td_delta_input ={
        "restart": {
                "tab":"Delta Kick Input",
                "text": "Restart Option",
                "help": None,
                "widget": Checkbutton,
                "default": False
        },
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
        # "induced_density": {
        #         "tab":"Properties",
        #         "group": "Observables to extract",
        #         "text": "Induced Density",
        #         "help": None,
        #         "widget": Checkbutton,
        #         "default": False
        #         },
        # TODO: Implement Induced Density
        # "restart_steps": {
        #         "tab":"Properties",
        #         "group": "Execution Details",
        #         "text": "Restart Write Interval",
        #         "help": None,
        #         "widget": Entry,
        #         "default": 50,
        # },
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

laser_td_input = {
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
                "text": "Delay time list in fs",
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
                "text": "Time step (in attosecond)",
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
        # "laser_label": {
        #         "tab":"Laser Design",
        #         "group": "laser details",
        #         "text": "Laser Label",
        #         "help": None,
        #         "widget": tk.Entry,
        #         "type": str,
        #         "default": "Laser1",
        #         },
        "time_origin": {
                "tab":"Laser Design",
                "group": "laser details",
                "text": "Time Origin in as",
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
                "text": "Time Origin w.r.t. probe 1 in as",
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
                "text": "Peak Strength in au",
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
                "text": "Full Width Half Max (FWHM in eV)",
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
                "text": "Frequency (in eV)",
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
                "text": "Delta Kick Strength (in au)",
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

plot_laser_input ={
        "delay_time": {
                "tab":"Plot Laser",
                # "group": "extra details",
                "text": "Delay time (in femtosecond)",
                "help": None,
                "widget": Combobox,
                "type": float,
                "default": 0,
                # "switch": lambda k:
                # k.get("laser_type") == "Delta Pulse"
                },   
}

def get_td_laser_w_delay():
        copy_laser_td = copy.deepcopy(laser_td_input)
        copy_laser_td.update(
                {"delay_values": {
                        "tab":"External Fields",
                        "group": "Choose Options",
                        "text": "Delay time (in fs)",
                        "help": None,
                        "widget": Combobox,
                        "type": float,
                        # "default": "0",
                        "switch": lambda k:
                        k.get("exp_type") == "Pump-Probe"
                        }})
        copy_laser_td.pop("delay_list")
        return copy_laser_td              

def update_widget_laser_details(laser_labels:list):
        # copy_input_widget_dict = copy.deeepcopy(input_widget_dict)
        _dict = dict()
        # _dict.update({ 
        #         "Laser Added": {
        #         "tab":"External Fields",
        #         "group": "Details",
        #         "text": "Origin",
        #         "help": None,
        #         "widget": tk.Label,
        #         "type": str,
        #         }, } )
       
        for i, label in enumerate(laser_labels):
            _dict.update(
                {label: {
                "tab":"External Fields",
                "group": "Laser Details",
                "text": label,
                "help": None,
                "widget": Checkbutton,
                "default": True
                },}
            )
        return _dict
        

