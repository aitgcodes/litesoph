import copy
import tkinter as tk
from tkinter import messagebox
from litesoph.gui.task_controller import TaskController
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError
from litesoph.gui.design import maskingpage 

class MaskingPageController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None
        self.computed = False

        try:
            self.task = self.workflow_manager.get_engine_task()
        except TaskSetupError as e:
            messagebox.showerror("Error", str(e))
            return
        
        r_list = self.get_region_tags()
        self.task_view = self.app.show_frame(task_view, self.task_info.engine, 
                            self.task_info.name, region_tags = r_list)
        
        self.task_view.energy_coupling_button.config(command = self._on_masking_page_compute)
        self.task_view.plot_button.config(command = self._on_plot_dm_file)
        self.task_view.back_button.config(command= self.workflow_controller.show_workmanager_page)

        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def get_region_tags(self):
        td_info = self.task.dependent_tasks[0]
        num_masks = len(td_info.output['dm_files'])-1
        region_list = [{'Region': 'Total'}]
        self.region_tags = ['Total']
        if num_masks > 0:
            for i in range(num_masks):
                region_i = 'Region '+ str(i+1)
                region_list.append({'Region': region_i+'(Complement)'})
                self.region_tags.append(region_i+'(Complement)')
                region_list.append({'Region': region_i+'(Masked)'})
                self.region_tags.append(region_i+'(Masked)')
        return region_list

    def get_region_id(self, region_var):
        focus = False
        i = int(region_var)
        region_id = i
        if i >0:
            if (i%2 != 0):
                region_id = (int(i)+1)/2
                focus = True
            else:
                region_id = int(i)/2
        return region_id, focus

    def _on_masking_page_compute(self, *_):
        inp_dict = self.task_view.get_parameters()
        region_vars = inp_dict.get('regions')
        axis = inp_dict.get('direction')

        if len(region_vars) == 0:
            messagebox.showerror(title='Error', message='Select the region.')
        elif len(region_vars) > 1:
            messagebox.showerror(title='Error', message='Only one region is required.')
        else:
            r_id = self.get_region_id(region_vars[0])[0]
            focus_val = self.get_region_id(region_vars[0])[1]
        try:
            txt = self.task.get_energy_coupling_constant(region_id = int(r_id),
                                        direction=axis, focus = focus_val)
            
            self.view_panel.insert_text(text= txt, state= 'disabled')
            self.computed = True
        except Exception as e:
            messagebox.showerror(title='Error', message=e)

    def _on_plot_dm_file(self, *_):
        if self.task_view.envelope_var.get() and not self.computed:
            messagebox.showwarning(title='Uh oh', message='First compute Energy Transfer Coupling Constant')
            return
        self.app.proceed_button.config(state = 'active')
        inp_dict = self.task_view.get_parameters()
        plot_region_ids = inp_dict.get('regions')
        axis = inp_dict.get('direction')
        envelope = inp_dict.get('envelope')
        
        plot_details_list = []
        plot_data = []       
        for i in plot_region_ids:
            focus = False
            region_id = int(i)
            if int(i)>0:
                if (int(i)%2 != 0):
                    region_id = (int(i)+1)/2
                    focus = True
                else:
                    region_id = int(i)/2
                    
            plot_data = (int(region_id), focus, axis, envelope)
            plot_details_list.append(plot_data)
        try:
            self.task.plot(plot_data=plot_details_list)
        except Exception as e:
            messagebox.showerror(title='Error', message=e)

