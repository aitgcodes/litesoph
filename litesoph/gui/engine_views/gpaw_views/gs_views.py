import tkinter as tk
from tkinter import ttk
from tkinter import font
from litesoph.gui import images
from litesoph.gui.input_validation import Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15

from litesoph.gui.engine_views import EngineViews
from litesoph.simulations.models import GpawModel


class GpawGSPage(EngineViews):

    def __init__(self, gspage) -> None:
        
        self.gspage = gspage
        #self._var = self.gspage._var
        self.default_para = GpawModel.ground_state

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

        def pick_box(e):

            if task.get() == 'nao':
                sub_task.config(value = self.default_para['basis']['values'])
                sub_task.set(self.default_para['basis']['default_value'])
            elif task.get() == "pw" or "fd":
                sub_task.config(value = '')
                sub_task.set('')


        task = ttk.Combobox(mode_frame, textvariable = self._var['mode'], values= self.default_para['mode']['values'])
        task['font'] = label_design['font']
        task.grid(row=2, column= 1, sticky='w', padx=2, pady=2)
        task.bind("<<ComboboxSelected>>", pick_box)
        task['state'] = 'readonly'
    
        self.basis = tk.Label(mode_frame, text="Basis",bg=label_design['bg'], fg=label_design['fg'])
        self.basis['font'] = label_design['font']
        self.basis.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        sub_task = ttk.Combobox(mode_frame, textvariable= self._var['basis'], value = self.default_para['basis']['values'])
        sub_task['font'] = label_design['font']
        sub_task.grid(row=4, column=1, sticky='w', padx=2, pady=2)
        sub_task['state'] = 'readonly'

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
        """ Creates widgets in calc_details tab for nao/pw"""

        gp_frame = ttk.Frame(parent, borderwidth=2)
        gp_frame.grid(row=0, column=0, sticky='w')
        myFont = font.Font(family='Helvetica', size=10, weight='bold')

        self.Frame2_note = tk.Label(gp_frame,text="LITESOPH input for Gpaw        ",fg="blue")
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=0, column=0, sticky='w', padx=2, pady=4)

        self.Frame2_note = tk.Label(gp_frame,text="Exchange Correlation",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        self.gpxc = ttk.Combobox(gp_frame, textvariable= self._var['xc'], value = self.default_para['xc']['values'])
        self.gpxc.current(0)
        self.gpxc['font'] = label_design['font']
        self.gpxc['state'] = 'readonly'
        self.gpxc.grid(row=2, column=1, sticky='w', padx=2, pady=2)

        self.spin = tk.Label(gp_frame,text="Spin Polarisation",bg=label_design['bg'], fg=label_design['fg'])
        self.spin['font'] = label_design['font']
        self.spin.grid(row=4, column=0, sticky='w', padx=2, pady=4)
   
        self.spinpol = ttk.Combobox(gp_frame, textvariable= self._var['spinpol'], value = self.default_para['spinpol']['values'])
        self.spinpol.current(0)
        self.spinpol['font'] = label_design['font']
        self.spinpol['state'] = 'readonly'
        self.spinpol.grid(row=4, column=1, padx=2, pady=2)

        self.nb = tk.Label(gp_frame,text="Number of Bands",bg=label_design['bg'], fg=label_design['fg'])
        self.nb['font'] = label_design['font']
        self.nb.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_bands = Onlydigits(gp_frame,textvariable= self._var['nbands'])
        self.entry_bands['font'] = label_design['font']
        self.entry_bands.grid(row=6, column=1, sticky='w', padx=2, pady=2)
      
        self.label_sp = tk.Label(gp_frame,text="Spacing (in Ang)",bg=label_design['bg'], fg=label_design['fg'])
        self.label_sp['font'] = label_design['font']
        self.label_sp.grid(row=8, column=0, sticky='w', padx=2, pady=4)

        self.entry_sp = Decimalentry(gp_frame,textvariable= self._var['h'])
        self.entry_sp['font'] =label_design['font']
        self.entry_sp.grid(row=8, column=1, sticky='w', padx=2, pady=2)

        self.Frame2_note = tk.Label(gp_frame,text="Vacuum size (in Ang)",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=10, column=0, sticky='w', padx=2, pady=4)

        self.entry_vac = Decimalentry(gp_frame,textvariable= self._var['vacuum'])
        self.entry_vac['font'] = label_design['font']
        self.entry_vac.grid(row=10, column=1, sticky='w', padx=2, pady=2)

    def show_advance_tab(self, parent):
        # parent.grid_remove()
        gp_conv = ttk.Frame(parent, borderwidth=2)
        gp_conv.grid(row=0, column=0, sticky='w')

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        
        self.label_pol_z = tk.Label(gp_conv, text="SCF Convergence for Gpaw       ", fg="blue")
        self.label_pol_z['font'] =  myFont
        self.label_pol_z.grid(row=0, column=0, sticky='w', padx=2, pady=4)
 
        self.label_pol_z = tk.Label(gp_conv, text="Maximum SCF iteration",bg=label_design['bg'], fg=label_design['fg'])
        self.label_pol_z['font'] =label_design['font']
        self.label_pol_z.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        #entry = ttk.Entry(self.Frame1,textvariable= self._var['maxiter'])
        entry = Onlydigits(gp_conv,textvariable= self._var['maxiter'])
        entry['font'] = label_design['font']
        entry.grid(row=2, column=1, sticky='w', padx=2, pady=2)

        self.Frame2_note = tk.Label(gp_conv,text="Energy(in au)",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        self.entry_ener = tk.Entry(gp_conv, textvariable= self._var['energy'])
        #self.entry_ener = Validatedconv(self.Frame1)
        self.entry_ener['font'] = label_design['font']
        self.entry_ener.grid(row=4, column=1, sticky='w', padx=2, pady=2)

        self.label_proj = tk.Label(gp_conv,text="Density",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        #self.label_proj.place(x=10,y=10)
        self.label_proj.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_proj = tk.Entry(gp_conv,textvariable= self._var['density'])
        self.entry_proj['font'] = label_design['font']
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1.0e-4")
        #self.entry_proj.place(x=280,y=10)
        self.entry_proj.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        self.label_proj = tk.Label(gp_conv,text="eigenstates",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        #self.label_proj.place(x=10,y=10)
        self.label_proj.grid(row=8, column=0, sticky='w', padx=2, pady=4)

        self.entry_proj = tk.Entry(gp_conv,textvariable= self._var['eigenstate'])
        self.entry_proj['font'] = label_design['font']
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1.0e-4")
        #self.entry_proj.pl]ace(x=280,y=10)
        self.entry_proj.grid(row=8, column=1, sticky='w', padx=2, pady=2)
    
        self.bdocc = tk.Label(gp_conv,text="Band Occupancy",bg=label_design['bg'], fg=label_design['fg'])
        self.bdocc['font'] = label_design['font']
        #self.bdocc.place(x=10,y=310)
        self.bdocc.grid(row=10, column=0, sticky='w', padx=2, pady=4)

        self.occ = ttk.Combobox(gp_conv, textvariable= self._var['bands'], value = self.default_para['bands']['values'])
        self.occ.current(0)
        self.occ['font'] = label_design['font']
        #self.occ.place(x=280,y=310)
        self.occ['state'] = 'readonly'
        self.occ.grid(row=10, column=1, sticky='w', padx=2, pady=2)

        self.lb2 = tk.Label(gp_conv,text="Smearing Function",bg=label_design['bg'], fg=label_design['fg'])
        self.lb2['font'] = label_design['font']
        #self.lb2.place(x=10,y=110)
        self.lb2.grid(row=12, column=0, sticky='w', padx=2, pady=4)

        self.entry_pol_x = ttk.Combobox(gp_conv, textvariable= self._var['smearfn'], value = self.default_para['smearfn']['values'])
        self.entry_pol_x.current(0)
        self.entry_pol_x['font'] = label_design['font']
        #self.entry_pol_x.place(x=280,y=110)
        self.entry_pol_x['state'] = 'readonly'
        self.entry_pol_x.grid(row=12, column=1, sticky='w', padx=2, pady=2)

        self.label_proj = tk.Label(gp_conv, text="Smearing (eV)",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        #self.label_proj.place(x=260,y=60)
        self.label_proj.grid(row=14, column=0, sticky='w', padx=2, pady=4)

        #self.entry_proj = tk.Entry(self.Frame2, width= 7,textvariable= self._var['smear'])
        self.entry_sm = Decimalentry(gp_conv, width= 7, textvariable= self._var['smear']) 
        self.entry_sm['font'] = label_design['font']
        #self.entry_sm.place(x=360,y=60)
        self.entry_sm.grid(row=14, column=1, sticky='w', padx=2, pady=2)

    def create_input_widgets(self) -> None:
        self.show_system_tab(self.gspage.Frame1_sub)
        self.show_cal_tab(self.gspage.Frame2_sub)
        self.show_advance_tab(self.gspage.Frame3_sub)

    def get_parameters(self) -> dict:
        from litesoph.utilities.units import au_to_eV
        inp_dict_gp = {
            'mode': self._var['mode'].get(),
            'xc': self._var['xc'].get(),
            'vacuum': self._var['vacuum'].get(),
            'occupations':{'name': self._var['smearfn'].get(),
                            'width': self._var['smear'].get()},
            'basis':{'default': self._var['basis'].get()},
            'h': self._var['h'].get(),
            'nbands' : self._var['nbands'].get(),
            'charge' : self._var['charge'].get(),
            'spinpol' : self._var['spinpol'].get(), 
            'multip' : self._var['multip'].get(), 
            'convergence': {'energy' : self._var['energy'].get() * round(au_to_eV,2),  # eV / electron f'{x: .2e}'
                        'density' :  self._var['density'].get(),
                        'eigenstates': self._var['eigenstate'].get(),  # eV^2
                        'bands' : self._var['bands'].get()}, 
            'maxiter' : self._var['maxiter'].get(),
            'box': self._var['shape'].get(),
            'smearing_func':self._var['smearfn'].get(),
            'properties': 'get_potential_energy()',
            'engine':'gpaw'
                    } 

        if self._var['basis'].get() == '':
            inp_dict_gp['basis']={}

        if self._var['mode'].get() == 'nao':
            inp_dict_gp['mode']='lcao'

        if self._var['nbands'].get() == '':
            inp_dict_gp['nbands']= None

        return inp_dict_gp