import tkinter as tk
from tkinter import messagebox
import copy
from litesoph.gui import design
from litesoph.common import models as m
from litesoph.gui.utils import dict2string

class LaserDesignController:

    def __init__(self, app, view, 
                        td_param:dict, 
                        laser_data:dict):
        """ td_param: GUI view inputs"""

        # Data extracted from TD page
        self.td_data = td_param  # GUI inputs extracted
        self.laser_info = m.LaserInfo(laser_data)
        self.main_window = app.main_window
        self.view = view
        self.focus = None
        self.assign_laser_profile_time()

    def assign_laser_profile_time(self):
        """Sets td simulation time to laser profile time(in as)"""
        time_step = self.td_data.get('time_step')
        num_steps = self.td_data.get('number_of_steps')
        self.total_time = float(time_step)* num_steps

    def bind_events_and_update_default_view(self):
        # TODO: update these event bindings

        self.main_window.bind_all('<<AddLaser>>', self._on_add_laser)
        self.main_window.bind_all('<<EditLaser>>', self._on_edit_laser)
        self.main_window.bind_all('<<RemoveLaser>>', self._on_remove_laser)
        self.main_window.bind_all('<<PlotLaser>>', self._on_plotting)
        self.main_window.bind_all('<<SelectLaser&UpdateView>>', self._on_select_laser)

        # Collecting exp_type from td_data passed from TDPage
        # TODO: decide on to retain previous exp_type sets
        exp_type = self.td_data.get('exp_type')
        if exp_type == "State Preparation":
            self.view.inp.widget["pump-probe_tag"].configure(state = 'disabled')
            self.view.inp.fields["pump-probe_tag"]["visible"] = False
        
        # if hasattr(self.task_view, 'set_parameters'):
        #     self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def get_laser_design_model(self, laser_input:dict):
        """Collects inputs to compute laser parameters 
        and returns LaserDesignPlotModel object"""

        from litesoph.utilities.units import as_to_au, au_to_fs
        laser_total_time_fs = self.total_time*as_to_au*au_to_fs
        self.laser_design = m.LaserDesignPlotModel(laser_inputs = [laser_input],
                laser_profile_time= laser_total_time_fs)
        
        # TODO: Make this multiple laser input dictionaries consistent with LaserDesignPlotModel        
        self.pulse_info = self.laser_design.get_laser_param_pulse(laser_input= laser_input)
        # self.pulse_list = self.laser_design.get_laser_pulse_list()    
        return self.laser_design
   
    def _on_add_laser(self, *_):  
        """On add laser button:
        \n Checks the validation for time-origin for state-preparation/pump-probe laser inputs
        \n Proceeds to append the lasers
        """
        # GUI inputs for laser page
        laser_gui_inp = self.view.inp.get_values()

        laser_gui_inp = {k : laser_gui_inp[k] for k in laser_gui_inp if laser_gui_inp[k] is not None}
        add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_gui_inp))
        if add_check:
            self.add_lasers_and_update_tree()
        else:
            pass

    def add_lasers_and_update_tree(self, index=None):
        # GUI inputs for laser page
        laser_gui_inp = self.view.get_parameters()
        # Laser design model
        laser_design_model = self.get_laser_design_model(laser_gui_inp)
        pulse = laser_design_model.pulse_info

        tag = laser_gui_inp.get('tag', None)
        if tag is None:
            _tag = 'State Preparation'
        else:
            _tag = tag
        self.laser_info.add_laser(system_key=_tag, laser_param= laser_gui_inp, index=index)
        self.laser_info.add_pulse(system_key=_tag, laser_pulse=pulse, index=index)
        self.update_labels_on_tree()  

    def _on_edit_laser(self, *_):
        """On Edit Button:
         Updates the laser info data"""

        if self.focus is not None:
            (parent, index) = self.focus
        else:
            messagebox.showerror(message="Select laser first.") 
            return

        # GUI inputs for laser page
        laser_gui_inp = self.view.inp.get_values()

        # TODO: Filter out the dict to modify the message
        add_check = messagebox.askokcancel(title="Laser to be added", message=dict2string(laser_gui_inp))
        if add_check:
            self.add_lasers_and_update_tree(index)
            self.focus = None
        else:
            pass

    def populate_laser_details(self, tag:str, index:int):        
        lasers = self.laser_info.data[tag]['lasers']
        laser_selected = lasers[index]
        # TODO: replace set_parameters
        self.view.set_parameters(laser_selected)
        # self.view.inp.init_widgets(var_values=laser_selected)

    def _on_remove_laser(self, *_):
        """ Removes the laser info data"""

        if self.focus is not None:
            (parent, index) = self.focus
        else:
            messagebox.showerror(message="Select laser first.")
            return
        remove_check = messagebox.askyesno(message="This laser:{} will be removed. Click OK to continue?".format(index+1))
        if remove_check:
            self.laser_info.remove_info(system_key=parent, laser_index=index)
            self.update_labels_on_tree()
            self.focus = None
        else:
            pass     

    def _on_select_laser(self, *_):
        """ Populates the selected laser entries"""

        item = None
        if len(self.view.tree.selection())>0:
            item = self.view.tree.selection()[0]
        
        if item is not None:
            label = str(self.view.tree.item(item,"text"))
            parent = str(self.view.tree.parent(item))
            try:
                index = int(label[-1]) -1
                self.focus = (parent, index)
                self.populate_laser_details(tag=parent, index=index)
                return (parent,index)
            except ValueError:
                # Error when the label does not end with an index
                self.focus = None               

    def update_labels_on_tree(self):
        """Method to update treeview"""
        _parents_under_root = self.view.tree.get_children()

        # Clearing treeview for existing parents
        for i, system_name in enumerate(self.laser_info.data.keys()):
            if system_name in _parents_under_root:
                if self.view.tree.get_children(system_name):
                    for child in self.view.tree.get_children(system_name):
                        self.view.tree.delete(child) 
            else:
                # Add the parents if not already present
                self.view.tree.insert('', str(i), str(system_name), text=str(system_name))

        # Attaching child to parent
        for parent in self.view.tree.get_children():
            num_lasers = self.laser_info.get_number_lasers(system_tag= parent)
            laser_labels = get_laser_labels(laser_defined=True, num_lasers= num_lasers)

            if laser_labels is not None:
                for i, label in enumerate(laser_labels):
                    id = self.view.tree.insert('', 'end', text=str(label))
                    self.view.tree.move(id, str(parent), 'end')

    def show_and_update_plot_page(self, *_):
        self.laser_plot_view = design.LaserPlotPage(self.main_window)
        self.update_tree_and_view_on_plot()

    def update_tree_and_view_on_plot(self):
        """Method to update treeview on Plotting page"""
        _parents_under_root = self.laser_plot_view.tree.get_children()

        # Clearing treeview for existing parents
        for i, system_name in enumerate(self.laser_info.data.keys()):
            if len(self.laser_info.data[system_name]['lasers']) > 0:
                if system_name in _parents_under_root:
                    pass
                else:
                    # Add the parents if not already present
                    self.laser_plot_view.tree.insert('', str(i), str(system_name), text=str(system_name))

        if len(self.laser_plot_view.tree.get_children()) == 1:
            self.laser_plot_view.label_delay.grid_remove()
            self.laser_plot_view.entry_delay.grid_remove()

        else:
            self.laser_plot_view.label_delay.grid()
            self.laser_plot_view.entry_delay.grid()
            # self.laser_plot_view.widget_frame.grid()

    def _on_plotting(self, *_):
        """ On Plotting Button: Shows toplevel for plotting
        and updates the binding"""

        if len(self.laser_info.data) > 0:
            self.show_and_update_plot_page()
            self.laser_plot_view.bind('<<PlotLasers>>', self._on_plot_button)
            # self.laser_plot_view.button_plot_w_delay.configure(command=self._on_plot_w_delay_button)           
        else:
            messagebox.showerror(message="Please add lasers to plot.")
            return 

    def _on_plot_button(self, *_):
        """On Plot Button in PlotPage"""
        from litesoph.utilities.units import as_to_au, au_to_fs, fs_to_au

        # bool if Probe is present
        plot_probe = False

        # TODO: Validate number of system selected
        systems_selected = self.laser_plot_view.laser_selected() 
        
        if "Probe" in systems_selected:
            plot_probe = True
        
        if plot_probe is True:
            # TODO: Validate Pump is present or not
            delay_in_fs = self.laser_plot_view._var['delay'].get()
            delay_in_au = float(delay_in_fs)*fs_to_au 

            laser_data_1 = copy.deepcopy(self.laser_info.data['Pump'])
            laser_data_2 = copy.deepcopy(self.laser_info.data['Probe'])

            lasers_pump_probe = list(add_delay_to_lasers(system_1= laser_data_1, 
                                system_2= laser_data_2, delay=delay_in_au)) 

            if len(systems_selected)==1:
                lasers = [lasers_pump_probe[1]]
            else:
                lasers = lasers_pump_probe

        else:
            lasers = []
            for laser_system in systems_selected:
                _lasers = self.extract_laser_param_from_system(laser_system)
                # _lasers = self.extract_laser_param_from_system(laser_system)
                lasers.append(_lasers)

        lasers_to_plot = []
        for laser in lasers:
            lasers_to_plot.extend(laser)

        (time_arr, list_strength_arr) = m.get_time_strength(list_of_laser_params=lasers_to_plot,
                                                laser_profile_time= self.total_time*as_to_au*au_to_fs)
        # TODO: Modify plot method to add tag of laser
        # Add polarization as variable to filter out strengths
        m.plot_laser(time_arr, list_strength_arr)

    def extract_laser_param_from_system(self, laser_system:str):
        """ Specific to LaserPlotPage/ Returns list of laser 
        parameters to plot"""

        pulses = []    
        if laser_system in self.laser_info.data.keys():
            _pulses = self.laser_info.data[laser_system].get('pulses')
            pulses.extend(_pulses)
        laser_sets = extract_lasers_from_pulses(pulses)
        laser_params =[]
        for laser in laser_sets:
            laser_params.append(laser[0])
        return laser_params  

    def create_laser_file(self, fname='laser.dat'):
        'Writes designed laser data to file'
        from litesoph.common.models import write_lasers
        from litesoph.utilities.units import as_to_au, au_to_fs
        lasers = []
        for laser_system in self.laser_info.data.keys():
            _lasers = self.extract_laser_param_from_system(laser_system)
            lasers.extend(_lasers)
        (time_arr, list_strength_arr) = m.get_time_strength(list_of_laser_params=lasers,
            laser_profile_time= self.total_time*as_to_au*au_to_fs
        )
        write_lasers(fname, time_t=time_arr*as_to_au, laser_strengths=list_strength_arr)

