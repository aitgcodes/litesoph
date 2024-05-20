import tkinter as tk
from tkinter import messagebox
import copy
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError
from litesoph.gui.task_controller import TaskController


class PumpProbePostProcessController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        try:
            self.task = self.workflow_manager.get_engine_task()
        except TaskSetupError as e:
            messagebox.showerror("Error", str(e))
            return
            
        self.task_view = self.app.show_frame(task_view)
        
        self.task_view.button_compute.config(command = self._on_compute_tas)
        self.task_view.button_plot.config(command = self._on_plot_tas)
        # self.task_view.back_button.config()


        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def _on_compute_tas(self, *_):
        inp_dict = self.task_view.get_parameters()
        try:
            self.task.generate_spectrums(**inp_dict)
            self.task.generate_tas_data()
            self.app.proceed_button.config(state='active')
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')
        else:
            messagebox.showinfo(message='Spectrums generated successfully.')


    def _on_plot_tas(self, *_):
        inp_dict = self.task_view.get_plot_parameters()
        try:
            self.task.plot(**inp_dict)
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')