import imp
import tkinter as tk
from tkinter import ttk
from tkinter import font
from litesoph.gui.design.template import View
from litesoph.gui.design.tree_design import TreeView, add_columns, update_tree_data
from litesoph.gui.visual_parameter import myfont, myfont2
from litesoph.gui import actions
 

class MaskingPage(View):
    def __init__(self, parent, engine,task_name, *args, **kwargs):
        super().__init__(parent, *args)

        region_tags_default = [
        {
        "region":"total",
        },
        {
        "region":"region 1(masked)",
        },
        {"region":"region 1(unmasked)",
        },
        ]

        tree_data = kwargs.get('region_tags', region_tags_default)

        self.engine = engine
        self.task_name = task_name

        self.SubFrame1 = self.input_param_frame 

        self.SubFrame2 = self.property_frame 

        self.SubFrame3 = self.submit_button_frame 

        self.Frame_button1 = self.save_button_frame 

        self.axis_var = tk.IntVar(value=0)
        self.region_var = tk.IntVar(value=0)
        self.plot_region = tk.StringVar()
        self.envelope_var = tk.BooleanVar()
        self.focus_var = tk.BooleanVar()

        self.Frame_dm = ttk.Frame(self.SubFrame1)
        self.Frame_dm.grid(row=0, column=0, sticky='nsew')

        self.Frame_energy_coupling = ttk.Frame(self.SubFrame1)
        self.Frame_energy_coupling.grid(row=1, column=0, sticky='nsew')

        self.label_title_dm = tk.Label(self.Frame_dm,text="Parameters for Region Specific Dipole Moment", fg='blue')
        self.label_title_dm['font'] = myfont()
        self.label_title_dm.grid(row=0, column=0, sticky='w', padx=5, pady=10)

        self.region_frame = ttk.Frame(self.Frame_dm) 
        self.region_frame.grid(row=1, column=0, sticky='nsew')

        self.label_region = tk.Label(self.region_frame,text="Select the region:", fg='black')
        self.label_region['font'] = myfont()
        self.label_region.grid(row=0, column=0,sticky='w', padx=5, pady=5)

        self.region_table = TreeView(self.region_frame)
        self.region_table.grid(row=0, column=1)
        add_columns(self.region_table.tree, tree_data=tree_data)
        update_tree_data(self.region_table.tree, tree_data=tree_data)         
                
        self.axis_frame = ttk.Frame(self.Frame_dm)
        self.axis_frame.grid(row=2, column=0,columnspan=4, sticky='news')

        self.label_axis = tk.Label(self.axis_frame,text="Axis to Plot:", fg='black')
        self.label_axis['font'] = myfont()
        self.label_axis.grid(row=0, column=0, padx=10, pady=10) 

        axis_list = {"X":0, "Y":1, "Z":2}
        for (text, value) in axis_list.items():
            tk.Radiobutton(self.axis_frame, text=text, variable=self.axis_var, font=myfont2(),
                justify='left',value=value).grid(row=0, column=value+1, ipady=5, sticky='w')

        self.label_title_energy_coupling = tk.Label(self.Frame_energy_coupling,text="Calculation of Energy Transfer Coupling Constant", fg='blue')
        self.label_title_energy_coupling['font'] = myfont()
        self.label_title_energy_coupling.grid(row=1, column=0, padx=5, pady=10)

        self.energy_coupling_button = tk.Button(self.Frame_energy_coupling, text="Compute", activebackground="#78d6ff", command= lambda : self.event_generate(f'<<SubLocal{self.task_name}>>'))
        self.energy_coupling_button['font'] = myfont()
        self.energy_coupling_button.grid(row=1, column=1)

        self.checkbox_envelope = tk.Checkbutton(self.Frame_energy_coupling, text="With envelope from Hilbert Transform", variable= self.envelope_var, font=myfont(), onvalue=1)
        self.checkbox_envelope.grid(row=2, column=0, ipady=5, sticky='w')
        
        self.plot_button = tk.Button(self.Frame_energy_coupling, text="Plot", activebackground="#78d6ff", command= lambda : self.event_generate(f'<<Plot{self.task_name}>>'))
        self.plot_button['font'] = myfont()
        self.plot_button.grid(row=2, column=1)

        self.back_button = tk.Button(self.Frame_button1, text="Back",activebackground="#78d6ff", command=lambda : self.event_generate(actions.SHOW_WORK_MANAGER_PAGE))
        self.back_button['font'] = myfont()
        self.back_button.grid(row=0, column=0, padx=10, sticky='nswe') 

    def get_regions(self):
        selected = self.region_table.tree.selection()
        labels = []
        if len(selected)>0:
            return list(selected)

    def get_parameters(self):
        pol =  self.axis_var.get()
        if pol == 0:
            direction = [1, 0, 0]
        elif pol == 1:
            direction = [0, 1, 0]
        else:
            direction = [0, 0, 1]

        mask = {
            # 'region': self.plot_region.get(),
            'regions': self.get_regions(),
            'direction': direction,
            'envelope': True if self.envelope_var.get() == 1 else False
        }
        return mask

