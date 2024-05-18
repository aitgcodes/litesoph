import tkinter as tk
from tkinter import messagebox
import copy
from litesoph.common.workflow_manager import WorkflowManager
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import InputError, Task, TaskFailed
from litesoph.common.task_data import TaskTypes as tt  
from litesoph.common.workflows_data import WorkflowTypes as wt                                
from litesoph.gui import views as v
from litesoph.common import models as m
from litesoph.gui.models import inputs as inp
from litesoph.gui.utils import dict2string
from litesoph.gui.task_controller import TaskController
from litesoph.gui import design
from litesoph.gui.controllers.laser_page import (LaserDesignController, 
                                                extract_lasers_from_pulses,
                                                add_delay_to_lasers)
from litesoph.utilities.units import as_to_au


class TDPageController(TaskController):

    def __init__(self, workflow_controller, app) -> None:
        super().__init__(workflow_controller, app)
        self.get_laser_data()

    def get_laser_data(self, laser_exists:bool=False):
        """Creates and populates laser data for current calculation.
        Add condition for populating"""

        self.laser_defined = laser_exists
        self.laser_data = {}
        if laser_exists:
            pass

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = tt.RT_TDDFT
        self.task_view = task_view
        self.task = None
        self.current_delay_index = 0
        self.app.proceed_button.config(command=self._on_proceed)

        self.job_sub_page = v.JobSubPage(self.app.task_input_frame)
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")

        self.task_view = self.app.show_frame(task_view, self.task_name)
        self.job_sub_page.back2task.config(command= self.show_task_view)

        self.main_window.bind_all('<<BackonTDPage>>', self._on_back)
        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        self.main_window.bind_all('<<Design&EditLaser>>', self._on_design_edit_laser)    
        self.main_window.bind_all('<<ViewLaserSummary>>', self._on_view_lasers)    
        self.task_view.set_sub_button_state('disable')

        if hasattr(self.task_view, 'set_parameters'):
            default_param = self.update_wf_view_defaults(
                            get_default_func= self.get_td_wf_defaults
                            )
            self.task_view.set_parameters(default_param)

    def get_td_wf_defaults(self):
        if self.workflow_manager.workflow_info._name == wt.PUMP_PROBE:
            wf_dict = {
                "field_type": "Electric Field",
                "exp_type": "Pump-Probe",
            }
        elif self.workflow_manager.workflow_info._name == wt.MASKING:
            wf_dict = {
                "field_type": "Electric Field",
                "exp_type": "State Preparation",
            }
        elif self.workflow_manager.workflow_info._name == wt.MO_POPULATION_TRACKING:
            wf_dict = {
                "field_type": "Electric Field",
                "exp_type": "State Preparation",
            }
        return wf_dict
    
    def set_laser_design_bool(self, bool:bool):
        self.laser_design_bool = bool

    def _on_back(self, *_):
        """ Shows the WorkFlowManager Page"""
        self.workflow_controller.show_workmanager_page()

    def _on_design_edit_laser(self, *_):
        """ On Laser design button, decides on showing LaserDesignPage and binds the widgets"""
        
        try:
            self.task_view_param = self.task_view.get_td_gui_inp()
        except ValueError as e:
            self.task_view_param = None
            messagebox.showerror(message=e)
            return
        
        # Delays attached as a list of delays before proceeding to laser-design 
        if self.task_view_param.get('delay_list', None) is not None:
            self.delay_list = self.task_view_param.get('delay_list')
        # Task specific parameters
        self.task_param = self.task_view.get_parameters()  

        laser_defined = False
        exp_type = self.task_view_param.get('exp_type') 
        laser_defined = validate_laser_defined(laser_data = self.laser_data, exp_type= exp_type) 

        if laser_defined:
            pass
        else:
            if len(self.laser_data) > 0:
                check = messagebox.askyesno(message="Previously designed laser will be removed. \nDo you want to continue?")
                if check:
                    self.laser_data ={}            

        # check = messagebox.askyesno(message= "Laser is already designed.\n Do you want to edit again?")
        # if not check:
        #     return   
        self._on_show_laser_page(show_stored= False)             

    def _on_show_laser_page(self, show_stored:bool, *_):
        """ Assigns LaserDesignController and shows the LaserDesignPage """

        self.laser_view = self.app.show_frame(design.LaserDesignPage)   
        self.view_panel.clear_text()
        self.laser_controller = LaserDesignController(app= self.app, view=self.laser_view, 
                                                    td_param= self.task_view_param,
                                                    laser_data= self.laser_data) 
        
        self.laser_controller.bind_events_and_update_default_view()  
        self.laser_controller.view.button_next.config(command=self.show_tdpage_and_update)
        self.laser_controller.view.button_back.config(command=self.show_task_view)

        self.laser_controller.update_labels_on_tree()

    def show_tdpage_and_update(self, *_):
        from litesoph.gui.models import inputs as inp

        exp_type = self.task_view_param.get('exp_type') 
        self.laser_defined = validate_laser_defined(self.laser_controller.laser_info.data, exp_type) 

        # Showing message before finalise the laser setup if laser defined is True
        if self.laser_defined:
            check = messagebox.askyesno(message= "Do you want to proceed with this laser setup?")
            if check:
                self.task_view.tkraise()
                self.task_view.set_sub_button_state('disable')
                self.task_view.label_msg.grid_remove()
                self.update_laser_on_td_page()
        else:
            if exp_type == 'Pump-Probe':
                pump_bool = self.laser_controller.laser_info.check_laser_exists(system_tag='pump')
                probe_bool = self.laser_controller.laser_info.check_laser_exists(system_tag='probe')
                if not pump_bool:
                    messagebox.showerror(message="Please add one pump laser.")
                    return
                if not probe_bool:
                    messagebox.showerror(message="Please add one probe laser.")
                    return 
            else:
                messagebox.showinfo(message= "Laser is not set. Please add lasers first.")       

    def update_laser_on_td_page(self):
        """ Checks condition for laser designed and updates TDPage view"""  
        from litesoph.gui.design.tdlaser import get_td_laser_w_delay     
    
        # GUI entries from previous td view
        if self.task_view_param is not None:
            td_param_stored = self.task_view_param        
        if self.task_view.inp.variable['exp_type'].get() == "State Preparation":
            pass
        else:
            widget_dict = copy.deepcopy(get_td_laser_w_delay())
            self.task_view.add_widgets(widget_dict)
            _gui_dict = {
                "field_type": td_param_stored.get("field_type"),
                "exp_type" : td_param_stored.get("exp_type")
            }
            _gui_dict.update(self.task_param)
            self.task_view.set_parameters(_gui_dict)

            # TODO: Remove this 
            if self.task_view_param.get('exp_type') == 'Pump-Probe':  
                if self.delay_list:
                    delays = copy.deepcopy(self.delay_list)
                else:
                    delays = [0]
                delays.insert(0, 'No Probe')
                self.task_view.inp.widget["delay_values"].config(values= delays)
                self.task_view.inp.widget["delay_values"].config(state = 'disabled')
                self.task_view.inp.widget["delay_values"].current(0)
                self.task_view.label_delay_entry.grid_remove()
                self.add_task(delays[1:])

        self.task_view.button_view.config(state='active')
        self.task_view.button_save.config(state='active')
        if self.task_view.label_delay_entry:
            self.task_view.label_delay_entry.grid_remove()

        self.task_view.inp.widget["field_type"].config(state = 'disabled')
        self.task_view.inp.widget["exp_type"].config(state = 'disabled')

    def get_laser_details(self):
        details = []
        for i,l_name in enumerate(self.laser_data.keys()):
            l_system = self.laser_data[l_name]
            tag = l_system.get('tag')
            details.append(f'\n{tag}')
            pulses = l_system.get('pulses')
            laser_sets = extract_lasers_from_pulses(pulses)
            laser_params = []

            for laser in laser_sets:
                laser_params.append(laser[1])            

            for laser_index,laser in enumerate(laser_params):
                details.append(f'\n#Laser {laser_index+1}:')
                for key, value in laser.items():                    
                    details.append(f"{key} =  {value}")

        txt =  '\n'.join(details)
        return(txt, details)           

    def add_task(self, delays):
        block_id = self.workflow_manager.current_container.block_id
        step_id = self.workflow_manager.current_container.id
        
        step = step_id+1
        for delay in delays:
            self.workflow_manager.add_task(self.task_name,
                                            block_id,
                                            step_id=step,
                                            dependent_tasks_uuid= self.workflow_controller.get_task_dependencies(self.task_name),
                                            container_cloneable = False)

            td_task_id = self.workflow_manager.containers[step].task_uuid
            dm_task_id = self.workflow_manager.containers[step+1].task_uuid
            self.workflow_manager.add_dependency(dm_task_id, td_task_id)
            step += 1

    def generate_input(self, *_):
        """ Checks experiment type and generate respective inputs"""
        
        self.task_info = self.workflow_manager.current_task_info
        self.task_info.param.clear()
        inp_dict = self.task_view.get_parameters()

        if ((inp_dict['time_step'] % 1) > 1e-8):
            messagebox.showerror(
                'Error', 'Time step has to be an integer'
            )
            return

        if self.task_view.inp.variable['exp_type'].get() == "State Preparation":
            lasers = copy.deepcopy(self.laser_data['State Preparation']['lasers'])
            pulses = copy.deepcopy(self.laser_data['State Preparation']['pulses'])
            laser_sets = extract_lasers_from_pulses(pulses)
            laser_data = []
            for i,laser in enumerate(laser_sets):
                laser_dict = laser[0]
                if laser_dict['type'] == 'delta':
                    # TODO: Please allow floating point time origin for multiple lasers.
                    # #WeWereToStressedForWorkshop
                    t0 = laser[1]['tin'] / as_to_au
                    if ((t0 % 1) > 1e-6):
                        messagebox.showerror(
                            'Error', 'Time origin for delta pulse has to be an integer'
                        )
                        return
                    # laser_dict['time0'] = t0
                laser_dict.update({'mask': lasers[i].get('mask', None)})
                laser_data.append(laser_dict)  
            inp_dict.update({'laser': laser_data})

        # adding masking in pump-probe
        else:
            try:
                delay = self.task_view.inp.variable["delay_values"].get()
            except tk.TclError:
                # lasers
                lasers = copy.deepcopy(self.laser_data['Pump']['lasers'])
                pulses = copy.deepcopy(self.laser_data['Pump']['pulses'])
                laser_sets = extract_lasers_from_pulses(pulses)
                lasers_list = []
                for i,laser in enumerate(laser_sets):
                    laser_dict = laser[0]
                    laser_dict.update({'mask': lasers[i].get('mask', None)})
                    lasers_list.append(laser_dict)  
                delay = "no_probe"
            else:
                pump_lasers = copy.deepcopy(self.laser_data['Pump']['lasers'])
                probe_lasers = copy.deepcopy(self.laser_data['Probe']['lasers'])
                lasers = [] 
                lasers.extend(pump_lasers)
                lasers.extend(probe_lasers)
                pump_data = copy.deepcopy(self.laser_data['Pump'])
                probe_data = copy.deepcopy(self.laser_data['Probe'])
                laser_tuple = add_delay_to_lasers(pump_data, probe_data,float(delay * as_to_au * 1000))

                pump_sets = laser_tuple[0]
                probe_sets = laser_tuple[1]
                laser_sets = []
                laser_sets.extend(pump_sets)
                laser_sets.extend(probe_sets)
                
                lasers_list = []
                for i,laser in enumerate(laser_sets):
                    laser_dict = laser
                    laser_dict.update({'mask': lasers[i].get('mask', None)})
                    lasers_list.append(laser_dict)  

            inp_dict.update({'laser': lasers_list,
                            'delay': delay})       
       
        self.task_info.param.clear()
        self.task_info.param.update(inp_dict)
        check = False
        try:
            self.task = self.workflow_manager.get_engine_task()
        except InputError as error_msg:
            messagebox.showerror(message= error_msg)
            return
        check = messagebox.askokcancel(title='Input parameters selected',
                         message= dict2string(inp_dict))
        if not check:
            return
        self.task.create_input()
        txt = self.task.get_engine_input()
        self.view_panel.insert_text(text=txt, state='normal')
        self.bind_task_events()

    def _on_proceed(self, *_):
        if self.workflow_manager.task_mode:
           return
        if self.task_view.inp.variable['exp_type'].get() == "Pump-Probe":            
            delays = self.delay_list
            if self.current_delay_index == len(delays):
                self.workflow_controller.next_task()
            else:
                self.workflow_controller.app.proceed_button.config(state = 'disabled')
                self.workflow_manager.next()
                self.task_view.tkraise()
                self.task_view.inp.widget["delay_values"].set(delays[self.current_delay_index])
                self.task_view.set_sub_button_state('disable')
                self.task_view.label_msg.grid_remove()
                self.current_delay_index += 1
        else:            
            self.workflow_controller.next_task()   
        
    def _on_view_lasers(self, *_):
        if len(self.laser_data) >0:
            laser_txt = self.get_laser_details()[0]
            self.view_panel.insert_text(text=laser_txt, state='normal')
        else:
            messagebox.showinfo(message='No Laser is designed.')

    def _on_save_button(self, task:Task, view, *_):
        """Modified save method for td laser"""
        template = self.view_panel.get_text()
        task.set_engine_input(template)
        task.save_input()
        # Writing laser pulses
        laser_fpath = task.task_dir / 'laser.dat'
        self.laser_controller.create_laser_file(fname= laser_fpath)
        view.set_sub_button_state('active')
        view.set_label_msg('saved')

def validate_laser_defined(laser_data:dict, exp_type:str):
    """ Validates laser_defined wrt exp_type and returns the bool"""

    check = False
    assert exp_type in ["Pump-Probe", "State Preparation"]
    laser_info = m.LaserInfo(laser_data)

    if exp_type == "Pump-Probe":
        pump_defined = laser_info.check_laser_exists('Pump')
        probe_defined = laser_info.check_laser_exists('Probe')
        if all([pump_defined, probe_defined]):
            check = True
    else: # State Preparation
        check = laser_info.check_laser_exists('State Preparation')

    return check