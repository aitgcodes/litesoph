import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox
from typing import Union

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
        self.workflow_frame = app.workflow_frame
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.task_input_frame = app.task_input_frame
        self.proceed_button = app.proceed_button
        self.workflow_navigation_view = None
        self.workflow_controller = WorkflowController(self, app)

    def open_project(self, project_manager: ProjectManager):
        self.project_manager = project_manager
        self.workmanager_page = self.app.show_frame(WorkManagerPage)
        self.workmanager_page.button_select_geom.config(command=self._on_get_geometry_file)
        self.workmanager_page.button_view.config(command=self._on_visualize)
        self.workmanager_page.button_proceed.config(command= self.start_workflow)
        self.workmanager_page._var['workflow'].trace_add('write', self.create_workflow_ui)
        if self.engine:
            self.workmanager_page.engine.set(self.engine)

    def create_workflow_ui(self, *_):
        
        workflow_option = self.workmanager_page.get_value('select_wf_option')
        check_show_workflow = (workflow_option == 1)

        if check_show_workflow:
            workflow  = self.workmanager_page.get_value('workflow')
            if not workflow:
                return
            for widget in self.workflow_frame.winfo_children():
                widget.destroy()
            self.workflow_navigation_view = WorkflowNavigation(self.workflow_frame, pick_workflow(workflow))

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
    
    # def _on_proceed(self, *_):

    #     simulation_type = [('electrons', 'None', '<<event>>'),
    #                     ('electrons', 'Delta Pulse',actions.SHOW_RT_TDDFT_DELTA_PAGE),
    #                     ('electrons', 'Gaussian Pulse', actions.SHOW_RT_TDDFT_LASER_PAGE),
    #                     ('electrons', 'Customised Pulse', '<<event>>'),
    #                     ('electron+ion', 'None', '<<event>>'),
    #                     ('electron+ion', 'Delta Pulse', '<<event>>'),
    #                     ('electron+ion', 'Gaussian Pulse', '<<event>>'),
    #                     ('electron+ion', 'Customised Pulse', '<<event>>'),
    #                     ('ions', 'None', '<<event>>'),
    #                     ('ions', 'Delta Pulse', '<<event>>'),
    #                     ('ions', 'Gaussian Pulse', '<<event>>'),
    #                     ('ions', 'Customised Pulse', '<<event>>')]

    #     w = self.workmanager_page
    #     sub_task = w.get_value('sub_task')
    #     task = w.get_value('task')
    #     workflow_option = w.get_value('select_wf_option')
    #     check_show_workflow = (workflow_option == 1)
    #     self.engine = w.engine.get()

    #     if check_show_workflow:
    #         workflow  = w.get_value('workflow')
    #         if workflow:
    #             self.create_workflow_ui(workflow)
    #         return
            
    #     if task == '--choose job task--':
    #         messagebox.showerror(title='Error', message="Please choose job type")
    #         return

    #     if self.engine == 'auto-mode' and sub_task != "Ground State":
    #         self.app._get_engine()
    #         if not self.engine:
    #             messagebox.showerror(title= "Error", message="Please perform ground state calculation with any of the engine." )
    #             return

    #     if task == "Simulations":

    #         if w.get_value('dynamics') == '--dynamics type--' or w.get_value('laser') == '-- laser type--':
    #             messagebox.showerror(title= 'Error',message="Please select the Sub task options")
    #             return

    #         for dynamics, laser, event in simulation_type:
    #             if dynamics == w.get_value('dynamics') and laser == w.get_value('laser'):
    #                 if event == "<<event>>":
    #                     messagebox.showinfo(title="Info", message="Option not Implemented")
    #                     return
    #                 else:
    #                     self.main_window.event_generate(event)
    #         return

    #     if sub_task  == "Ground State":
    #         if self.project_manager.check_geometry():
    #             self.main_window.event_generate(actions.SHOW_GROUND_STATE_PAGE)
    #         else:
    #             messagebox.showerror(title = 'Error', message= "Upload geometry file")
    #             return
    #         return

    #     if sub_task in ["Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]:
    #         messagebox.showinfo(title='Info', message="This option is not yet Implemented.")
    #         return
        
    #     elif sub_task == "Compute Spectrum":
    #         self.main_window.event_generate(actions.SHOW_SPECTRUM_PAGE)   
    #     elif sub_task == "Dipole Moment and Laser Pulse":
    #         self.main_window.event_generate('')
    #     elif sub_task == "Kohn Sham Decomposition":
    #            self.main_window.event_generate(actions.SHOW_TCM_PAGE) 
    #     elif sub_task == "Population Tracking":
    #            self.main_window.event_generate(actions.SHOW_MO_POPULATION_CORRELATION_PAGE)
    #     elif sub_task == "Masking":
    #         self.main_window.event_generate(actions.SHOW_MASKING_PAGE) 

    #     w.refresh_var()