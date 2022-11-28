import tkinter as tk
from tkinter import messagebox
from typing import Union
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.common.task import Task, TaskFailed
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError, WorkflowEnded
from litesoph.gui.workflow_navigation import WorkflowNavigation
from litesoph.gui import actions
from litesoph.gui.task_controller import (TaskController,
                                            LaserPageController,
                                            PostProcessTaskController,
                                            MaskingPageController)
from litesoph.gui import views as v


task_view_map={
    tt.GROUND_STATE: v.GroundStatePage,
    tt.RT_TDDFT: [v.TimeDependentPage, v.LaserDesignPage],
    tt.COMPUTE_SPECTRUM: v.PlotSpectraPage,
    tt.COMPUTE_AVERAGED_SPECTRUM: v.PlotSpectraPage,
    tt.TCM: v.TcmPage, 
    tt.MO_POPULATION: v.PopulationPage,
    tt.MASKING: v.MaskingPage,
}

class WorkflowController:

    def __init__(self, project_controller, app) -> None:
        self.app = app
        self.project_controller = project_controller
        self.workflow_navigation_view = project_controller.workflow_navigation_view
        self.main_window = app.main_window
        self.view_panel = app.view_panel

        
    def start(self, workflow_manager: WorkflowManager):
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
            task_and_view = self._get_task()
            if not task_and_view:
                return 
        else:
            if not self.workflow_navigation_view:
                return
        task_name, task_view = task_and_view   
        self.workflow_manager.next(task_name)

        self.task_controller = get_task_controller(task_view, self, self.app)
        
        self.task_controller.set_task(self.workflow_manager, task_view)

    def _get_task(self) -> Union[tuple, None]:

        simulation_type = [('electrons', 'None', '<<event>>'),
                        ('electrons', 'Delta Pulse',v.TimeDependentPage),
                        ('electrons', 'Gaussian Pulse', v.LaserDesignPage),
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

            for dynamics, laser, task_view in simulation_type:
                if dynamics == w.get_value('dynamics') and laser == w.get_value('laser'):
                    if task_view == "<<event>>":
                        messagebox.showinfo(title="Info", message="Option not Implemented")
                        return
                    else:
                        return (tt.RT_TDDFT, task_view)
            return

        if sub_task  == "Ground State":
            return (tt.GROUND_STATE, v.GroundStatePage)

        if sub_task in ["Induced Density Analysis","Generalised Plasmonicity Index", "Plot"]:
            messagebox.showinfo(title='Info', message="This option is not yet Implemented.")
            return
        
        if sub_task == "Compute Spectrum":
            return (tt.COMPUTE_SPECTRUM, v.PlotSpectraPage)
            #self.main_window.event_generate(actions.SHOW_SPECTRUM_PAGE)   
        if sub_task == "Dipole Moment and Laser Pulse":
            return
        if sub_task == "Kohn Sham Decomposition":
            return (tt.TCM, v.TcmPage)
            #self.main_window.event_generate(actions.SHOW_TCM_PAGE) 
        if sub_task == "Population Tracking":
            return (tt.MO_POPULATION, v.PopulationPage)
            #self.main_window.event_generate(actions.SHOW_MO_POPULATION_CORRELATION_PAGE)
        if sub_task == "Masking":
            return (tt.MASKING, v.MaskingPage)
            #self.main_window.event_generate(actions.SHOW_MASKING_PAGE) 

    
class WorkflowModeController(WorkflowController):

    def __init__(self, project_controller, app) -> None:
        super().__init__(project_controller, app)

    def start(self, workflow_manager: WorkflowManager):
        self.workflow_manager = workflow_manager
        # self.workmanager_page = self.project_controller.workmanager_page
        self.app.proceed_button.config(command= self.start_task)
        
        self.start_task()        
        

    def show_workmanager_page(self, *_):
        self.workmanager_page._var['select_wf_option'].set(value=1)
        self.workmanager_page.tkraise()
        self.app.proceed_button.config(command= self.start_task)
    
    def start_task(self, *_):
        
        try:
            self.workflow_manager.next()
        except TaskSetupError as e:
            messagebox.showerror(title='Error', message=e)
            return
        except WorkflowEnded as e:
            messagebox.showinfo(title='Info', message="All the tasks in the workflow are completed successfully.")
            block_id = self.workflow_manager.current_container.block_id
            self.workflow_navigation_view.start(block_id + 1)
            return
        
        task_view = task_view_map.get(self.workflow_manager.current_task_info.name)

        if isinstance(task_view, list):
            env_param = self.workflow_manager.current_container.env_parameters
            laser_option = env_param.get('laser', None)
            if laser_option:
                task_view = task_view[1]
            else:
                task_view = task_view[0]

        self.task_controller = get_task_controller(task_view, self, self.app)

        block_id = self.workflow_manager.current_container.block_id
        self.workflow_navigation_view.start(block_id)
        self.task_controller.set_task(self.workflow_manager, task_view)


def get_task_controller( task_view, workflow_controller, app) -> TaskController:
    
    if task_view == v.LaserDesignPage:
        task_controller = LaserPageController
    elif task_view == v.MaskingPage:
        task_controller = MaskingPageController
    elif task_view in [v.PlotSpectraPage, v.TcmPage, v.PopulationPage]:
        task_controller = PostProcessTaskController
    else:
        task_controller = TaskController
        
    return task_controller(workflow_controller, app)