def get_laser_labels(laser_defined = False, num_lasers:int= 0):
    if not laser_defined:
        return None
    else:
        if num_lasers > 0:
            laser_label_list = list("laser"+ str(i+1) for i in range(num_lasers))
            return laser_label_list
        else:
            return None
        # else:
        #     raise ValueError("number of Lasers not found.")

def extract_lasers_from_pulses(list_of_pulses:list):
    """ Gets (laser_design,input parameters)
    \n from pulse objects as list of tuples"""
    lasers = []
    if len(list_of_pulses)> 0:
        for pulse in list_of_pulses:
            _laser_design = pulse.laser_design
            _laser_input = pulse.laser_input
            lasers.append((_laser_design, _laser_input))  
    return lasers 

def add_delay_to_lasers(system_1:dict, system_2:dict, delay:float):
    """
    Adds delay between the laser systems and returns the updated ones,
    delay(in au) defined between last laser pulse centre of system 1 and
    first laser pulse centre of system 2

    Delay should be provided in au
    """

    sys1 = system_1
    sys2 = system_2

    pulses_sys1 = sys1['pulses']
    pulses_sys2 = sys2['pulses']

    set_sys1 = extract_lasers_from_pulses(pulses_sys1)
    set_sys2 = extract_lasers_from_pulses(pulses_sys2)

    lasers_sys1 = []
    lasers_sys2 = []

    for laser_set in set_sys1:
        lasers_sys1.append(laser_set[0])

    for laser_set in set_sys2:
        lasers_sys2.append(laser_set[0])

    last_params_sys1 = lasers_sys1[-1]
    first_params_sys2 = lasers_sys2[0]
    # Peak centre of last laser in system 1 (in au)
    time0_ref_1 = last_params_sys1.get('time0')
    # Peak centre of first laser in system 2 (in au)
    time0_ref_2 = first_params_sys2.get('time0')

    # Delay added for Probe system(in au)
    delay_to_add = float(time0_ref_1) + float(delay)- float(time0_ref_2)

    for i,laser_param in enumerate(lasers_sys2):
        _time0 = float(laser_param.get('time0'))
        laser_param['time0'] = _time0 + delay_to_add
    return (lasers_sys1, lasers_sys2)