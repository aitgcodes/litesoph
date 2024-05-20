import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox
from typing import Union
from litesoph.gui.visual_parameter import myfont
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.gui.navigation import ProjectTreeNavigation
from litesoph.gui.task_controller import TaskController
from litesoph.gui.workflow_navigation import WorkflowNavigation
from litesoph.gui.views import WorkManagerPage, CreateWorkflowPage
from litesoph.gui import actions
from litesoph.gui.workflow_controller import WorkflowController, WorkflowModeController
from litesoph.common.project_manager import ProjectManager, WorkflowSetupError
from litesoph.common.data_sturcture.data_classes import ProjectInfo
from litesoph.common.workflows_data import predefined_workflow


class ProjectController:

    def __init__(self, app) -> None:
        self.app = app
        self.engine = app.engine
        self.input_frame = app.input_frame
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.workflow_navigation_view = None
        self.project_tree_view = app.project_tree_view

    def open_project(self, project_manager: ProjectManager):
        self._bind_event_callbacks()
        self.project_manager = project_manager
        self.workflow_list = project_manager.workflow_list
        self.project_tree_view.update(self.project_manager.project_info)
        self.open_workflow()

    def _bind_event_callbacks(self):
        event_callbacks = {
            actions.CREATE_NEW_WORKFLOW : self.create_workflow_window,
            actions.OPEN_LS_VIZ : self._open_ls_viz
        }
        for event, callback in event_callbacks.items():
            self.main_window.bind_all(event, callback)          

    def open_workflow(self, workflow_uuid: str = ''):
        self.app.create_workflow_frames()
        
        if workflow_uuid:
            workflow_info = self.project_manager.get_workflow_info(workflow_uuid)
        else:
            workflow_info = self.project_manager.current_workflow_info
        
        self.app.set_title(self.project_manager.label, workflow_info.label)
        
        if workflow_info.name and not workflow_info.task_mode:
            self._create_workflow_navigation(workflow_info.name)
            self.workflow_manager = self.project_manager.open_workflow(workflow_info.uuid)
            workflow_controller = self._get_workflow_controller(workflow_info.name)
            self.workflow_controller = workflow_controller(self, self.app)
            self.workflow_controller.start(self.workflow_manager)
            return

        self.workmanager_page = self.app.show_frame(WorkManagerPage)
        self.workmanager_page.workflow_list = get_predefined_workflow()
        self.workmanager_page.button_select_geom.config(command=self._on_get_geometry_file)
        self.workmanager_page.button_view.config(command=self._on_visualize)
        
        if hasattr(self.workmanager_page, 'entry_workflow'):
            self.workmanager_page.entry_workflow['values'] = get_predefined_workflow()
        
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
            self._create_workflow_navigation(workflow, True)
    
    def _create_workflow_navigation(self, workflow, name=False):
        for widget in self.app.workflow_frame.winfo_children():
                widget.destroy()
        self.workflow_navigation_view = WorkflowNavigation(self.app.workflow_frame, get_workflow_block(workflow, name))
        
    def create_new_workflow(self):
        workflow_label = self.workflow_create_window.get_value('workflow_name')
        workflow_option = self.workflow_create_window.get_value('workflow_option')

        if workflow_option == 0:
            try:
                self.project_manager.new_workflow(workflow_label)
            except WorkflowSetupError as e:
                messagebox.showerror(title='Error creating workflow', message=e)
                return
        else:
            branch_point = self.workflow_create_window.get_value('branch_pt')
            parent_workflow = self.workflow_create_window.get_value('source_wf')
            traget_workflow_type = self.workflow_create_window.get_value('target_wf')
            parent_workflow = parent_workflow.split(':')
            branch_point = branch_point.split(':')
            try:
                self.project_manager.clone_workflow(parent_workflow[1].strip(),
                                                    traget_workflow_type,
                                                    int(branch_point[1].strip()),
                                                    workflow_label)
            except Exception as e:
                messagebox.showerror(title='Error cloning workflow', message=e)
                return
            else:
                messagebox.showinfo(title= 'Info', message= f"successfully created New workflow: {workflow_label}")
                self.workflow_create_window._var['workflow_name'].set('')
            return
        self.workflow_create_window.destroy()
        self.open_workflow()

    def open_existing_workflow(self):
        pass
    
    def remove_workflow(self):
        pass

    def update_source_workflow_entry(self, *_):
        workflow_option = self.workflow_create_window.get_value('workflow_option')

        if workflow_option == 0:
            return

        workflow_names =  [] #self.project_manager.list()
        for _, workflow in enumerate(self.project_manager.workflow_list):
            workflow_names.append(f"{workflow.label}: {workflow.uuid}")

        self.workflow_create_window.entry_wf_select.config(values=workflow_names)
        self.workflow_create_window.entry_wf_select.current(0)

    def update_branch_point_entry(self, *_):
        source_workflow = self.workflow_create_window.get_value('source_wf')
        if not source_workflow:
            return

        source_workflow = source_workflow.split(':')
        if len(source_workflow) < 2:
            return

        source_workflow_info = self.project_manager.get_workflow_info(source_workflow[1].strip())

        branch_points = []
        for i, block in enumerate(source_workflow_info.steps):
            branch_points.append(f"{block.name}: {i}")  # Ensure block has a 'name' attribute

        if branch_points:  # Check if branch_points is not empty before proceeding
            self.workflow_create_window.entry_branch_pt['values'] = branch_points
            self.workflow_create_window.entry_branch_pt.current(0)
        else:
            self.workflow_create_window.entry_branch_pt['values'] = []  # Clear values if branch_points is empty

    
    def toggle_wf_option(self, *_):
        self.workflow_create_window.toggle_wf_option()
        self.update_source_workflow_entry()
        
        traget_workflows = self.project_manager.list_available_workflows()
        self.workflow_create_window.entry_target_wf.config(values= traget_workflows)
        self.workflow_create_window.entry_target_wf.current(0)

    def create_workflow_window(self, *_):
        self.workflow_create_window = CreateWorkflowPage(self.main_window)

        self.workflow_create_window._var['workflow_option'].trace_add('write', self.toggle_wf_option)
        self.workflow_create_window._var['source_wf'].trace_add('write', self.update_branch_point_entry)
        self.workflow_create_window.create_button.config(command= self.create_new_workflow) 
    
    def _open_ls_viz(self,*_):
        project_dir= str(self.project_manager.project_info.path)
        from litesoph.visualization import ls_viz_app
        ls_viz_app.LSVizApp(self.main_window,project_dir).run()
    
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
    
    def _get_workflow_controller(self, name):
        if name == 'task_mode':
            return WorkflowController
        elif name in list(predefined_workflow.keys()):
            return WorkflowModeController
        else:
            messagebox.showerror(message=f'Workflow: {name} not implemented')

    def start_workflow(self, *_):
        workflow_info = self.project_manager.current_workflow_info
        param_view  = self.workmanager_page.get_parameters()
            
        param ={}
        for item in ['environment', 'charge', 'multiplicity', 'engine']:
            param[item] = param_view.get(item)
        
        workflow_type = param_view.pop('workflow')
        workflow_option = self.workmanager_page.get_value('select_wf_option')
        check_user_workflow = (workflow_option == 2)
        if check_user_workflow:
            workflow_type = "task_mode"
            if self.workflow_navigation_view:
                for widget in self.app.workflow_frame.winfo_children():
                    widget.destroy()
                # self.workflow_navigation_view.clear()
        else:
            workflow_type = get_workflow_type(workflow_type)

        # global gs_visible_default
        # from litesoph.gui.models.inputs import gs_visible_default
        # if param['multiplicity'] == 3:
        #     gs_visible_default['spin'] = False
        # else:
        #     gs_visible_default['spin'] = True
            
        if workflow_info.name:
            workflow_controller = self._get_workflow_controller(workflow_info.name)
            self.workflow_controller = workflow_controller(self, self.app)
            self.workflow_manager = self.project_manager.open_workflow(workflow_info.uuid)

        else:
            workflow_controller = self._get_workflow_controller(workflow_type)
            if not workflow_controller:
                return
            self.workflow_controller = workflow_controller(self, self.app)
            self.workflow_manager = self.project_manager.start_workflow(workflow_type, param) 
        
        self.workflow_controller.start(self.workflow_manager)
    
        
def get_predefined_workflow():

    workflows=[]
    for workflow in predefined_workflow:
        workflows.append(predefined_workflow[workflow]['name'])

    return workflows

def get_workflow_block(workflow, name=False):
    
    if name:
        workflow = get_workflow_type(workflow)

    blocks =  predefined_workflow.get(workflow)['blocks']
    return [block['name'] for block in blocks]

def get_workflow_type(workflow_name):
    for workflow in predefined_workflow:
        if predefined_workflow[workflow]['name'] == workflow_name:
            return workflow
