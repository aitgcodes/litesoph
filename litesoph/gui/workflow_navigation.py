import tkinter as tk
from tkinter import ttk
from litesoph.gui import visual_parameter as v
from litesoph.gui.visual_parameter import work_flow_ui_design, config_widget
from litesoph.common.workflows_data import predefined_workflow
_dict_task = {
    'gs' : {'task_name':'gs',
            'display_text':'Ground State'},
    'rt_tddft_delta': {'task_name':'rt_tddft_delta',
                        'display_text':'Delta Kick Perturbation'},
    'extract_dm': {'task_name':'',
                    'display_text':'Extracting Dipole Moment'},
    'process_dm': {'task_name':'',
                    'display_text':'Processing Dipole Moment'},
    'spec_calc': {'task_name':'spectrum',
                    'display_text':'Spectrum Calculation'},
    'spec_plot': {'task_name':'spectrum_plot',
                    'display_text':'Spectrum Plot'},
    'ext_field_des': {'task_name':'laser_design',
                        'display_text':'External Field Design'},
    'rt_tddft_laser': {'task_name':'rt_tddft_laser',
                       'display_text':'TD Perturbation'},
    'rt_tddft_obs': {'task_name':'',
                    'display_text':'TD Observable Analysis'},
    'ksd_calc': {'task_name':'ksd',
                    'display_text':'KSD Recipe'},
    'ksd_plot': {'task_name':'ksd_plot',
                'display_text':'KSD Plot'},
    'pop_track_calc': {'task_name':'mo_population',
                    'display_text':'Population Tracking Recipe'},
    'pop_track_plot': {'task_name':'mo_population_plot',
                    'display_text':'Population Tracking Plot'}    
}

workflows_ui_map = {'Spectrum': 'spectrum', 
                'Averaged Spectrum': 'averaged_spectrum', 
                'Kohn Sham Decomposition': 'kohn_sham_decomposition',
                'MO Population Tracking': 'mo_population_tracking'}

_workflow = {
    
    'Spectrum': ['gs', 'rt_tddft_delta','extract_dm','process_dm', 'spec_calc', 'spec_plot'],    
    'Time Dependent Calculation': ['gs', 'ext_field_des', 'rt_tddft_laser', 'rt_tddft_obs'],
    'Kohn Sham Decomposition': ['gs', 'rt_tddft_delta','extract_dm','process_dm', 'spec_calc', 'spec_plot', 'ksd_calc', 'ksd_plot'],
    'MO Population Tracking': ['gs', 'ext_field_des', 'rt_tddft_laser', 'pop_track_calc', 'pop_track_plot'],
   }

def pick_workflow(workflow_var:str):
    workflow = workflows_ui_map.get(workflow_var)
    workflow_branch =  predefined_workflow.get(workflow)['blocks']
    return workflow_branch

class WorkflowNavigation:
        
    config_done = {'background':'pale green'}
    config_current = {'background':'light yellow'}

    def __init__(self, parent, workflow_list:list) -> None:
        self.config_default = work_flow_ui_design
        self.parent = parent
        self.workflow_list = workflow_list
        self.widgets = {}
        self.current_index = -1
        self.default_state = 'default'
        self.create_widgets(parent, self.workflow_list)
           
    def create_widgets(self, parent, workflow_list:list):
        """ Creates the widgets for workflow view"""
        self.clear()
        title_label = tk.Label(parent,text='Workflow', bg=v.label_design['bg'], fg=v.label_design['fg'], font=v.myfont())
        title_label.grid(row=0, column=0)

        canvas_workflow = tk.Canvas(parent)
        canvas_workflow.grid(row=1, column=0)

        i = 0
        for task_name in workflow_list:
            self.widgets[task_name] = []
            widget= tk.Button(canvas_workflow, text = task_name, width=25)
            self.widgets[task_name].append(widget)
            self.widgets[task_name].append(self.default_state)
            config_widget(self.widgets[task_name][0], config_dict=self.config_default)
            self.widgets[task_name][0].grid(row=i, column=0, sticky='nsew', padx=5, pady=5)
            i+=3

    def _update_widgets(self, current_index:int):
        """Updates the current index and state"""
        self.current_index = current_index
        if current_index == len(self.workflow_list):
            task_item = self.workflow_list[current_index-1]
            self.widgets[task_item][1] = 'done'
        else:    
            for i in range(0, current_index):
                task_item = self.workflow_list[i]
                self.widgets[task_item][1] = 'done'
            for i in range(current_index, len(self.workflow_list)):
                task_item = self.workflow_list[i]
                self.widgets[task_item][1] = 'default'
            current_task = self.workflow_list[current_index]
            self.widgets[current_task][1] = 'current'

    def prev(self):
        """ Shifts the current state to previous"""
        if 0 < self.current_index <= len(self.workflow_list):                  
            self.current_index -= 1
        self._update_widgets(self.current_index)
        self._update_config()
        
    def next(self):
        """ Shifts the current state to next"""
        if self.current_index < len(self.workflow_list):
            self.current_index += 1
        self._update_widgets(self.current_index)
        self._update_config()
    
    def start(self, index=0):
        self.current_index = index
        self._update_widgets(self.current_index)
        self._update_config()
    
    def _update_config(self):
        """ Assigns the visual config"""
        for key,value in self.widgets.items():
            if value[1] == 'done':
                config_widget(value[0], config_dict=self.config_done)
            elif value[1] == 'current':
                config_widget(value[0], config_dict=self.config_current)
            elif value[1] == 'default':
                config_widget(value[0], config_dict=self.config_default)

    def clear(self):

        for widget in self.parent.winfo_children():
            widget.destroy()