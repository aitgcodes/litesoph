import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox
from typing import Union
from litesoph.gui.visual_parameter import myfont
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.gui.task_controller import TaskController
from litesoph.gui.workflow_navigation import WorkflowNavigation, pick_workflow
from litesoph.gui.views import WorkManagerPage
from litesoph.gui import actions
from litesoph.gui.workflow_controller import WorkflowController
from litesoph.common.project_manager import ProjectManager
from litesoph.common.data_sturcture.data_classes import ProjectInfo

class ProjectController:

    def __init__(self, app) -> None:
        self.app = app
        self.engine = app.engine
        self.input_frame = app.input_frame
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.workflow_navigation_view = None
        self.workflow_controller = WorkflowController(self, app)

    def open_project(self, project_manager: ProjectManager):
        self.project_manager = project_manager
        self.app.create_workflow_frames()
        self.workmanager_page = self.app.show_frame(WorkManagerPage)
        self.workmanager_page.button_select_geom.config(command=self._on_get_geometry_file)
        self.workmanager_page.button_view.config(command=self._on_visualize)
        self.workmanager_page._var['workflow'].trace_add('write', self.create_workflow_ui)
        self.app.proceed_button.config(command= self.start_workflow)
        if self.engine:
            self.workmanager_page.engine.set(self.engine)

    def create_workflow_ui(self, *_):
        
        workflow_option = self.workmanager_page.get_value('select_wf_option')
        check_show_workflow = (workflow_option == 1)

        if check_show_workflow:
            workflow  = self.workmanager_page.get_value('workflow')
            if not workflow:
                return
            for widget in self.app.workflow_frame.winfo_children():
                widget.destroy()
            self.workflow_navigation_view = WorkflowNavigation(self.app.workflow_frame, pick_workflow(workflow))

    def create_new_workflow(self):
        label = 'yes'
        self.project_manager.new_workflow(label)

    def open_existing_workflow(self):
        pass
    
    def remove_workflow(self):
        pass

    def _on_get_geometry_file(self, *_):
        """creates dialog to get geometry file and copies the file to project directory as coordinate.xyz"""
        try:
            geometry_file = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=[(" Text Files", "*.xyz")])
        except Exception as e:
            return
        else:
            if geometry_file:
                self.project_manager.add_geometry(Path(geometry_file))
                self.workmanager_page.show_upload_label()

    def _on_visualize(self, *_):
        """ Calls an user specified visualization tool """
        try:
            self.project_manager.visualize_geometry()
        except Exception as e:
            msg = "Cannot visualize molecule."
            messagebox.showerror(title='Error', message=msg, detail=e) 

    def start_workflow(self, *_):
        
        param_view  = self.workmanager_page.get_parameters()
        
        param ={}
        for item in ['environment', 'charge', 'multiplicity', 'engine']:
            param[item] = param_view.get(item)
        
        workflow_type = param_view.pop('workflow')
        workflow_option = self.workmanager_page.get_value('select_wf_option')
        check_user_workflow = (workflow_option == 2)
        if check_user_workflow:
            workflow_type = "user_defined"
            if self.workflow_navigation_view:
                self.workflow_navigation_view.clear()
        self.workflow_manager = self.project_manager.start_workflow(workflow_type, param) 
        self.workflow_controller.start(self.workflow_manager, param_view)
    