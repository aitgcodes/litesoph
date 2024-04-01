import tkinter as tk
from tkinter import messagebox
from typing import Union
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list

from litesoph.common.task import Task, TaskFailed
from litesoph.common.task_manager import check_task_completion
from litesoph.common.task_data import TaskTypes as tt
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError, WorkflowEnded
from litesoph.gui.workflow_navigation import WorkflowNavigation
from litesoph.gui import actions
from litesoph.gui.task_controller import (TaskController,
                                            PostProcessTaskController,)
from litesoph.gui import views as v
from litesoph.common.task_data import (task_dependencies_map,
                                    check_properties_dependencies)
from litesoph.gui import design
from litesoph.gui import controllers as ctrl
from litesoph.gui.controllers import masking_controller, td_page


task_view_map={
    tt.GROUND_STATE: v.GroundStatePage,
    tt.RT_TDDFT: [v.TimeDependentPage, design.TDPage],
    tt.COMPUTE_SPECTRUM: v.PlotSpectraPage,
    tt.COMPUTE_AVERAGED_SPECTRUM: v.PlotSpectraPage,
    tt.TCM: v.TcmPage, 
    tt.MO_POPULATION: v.PopulationPage,
    tt.MASKING: design.MaskingPage,
    tt.COMPUTE_TAS: v.PumpProbePostProcessPage        
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
        self.task_mode_workflow = self.workflow_manager.task_mode
        self.workmanager_page = self.project_controller.workmanager_page
        self.start_task()        
        

    def show_workmanager_page(self, *_):
        self.workmanager_page._var['select_wf_option'].set(value=2)
        self.workmanager_page.tkraise()
        self.app.proceed_button.config(command= self.start_task, state = 'normal')
    
    def get_task_dependencies(self, task_name):
        
        #TODO: Function needs to be reimplemented to get only the uuids of 
        # dependent tasks
        dependencies_data = task_dependencies_map.get(task_name)
        if not dependencies_data:
            return list()

        dependent_tasks = []
        for task in dependencies_data:
            if isinstance(task, str):
                dependent_tasks.append(task)
            elif isinstance(task, dict):
                dependent_tasks.extend([key for key  in task.keys()])

        task_list = self.workflow_manager.get_taskinfo(dependent_tasks[0])
        
        completed_task_list =[]
        for task_info in task_list:
            if check_task_completion(task_info):
                completed_task_list.append(task_info)

        if not completed_task_list:
            messagebox.showwarning(message = f"Dependent task:{dependent_tasks} not done")

        check, msg = check_properties_dependencies(task_name, completed_task_list[0])
        if not check:
            messagebox.showerror(message=msg)
        
        tasks_uuids= [task_info.uuid for task_info in completed_task_list]
        return tasks_uuids

    def start_task(self, *_):
        
        task_name = None
        if self.task_mode_workflow:
            task_and_view = self._get_task()
            if not task_and_view:
                return 
        else:
            if not self.workflow_navigation_view:
                return
        task_name, task_view = task_and_view
        step_id = self.workflow_manager.current_step
        
        if not step_id:
            step_id = 0
        else:
            step_id = step_id[0] + 1

        if not self.workflow_manager.check_block(block_id=0):

            try:
                self.workflow_manager.add_block(block_id=0,
                                            name ='task mode',
                                            store_same_task_type=False)
            except TaskSetupError as e:
                messagebox.showerror(title='Error', message=e)
                return

        self.workflow_manager.add_task(task_name,
                                        block_id=0,
                                        step_id= step_id,
                                        dependent_tasks_uuid= self.get_task_dependencies(task_name))   

        try:
            self.workflow_manager.next()
        except TaskSetupError as e:
            messagebox.showinfo(title='Error', message=e)
            return

        self.task_controller = get_task_controller(task_view, self, self.app)
        self.task_controller.set_task(self.workflow_manager, task_view)
        self.app.proceed_button.config(state = 'disabled')

    def _get_task(self) -> Union[tuple, None]:

        simulation_type = [('electrons', 'None', '<<event>>'),
                        ('electrons', 'Delta Pulse',v.TimeDependentPage),
                        ('electrons', 'Multiple Pulse', design.TDPage),
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
            return (tt.MASKING, design.MaskingPage)
            #self.main_window.event_generate(actions.SHOW_MASKING_PAGE) 

    
class WorkflowModeController(WorkflowController):

    def __init__(self, project_controller, app) -> None:
        super().__init__(project_controller, app)


    def start(self, workflow_manager: WorkflowManager):
        self.workflow_manager = workflow_manager
        # self.workmanager_page = self.project_controller.workmanager_page
        self.app.proceed_button.config(command= self.next_task, state = 'disabled')
        self.start_task()        
        

    def show_workmanager_page(self, *_):
        self.workmanager_page._var['select_wf_option'].set(value=1)
        self.workmanager_page.tkraise()
        self.app.proceed_button.config(command= self.next_task, state = 'disabled')
    

    def start_task(self, *_):
        
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

    
    def next_task(self):

        try:
            self.workflow_manager.next()
        except TaskSetupError as e:
            messagebox.showerror(title='Error', message=e)
            return
        except WorkflowEnded as e:
            messagebox.showinfo(title='Info', message="All the tasks in the workflow are completed successfully.")
            block_id = self.workflow_manager.current_container.block_id
            self.workflow_navigation_view.start(block_id + 1)
            self.workflow_navigation_view.start(block_id + 2)
            return
        
        self.start_task()


def get_task_controller( task_view, workflow_controller, app) -> TaskController:
    
    if task_view == design.TDPage:
        task_controller = td_page.TDPageController
    elif task_view == design.MaskingPage:
        task_controller = masking_controller.MaskingPageController
    elif task_view in [v.PlotSpectraPage, v.TcmPage, v.PopulationPage]:
        task_controller = PostProcessTaskController
    elif task_view == v.PumpProbePostProcessPage:
        task_controller = ctrl.PumpProbePostProcessController
    else:
        task_controller = TaskController
        
    return task_controller(workflow_controller, app)