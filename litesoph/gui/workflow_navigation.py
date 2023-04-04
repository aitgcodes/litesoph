import tkinter as tk
from tkinter import ttk
from litesoph.gui import visual_parameter as v
from litesoph.gui.visual_parameter import work_flow_ui_design, config_widget


class WorkflowNavigation:
        
    config_done = {'background':'pale green'}
    config_current = {'background':'light yellow'}

    def __init__(self, parent, workflow_list:list) -> None:
        #self.config_default = work_flow_ui_design
        self.parent = parent
        self.workflow_list = workflow_list
        self.widgets = {}
        self.current_index = -1
        self.default_state = 'default'
        v.set_wf_style()
        self.create_widgets(parent, self.workflow_list)
           
    def create_widgets(self, parent, workflow_list:list):
        """ Creates the widgets for workflow view"""
        self.clear()
        title_label = tk.Label(parent,text='Workflow', bg=v.label_design['bg'], fg=v.label_design['fg'], font=v.myfont())
        title_label.grid(row=0, column=0)

        canvas_workflow = tk.Canvas(parent)
        canvas_workflow.grid(row=1, column=0)

        i = 0
        for n ,task_name in enumerate(workflow_list):
            self.widgets[str(n)] = []
            # widget= tk.Button(canvas_workflow, text = task_name, width=25)
            widget= ttk.Label(canvas_workflow, text = str(task_name), 
                            width=25, padding=(5, 5, 5, 5), borderwidth=1)
            self.widgets[str(n)].append(widget)
            self.widgets[str(n)].append(self.default_state)
            self.widgets[str(n)][0].configure(style= 'Default.Wf.TLabel')
            # config_widget(self.widgets[str(n)][0], config_dict=self.config_default)
            self.widgets[str(n)][0].grid(row=i, column=0, sticky='nsew', padx=5, pady=5)
            i+=3

    def _update_widgets(self, current_index:int):
        """Updates the current index and state"""
        self.current_index = current_index
        if current_index == len(self.workflow_list):
            # task_item = self.workflow_list[current_index-1]
            self.widgets[str(current_index-1)][1] = 'done'
        else:    
            for i in range(0, current_index):
                task_item = self.workflow_list[i]
                self.widgets[str(i)][1] = 'done'
            for i in range(current_index, len(self.workflow_list)):
                task_item = self.workflow_list[i]
                self.widgets[str(i)][1] = 'default'
            current_task = self.workflow_list[current_index]
            self.widgets[str(current_index)][1] = 'current'

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
                value[0].configure(style= 'Done.Wf.TLabel')
                # config_widget(value[0], config_dict=self.config_done)
            elif value[1] == 'current':
                value[0].configure(style= 'Current.Wf.TLabel')
                # config_widget(value[0], config_dict=self.config_current)
            elif value[1] == 'default':
                value[0].configure(style= 'Default.Wf.TLabel')
                # config_widget(value[0], config_dict=self.config_default)

    def clear(self):

        for widget in self.parent.winfo_children():
            widget.destroy()