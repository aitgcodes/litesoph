import tkinter as tk
from tkinter import messagebox
from typing import Union
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.common.task import (Task, TaskFailed,
                                GROUND_STATE,RT_TDDFT_DELTA,
                                RT_TDDFT_LASER, SPECTRUM,
                                TCM, MO_POPULATION,
                                MASKING)
from litesoph.common.workflow_manager import WorkflowManager
from litesoph.gui.workflow_navigation import WorkflowNavigation
from litesoph.gui import actions
from litesoph.gui.task_controller import TaskController
from litesoph.gui import views as v


task_view_map={
    GROUND_STATE: v.GroundStatePage,
    RT_TDDFT_DELTA: v.TimeDependentPage,
    RT_TDDFT_LASER: v.LaserDesignPage,
    SPECTRUM: v.PlotSpectraPage,
    TCM: v.TcmPage,
    MO_POPULATION: v.PopulationPage,
    MASKING: v.MaskingPage
}

class WorkflowController:

    def __init__(self, project_controller, app) -> None:
        self.app = app
        self.project_controller = project_controller
        self.workflow_navigation_view = project_controller.workflow_navigation_view
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.task_controller = TaskController(self,  app)
    

    def start(self, workflow_manager: WorkflowManager, param):
        self.workflow_manager = workflow_manager
        self.user_defined_workflow = self.workflow_manager.user_defined
        self.workmanager_page = self.project_controller.workmanager_page
        self.start_task()        
        

    def show_workmanager_page(self, *_):
        self.workmanager_page._var['select_wf_option'].set(value=2)
        self.workmanager_page.tkraise()
        self.app.proceed_button.config(command= self.start_task)
    
    def start_task(self, *_):
        
        task_name = None
        if self.user_defined_workflow:
            task_name = self.get_task_name()
            if not task_name:
                raise Exception('Task name not specified.') 
        else:
            if not self.workflow_navigation_view:
                return
            
        self.workflow_manager.next(task_name)
        task_info = self.workflow_manager.current_task_info
        self.task_controller.set_task(self.workflow_manager, task_view_map[task_info.name])

    def get_task_name(self) -> Union[str, None]:

        simulation_type = [('electrons', 'None', '<<event>>'),
                        ('electrons', 'Delta Pulse',RT_TDDFT_DELTA),
                        ('electrons', 'Gaussian Pulse', RT_TDDFT_LASER),
                        ('electrons', 'Customised Pulse', '<<event>>'),
                        ('electron+ion', 'None', '<<event>>'),
                        ('electron+ion', 'Delta Pulse', '<<event>>'),
                        ('electron+ion', 'Gaussian Pulse', '<<event>>'),
                        ('electron+ion', 'Customised Pulse', '<<event>>'),
                        ('ions', 'None', '<<event>>'),
                        ('ions', 'Delta Pulse', '<<event>>'),
                        ('ions', 'Gaussian Pulse', '<<event>>'),
                        ('ions', 'Customised Pulse', '<<event>>')]

        w = self.workmanager_page
        sub_task = w.get_value('sub_task')
        task = w.get_value('task')
        self.engine = w.engine.get()

        if task == '--choose job task--':
            messagebox.showerror(title='Error', message="Please choose job type")
            return

        if self.engine == 'auto-mode' and sub_task != "Ground State":
            self.app._get_engine()
            if not self.engine:
                messagebox.showerror(title= "Error", message="Please perform ground state calculation with any of the engine." )
                return

        if task == "Simulations":

            if w.get_value('dynamics') == '--dynamics type--' or w.get_value('laser') == '-- laser type--':
                messagebox.showerror(title= 'Error',message="Please select the Sub task options")
                return

            for dynamics, laser, task_name in simulation_type:
                if dynamics == w.get_value('dynamics') and laser == w.get_value('laser'):
                    if task_name == "<<event>>":
                        messagebox.showinfo(title="Info", message="Option not Implemented")
                        return
                    else:
                        return task_name
            return

        if sub_task  == "Ground State":
            return GROUND_STATE

        if sub_task in ["Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]:
            messagebox.showinfo(title='Info', message="This option is not yet Implemented.")
            return
        
        if sub_task == "Compute Spectrum":
            return SPECTRUM
            #self.main_window.event_generate(actions.SHOW_SPECTRUM_PAGE)   
        if sub_task == "Dipole Moment and Laser Pulse":
            return
        if sub_task == "Kohn Sham Decomposition":
            return TCM
            #self.main_window.event_generate(actions.SHOW_TCM_PAGE) 
        if sub_task == "Population Tracking":
            return MO_POPULATION
            #self.main_window.event_generate(actions.SHOW_MO_POPULATION_CORRELATION_PAGE)
        if sub_task == "Masking":
            return MASKING
            #self.main_window.event_generate(actions.SHOW_MASKING_PAGE) 
