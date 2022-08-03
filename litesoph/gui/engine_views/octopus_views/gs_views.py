import tkinter as tk
from tkinter import ttk
from tkinter import font
from litesoph.gui import images
from litesoph.gui.input_validation import Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15

from litesoph.gui.engine_views import EngineViews
from litesoph.simulations.models import OctopusModel


class OctGSPage(EngineViews):

    def __init__(self, gspage) -> None:
        
        self.gspage = gspage
        self.default_para = OctopusModel.ground_state

    def show_system_tab(self, parent):
        """ Creates widgets for system tab inputs"""

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=0, column=0)      

        self.heading = tk.Label(mode_frame,text="LITESOPH input for Ground State",fg='green')
        self.heading['font'] = myfont15()
        self.heading.grid(row=0, column=0, pady=5)
                
        self.label_proj = tk.Label(mode_frame,text="Mode",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        task = ttk.Combobox(mode_frame, textvariable = self._var['mode'], values= self.default_para['mode']['values'])
        task['font'] = label_design['font']
        task.grid(row=2, column= 1, sticky='w', padx=2, pady=2)
        #task.bind("<<ComboboxSelected>>", pick_box)
        task['state'] = 'readonly'

        self.charge = tk.Label(mode_frame, text="Charge",bg=label_design['bg'], fg=label_design['fg'])
        self.charge['font'] = label_design['font']
        self.charge.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_chrg = Onlydigits(mode_frame,textvariable=self._var['charge'])
        self.entry_chrg['font'] = label_design['font']
        self.entry_chrg.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        multiplicity_label = tk.Label(mode_frame, text='Multiplicity',bg=label_design['bg'], fg=label_design['fg'])
        multiplicity_label['font'] = label_design['font']
        multiplicity_label.grid(row=7, column=0, sticky='w', padx=2, pady=4)

        multiplicity_entry = Onlydigits(mode_frame,textvariable= self._var['multip'])
        multiplicity_entry['font'] =label_design['font']
        multiplicity_entry.grid(row=7, column=1, sticky='w', padx=2, pady=2)
    
    def show_cal_tab(self,parent): 
        """ Creates widgets for fd mode in second tab"""

        common_frame = ttk.Frame(parent)
        common_frame.grid(row=0, column=0, sticky='nsew')

        sub_frame = ttk.Frame(parent)
        sub_frame.grid(row=1, column=0, sticky='nsew')

        self.shape = tk.Label(common_frame,text="Box Shape", justify='left', bg=label_design['bg'], fg=label_design['fg'])
        self.shape['font'] = label_design['font']
        self.shape.grid(row=0, column=0, sticky='nsew', padx=10, pady=4)

        def pick_frame(*_):
            for widget in sub_frame.winfo_children():
                widget.destroy()  
            self.octopus_frame(sub_frame)
            self.oct_simbox(sub_frame)               
            
        self.box_shape = ttk.Combobox(common_frame, textvariable= self._var['shape'], value =self.default_para['shape']['values'])
        self.box_shape['font'] = label_design['font']
        self.box_shape.bind("<<ComboboxSelected>>", pick_frame)
        self.box_shape['state'] = 'readonly'
        self.box_shape.grid(row=0, column=1, sticky='w', padx=10, pady=2)

        self.label_sp = tk.Label(common_frame,text="Spacing (in Ang)",bg=label_design['bg'], fg=label_design['fg'])
        self.label_sp['font'] = label_design['font']
        self.label_sp.grid(row=1, column=0,  sticky='nsew', padx=6, pady=4)

        self.entry_sp = Decimalentry(common_frame,textvariable= self._var['h'])  
        self.entry_sp['font'] = label_design['font']
        self.entry_sp.grid(row=1, column=1,  sticky='nsew', padx=6, pady=2)

        self.spin = tk.Label(common_frame,text="Spin Polarisation",bg=label_design['bg'], fg=label_design['fg'])
        self.spin['font'] = label_design['font']
        self.spin.grid(row=2, column=0, sticky='nsew', padx=6, pady=4)
   
        self.spinpol = ttk.Combobox(common_frame, textvariable= self._var['spinpol'], value = self.default_para['spinpol']['values'])
        #self.spinpol.current(0)
        self.spinpol['font'] = label_design['font']
        self.spinpol['state'] = 'readonly'
        self.spinpol.grid(row=2, column=1, padx=6, pady=2) 

        pick_frame()

    def octopus_frame(self,parent): 
        """Creates widgets in calc_details tab/Octopus""" 

        oct_frame = ttk.Frame(parent, borderwidth=2)
        oct_frame.grid(row=1, column=0, sticky='nsew')
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.expt_label = tk.Label(oct_frame,text="Experimental Features",bg=label_design['bg'], fg=label_design['fg'])
        self.expt_label['font'] = label_design['font']
        self.expt_label.grid(row=2, column=0, sticky='w', padx=2, pady=6)
       

        def pick_expt(*_):
            if self._var['expt'].get() == "yes":
                self.cb1.config(value = sum(self.default_para['pseudo']['values']['expt_yes'], []))
                self.cb1.set("--choose option--")
            elif self._var['expt'].get() == "no":
                self.cb1.config(value = self.default_para['pseudo']['values']['expt_no'])
                self.cb1.set("--choose option--")

        self.expt_combo = ttk.Combobox(oct_frame,width= 10, textvariable= self._var['expt'], value = self.default_para['expt']['values'])
        self.expt_combo['font'] =label_design['font']
        self.expt_combo.bind("<<ComboboxSelected>>", pick_expt)
        self.expt_combo['state'] = 'readonly'
        self.expt_combo.grid(row=2, column=1, sticky='we', padx=2, pady=6)

        self.lb1 = tk.Label(oct_frame,text="Pseudo Potential",bg=label_design['bg'], fg=label_design['fg'])
        self.lb1['font'] = label_design['font']
        self.lb1.grid(row=3, column=0, sticky='w', padx=2, pady=6)

    
        def pick_xc(*_):
            if self._var['expt'].get() == "no":
                self.x_entry.config(value = self.default_para['x']['values']['lda_x'])
                self.x_entry.current(0)
                self.c_entry.config(value = self.default_para['c']['values']['lda_c'])
                self.c_entry.current(0)

            elif self._var['expt'].get() == "yes":

                if self._var['pseudo'].get() in self.default_para['pseudo']['values']['expt_yes'][1]:
                    self.x_entry.config(value = self.default_para['x']['values']['pbe_x'])
                    self.x_entry.current(0)
                    self.c_entry.config(value = self.default_para['c']['values']['pbe_c'])
                    self.c_entry.current(0)
                elif self._var['pseudo'].get() in self.default_para['pseudo']['values']['expt_yes'][0]:
                    self.x_entry.config(value = self.default_para['x']['values']['lda_x'])
                    self.x_entry.current(0)
                    self.c_entry.config(value = self.default_para['c']['values']['lda_c'])
                    self.c_entry.current(0)

                else:
                    self._var['x'].set('')
                    self._var['c'].set('')
                    self.x_entry.config(value = '')
                    self.c_entry.config(value = '')

        self._var['expt'].trace_add('write', pick_xc)

        self.cb1 = ttk.Combobox(oct_frame,width= 10, textvariable= self._var['pseudo'])
        self.cb1['font'] = label_design['font']
        self.cb1.bind("<<ComboboxSelected>>", pick_xc)
        self.cb1['state'] = 'readonly'
        self.cb1.set("--choose option--")
        self.cb1.grid(row=3, column=1, sticky='we', padx=2, pady=6)

        oct_xc_frame = ttk.Frame(oct_frame)
        oct_xc_frame.grid(row = 5, column=0, columnspan=4)
       
        self.Frame2_note = tk.Label(oct_frame,text="Exchange Correlation",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=4, column=0, sticky='w', padx=4, pady=6)
        
        x_label = tk.Label(oct_xc_frame,text="x",fg="black")
        x_label['font'] = label_design['font']
        x_label.grid(row=0, column=1, sticky='we', padx=2, pady=4)

        self.x_entry = ttk.Combobox(oct_xc_frame, textvariable= self._var['x'])
        self.x_entry['font'] = label_design['font']
        self.x_entry.grid(row=0, column=2, sticky='we', padx=2, pady=4)
        self.x_entry['state'] = 'readonly'

        c_label = tk.Label(oct_xc_frame,text="c",fg="black")
        c_label['font'] = label_design['font']
        c_label.grid(row=0, column=3, sticky='we', padx=2, pady=4)

        self.c_entry = ttk.Combobox(oct_xc_frame, textvariable= self._var['c'])
        self.c_entry['font'] = label_design['font']
        self.c_entry.grid(row=0, column=4, sticky='we', padx=2, pady=4)
        self.c_entry['state'] = 'readonly'  

    
        self.Frame2_note = tk.Label(oct_frame,text="Eigen Solver",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=7, column=0, sticky='w', padx=2, pady=6)

        self.entry_pol_x = ttk.Combobox(oct_frame, textvariable= self._var['eigen'], value = self.default_para['eigen']['values'])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = label_design['font']
        self.entry_pol_x['state'] = 'readonly'
        self.entry_pol_x.grid(row=7, column=1, sticky='w', padx=2, pady=6) 

        self.label_extra_states = tk.Label(oct_frame,text="Number of Extra States",bg=label_design['bg'], fg=label_design['fg'])
        self.label_extra_states['font'] = label_design['font']
        self.label_extra_states.grid(row=8, column=0, sticky='w', padx=2, pady=6)

        self.entry_extra_states = Onlydigits(oct_frame, textvariable= self._var['extra_states'])
        # self.entry_extra_states.current(0)
        self.entry_extra_states['font'] = label_design['font']
        self.entry_extra_states.grid(row=8, column=1, sticky='w', padx=2, pady=6)              

        pick_expt()

    def oct_simbox(self, parent):
        self.oct_simb = ttk.Frame(parent)
        self.oct_simb.grid(row=2, column=0, sticky='w')

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        j= font.Font(family ='Courier', size=20,weight='bold')
        k= font.Font(family ='Courier', size=40,weight='bold')
        l= font.Font(family ='Courier', size=15,weight='bold')

        self.subheading = tk.Label(self.oct_simb,text="Simulation Box",fg='blue')
        self.subheading['font'] =  myFont
        self.subheading.grid(row=0, column=0, sticky='w')

        self.boxlabel = tk.Label(self.oct_simb,text="Simulation box unit",bg=label_design['bg'], fg=label_design['fg'])
        self.boxlabel['font'] = label_design['font']
        self.boxlabel.grid(row=1, column=0, sticky='w', padx=2, pady=4)        
        
        unit = ttk.Combobox(self.oct_simb, width=8, textvariable= self._var['unit_box'], value = self.default_para['unit_box']['values'])
        unit.current(0)
        unit['font'] = label_design['font']
        unit.grid(row=1, column=1, sticky='w', padx=12, pady=2)
        unit['state'] = 'readonly'

        # self.oct_minsph_frame(self.oct_simb)
        if self._var['shape'].get() == "parallelepiped":
            self.oct_ppl_frame(self.oct_simb)
            # self.box1.grid(row=12, column=0, sticky='w', padx=2, pady=4)
                
        elif self._var['shape'].get() == "minimum": 
            self.oct_minsph_frame(self.oct_simb)
            # self.box1.grid(row=12, column=0, sticky='w', padx=2, pady=4)
                
        elif self._var['shape'].get() == "sphere":
            self.oct_minsph_frame(self.oct_simb)
            # self.box1.grid(row=12, column=0, sticky='w', padx=2, pady=4)
                
        elif self._var['shape'].get() == "cylinder": 
            self.oct_cyl_frame(self.oct_simb)
        # return oct_simb
  
    def oct_ppl_frame(self,parent):

        oct_ppd_frame = ttk.Frame(parent)
        oct_ppd_frame.grid(row=4, column=0, columnspan=3)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
       
        self.note = tk.Label(oct_ppd_frame,text="Length of Box (lx, ly, lz)",bg=label_design['bg'], fg=label_design['fg'])
        self.note['font'] = label_design['font']
        #self.note.place(x=10,y=40)
        self.note.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        #self.entry1 = tk.Entry(self.Frame3,width= 5, textvariable= self._var['lx'])
        self.entry1 = Decimalentry(oct_ppd_frame, width =5, textvariable = self._var['lx'])
        self.entry1['font'] = label_design['font']
        #self.entry1.place(x=220,y=40)
        self.entry1.grid(row=4, column=1, sticky='w', padx=8, pady=2)

        #self.entry2 = tk.Entry(self.Frame3, width= 5, textvariable= self._var['ly'])
        self.entry2 = Decimalentry(oct_ppd_frame,width= 5, textvariable= self._var['ly'])
        self.entry2['font'] = label_design['font']
        #self.entry2.place(x=280,y=40)
        self.entry2.grid(row=4, column=2, sticky='w', padx=16, pady=2)

        #self.entry3 = tk.Entry(self.Frame3,width=5, textvariable= self._var['lz'])
        self.entry3 = Decimalentry(oct_ppd_frame, width= 5, textvariable= self._var['lz'])
        self.entry3['font'] = label_design['font']
        #self.entry3.place(x=340,y=40)
        self.entry3.grid(row=4, column=3, sticky='w', padx=16, pady=2)
                  
    def oct_minsph_frame(self,parent):
  
        ocms_frame = ttk.Frame(parent, borderwidth=2)
        ocms_frame.grid(row=4, column=0)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        self.note = tk.Label(ocms_frame,text="Radius of Box",bg=label_design['bg'], fg=label_design['fg'])
        self.note['font'] = label_design['font']
        self.note.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        self.entryr = Decimalentry(ocms_frame, textvariable= self._var['r'], width= 5)
        self.entryr['font'] = label_design['font']
        self.entryr.grid(row=4, column=1, sticky='w', padx=12, pady=2)

    def oct_cyl_frame(self, parent):

        occyl_frame = ttk.Frame(parent, borderwidth=2)
        occyl_frame.grid(row=4, column=0)

        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.note1 = tk.Label(occyl_frame,text="Length of Cylinder",bg=label_design['bg'], fg=label_design['fg'])
        self.note1['font'] = label_design['font']
        self.note1.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        #self.entryl = tk.Entry(self.Frame3, textvariable= self._var['l'], width= 5)
        self.entryl = Decimalentry(occyl_frame, textvariable= self._var['l'], width= 5)
        self.entryl['font'] = label_design['font']
        self.entryl.grid(row=4, column=1, sticky='w', padx=12, pady=2)
 
        self.note2 = tk.Label(occyl_frame,text="Radius of Cylinder",bg=label_design['bg'], fg=label_design['fg'])
        self.note2['font'] = label_design['font']
        self.note2.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        #self.entrycr = tk.Entry(self.Frame3, textvariable= self._var['r'], width= 5)
        self.entrycr = Decimalentry(occyl_frame, textvariable= self._var['r'], width= 5)
        self.entrycr['font'] = label_design['font']
        self.entrycr.grid(row=6, column=1, sticky='w', padx=12, pady=2)


    def show_advance_tab(self, parent):
        """ Creates the widgets for Advanced info tab"""

        oct_conv = ttk.Frame(parent, borderwidth=2)
        oct_conv.grid(row=0, column=0, sticky = 'w')
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.label_title = tk.Label(oct_conv, text="SCF Convergence for Octopus    ", fg="blue")
        self.label_title['font'] =  myFont
        self.label_title.grid(row=0, column=0, sticky='w', padx=2, pady=4)
      
        self.label_maxiter = tk.Label(oct_conv, text="Maximum SCF iteration",bg=label_design['bg'], fg=label_design['fg'])
        self.label_maxiter['font'] = label_design['font']
        self.label_maxiter.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        self.entry_maxiter = Onlydigits(oct_conv,textvariable= self._var['maxiter'])
        self.entry_maxiter['font'] = label_design['font']
        self.entry_maxiter.grid(row=2, column=1, sticky='w', padx=2, pady=2)

        self.label_conv_en = tk.Label(oct_conv,text="Energy(in au)",bg=label_design['bg'], fg=label_design['fg'])
        self.label_conv_en['font'] = label_design['font']
        self.label_conv_en.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        self.entry_conv_en = tk.Entry(oct_conv, textvariable= self._var['conv_energy'])
        self.entry_conv_en['font'] = label_design['font']
        self.entry_conv_en.grid(row=4, column=1, sticky='w', padx=2, pady=2)
 
        self.label_absconv = tk.Label(oct_conv,text="Absolute Convergence",fg="blue")
        self.label_absconv['font'] = label_design['font']
        self.label_absconv.grid(row=8, column=0, sticky='w', padx=2, pady=4)

        self.label_absden = tk.Label(oct_conv,text="Density",bg=label_design['bg'], fg=label_design['fg'])
        self.label_absden['font'] = label_design['font']
        self.label_absden.grid(row=10, column=0, sticky='w', padx=2, pady=4)

        self.entry_absden = tk.Entry(oct_conv,textvariable= self._var['abs_density'])
        self.entry_absden['font'] = label_design['font']
        self.entry_absden.delete(0,tk.END)
        self.entry_absden.insert(0,"0.0")
        self.entry_absden.grid(row=10, column=1, sticky='w', padx=2, pady=2)
     
        self.label_absev = tk.Label(oct_conv,text="Sum of eigen values",bg=label_design['bg'], fg=label_design['fg'])
        self.label_absev['font'] = label_design['font']
        self.label_absev.grid(row=12, column=0, sticky='w', padx=2, pady=4)

        self.entry_absev = tk.Entry(oct_conv,textvariable= self._var['abs_eigen'])
        self.entry_absev['font'] = label_design['font']
        self.entry_absev.delete(0,tk.END)
        self.entry_absev.insert(0,"0.0")
        self.entry_absev.grid(row=12, column=1, sticky='w', padx=2, pady=2)
    
        self.label_relconv = tk.Label(oct_conv,text="Relative Convergence",fg="blue")
        self.label_relconv['font'] = label_design['font']
        self.label_relconv.grid(row=14, column=0, sticky='w', padx=2, pady=4)

        self.label_relden = tk.Label(oct_conv,text="Density",bg=label_design['bg'], fg=label_design['fg'])
        self.label_relden['font'] = label_design['font']
        self.label_relden.grid(row=16, column=0, sticky='w', padx=2, pady=4)

        self.entry_relden = tk.Entry(oct_conv,textvariable= self._var['rel_density'])
        self.entry_relden['font'] = label_design['font']
        self.entry_relden.delete(0,tk.END)
        self.entry_relden.insert(0,"1.0e-4")
        self.entry_relden.grid(row=16, column=1, sticky='w', padx=2, pady=2)
        
        self.label_relev = tk.Label(oct_conv, text="Sum of eigen values",bg=label_design['bg'], fg=label_design['fg'])
        self.label_relev['font'] = label_design['font']
        self.label_relev.grid(row=18, column=0, sticky='w', padx=2, pady=4)

        self.entry_relev = tk.Entry(oct_conv, textvariable= self._var['rel_eigen'])
        self.entry_relev['font'] = label_design['font']
        self.entry_relev.delete(0,tk.END)
        self.entry_relev.insert(0,"0.0")
        self.entry_relev.grid(row=18, column=1, sticky='w', padx=2, pady=2)

        self.other_scf = tk.Label(oct_conv,text="Other Scf Parameters",fg="blue")
        self.other_scf['font'] = label_design['font']
        self.other_scf.grid(row=19, column=0, sticky='w', padx=2, pady=4)

        self.label_mixing = tk.Label(oct_conv,text="Mixing",bg=label_design['bg'], fg=label_design['fg'])
        self.label_mixing['font'] = label_design['font']
        self.label_mixing.grid(row=20, column=0, sticky='w', padx=2, pady=4)

        self.entry_mixing = Decimalentry(oct_conv, textvariable= self._var['mixing'])
        self.entry_mixing['font'] = label_design['font']
        self.entry_mixing.grid(row=20, column=1, sticky='w',padx=2, pady=2)

        self.label_smear = tk.Label(oct_conv, text="Smearing (eV)",bg=label_design['bg'], fg=label_design['fg'])
        self.label_smear['font'] = label_design['font']
        self.label_smear.grid(row=22, column=0, sticky='w', padx=2, pady=4)

        self.entry_smear = Decimalentry(oct_conv, textvariable= self._var['smear']) 
        self.entry_smear['font'] = label_design['font']
        self.entry_smear.grid(row=22, column=1, sticky='w', padx=2, pady=2)

        self.label_smearfunc = tk.Label(oct_conv,text="Smearing Function",bg=label_design['bg'], fg=label_design['fg'])
        self.label_smearfunc['font'] = label_design['font']
        self.label_smearfunc.grid(row=24, column=0, sticky='w', padx=2, pady=4)

        self.entry_smearfunc = ttk.Combobox(oct_conv, textvariable= self._var['smearfn'], value = self.default_para['smearfn']['values'])
        self.entry_smearfunc.current(0)
        self.entry_smearfunc['font'] = label_design['font']
        self.entry_smearfunc['state'] = 'readonly'
        self.entry_smearfunc.grid(row=24, column=1, sticky='w', padx=2, pady=2)


    def create_input_widgets(self) -> None:
        self.show_system_tab(self.gspage.system_frame)
        self.show_cal_tab(self.gspage.calculation_frame)
        self.show_advance_tab(self.gspage.advanced_info_frame)

    def get_parameters(self) -> dict:

        from litesoph.utilities.units import au_to_eV

        inp_dict_oct = {
            "engine": "octopus",
            "CalculationMode": "gs",
            "UnitsOutput": "ev_angstrom",
            "ExperimentalFeatures": self._var['expt'].get(),
            "XCFunctional": [self._var['x'].get(),self._var['c'].get()],
            "PseudopotentialSet" : self._var['pseudo'].get(),
            "Spacing": str(self._var['h'].get())+ '*angstrom',
            "SpinComponents": self._var['spinpol'].get(),
            "ExcessCharge": self._var['charge'].get(),
            "MaximumIter": self._var['maxiter'].get(),
            "ConvEnergy": self._var['conv_energy'].get(),
            "ConvAbsDens": self._var['abs_density'].get(),
            "ConvAbsEv": self._var['abs_eigen'].get(),
            "ConvRelDens": self._var['rel_density'].get(),
            "ConvRelEv": self._var['rel_eigen'].get(),
            "Eigensolver":self._var['eigen'].get(),
            "Smearing":self._var['smear'].get(),
            "SmearingFunction":self._var['smearfn'].get(),
            "Mixing":self._var['mixing'].get(),
            "ExtraStates" : self._var['extra_states'].get()
                    }                  


        if self._var['shape'].get() in ['minimum','sphere']:
            inp_dict_oct["BoxShape"]={"name":self._var['shape'].get(),
                        "param":{'Radius':str(self._var['r'].get())+'*angstrom'}}
        elif self._var['shape'].get() == 'cylinder':
            inp_dict_oct["BoxShape"]={"name":self._var['shape'].get(),
                        "param":{'Radius':str(self._var['r'].get())+'*angstrom',
                        'Xlength':str(self._var['l'].get()/2)+'*angstrom'}}
        elif self._var['shape'].get() == 'parallelepiped':
            inp_dict_oct["BoxShape"]={"name":self._var['shape'].get(),
                        "param":{'LSize':[[
                            str(self._var['lx'].get()/2)+'*angstrom',
                            str(self._var['ly'].get()/2)+'*angstrom',
                            str(self._var['lz'].get()/2)+'*angstrom']]}}       
        return inp_dict_oct