from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from typing import OrderedDict
import tkinter as tk
import pygubu

import pathlib 


#---LITESOPH modules
from litesoph.gui.visual_parameter import myfont, create_design_feature
from litesoph.gui.logpanel import LogPanelManager
from litesoph.gui.menubar import get_main_menu_for_os
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list
from litesoph.gui.viewpanel import ViewPanelManager
from litesoph.common.ls_manager import LSManager 
from litesoph.common.project_manager import ProjectManager
from litesoph.common import models as m
from litesoph.gui.project_controller import ProjectController
from litesoph.gui import views as v
from litesoph.gui.views import StartPage
from litesoph.gui import actions
from litesoph.common.task import Task, TaskFailed
from litesoph.gui.navigation import ProjectTreeNavigation
from litesoph import about_litesoph


TITLE_FONT = ("Helvetica", 18, "bold")

DESINGER_DIR = pathlib.Path(__file__).parent

class GUIAPP:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.builder = pygubu.Builder()

        self.builder.add_from_file(str(DESINGER_DIR / "main_window.ui"))

        self.main_window = self.builder.get_object('mainwindow')

        menu_class = get_main_menu_for_os('Linux')
        menu = menu_class(self.main_window)
        self.main_window.config(menu=menu)

        self.treeview = self.builder.get_object('treeview1')

        self.input_frame = self.builder.get_object('inputframe')

        create_design_feature()

        self.project_window = None

        # self.navigation = ProjectList(self)
        self.project_tree_view = ProjectTreeNavigation(self)
        self.view_panel = ViewPanelManager(self)
        self.ls_manager = LSManager()
        self.curent_project_manager = None
        self.engine = None

        self.setup_bottom_panel()

        self.status_engine = self.builder.get_variable('cengine_var')
        self.status_engine.set('')
        
        self.builder.connect_callbacks(self)

        
        self.laser_design = None

        self._frames = OrderedDict()
        
        self.project_controller = ProjectController(self)

        #self._show_page_events()
        self._bind_event_callbacks()
        self.show_start_page()
        self.main_window.after(5000, self.save_data_repeat)
        self.main_window.after(1000, self.update_project_tree)

    def run(self):
        self.main_window.protocol("WM_DELETE_WINDOW", self.__on_window_close)
        self.main_window.mainloop()

    def __on_window_close(self):
        """Manage WM_DELETE_WINDOW protocol."""
        self.save_data()
        self.main_window.withdraw()
        self.main_window.destroy()

    def quit(self):
        """Exit the app if it is ready for quit."""
        self.__on_window_close()

    def setup_bottom_panel(self):

        self.log_panel = LogPanelManager(self)

    def save_data_repeat(self):
        self.save_data()
        self.main_window.after(30000, self.save_data_repeat)

    def save_data(self):
        self.ls_manager.save()

    def update_project_tree(self):
        if self.curent_project_manager:
            self.project_tree_view.update(self.curent_project_manager.project_info)
        self.main_window.after(1000, self.update_project_tree)
        
    def on_bpanel_button_clicked(self):
        self.log_panel.on_bpanel_button_clicked()

    def set_title(self, project_name = None, workflow_name = None):
        title = 'LITESOPH'

        if project_name:
            title = project_name + '-' + title

        if workflow_name:
            title = workflow_name + '-' + title
        
        self.main_window.wm_title(title)


    def _refresh_config(self,*_):
        """reads and updates the lsconfig object from lsconfig.ini"""
        self.ls_manager.read_lsconfig()

    def create_workflow_frames(self):

        for widget in self.input_frame.winfo_children():
            widget.destroy()

        self.task_input_frame = ttk.Frame(self.input_frame)
        self.task_input_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.workflow_frame = ttk.Frame(self.input_frame)
        self.workflow_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.proceed_button_frame = ttk.Frame(self.input_frame)
        self.proceed_button_frame.pack(fill=tk.BOTH, side=tk.BOTTOM)

        self.proceed_button = tk.Button(self.proceed_button_frame, text="Proceed",activebackground="#78d6ff")
        self.proceed_button['font'] = myfont()
        self.proceed_button.pack(side=tk.RIGHT, padx=10)
    
    def show_start_page(self):
        start_page = StartPage(self.input_frame)
        start_page.button_create_project.config(command= self.create_project_window)
        start_page.button_open_project.config(command= self._on_open_project)
        start_page.button_about_litesoph.config(command= about_litesoph)
        start_page.grid(row=0, column=0, sticky='NSEW')

    def show_frame(self, frame,*args, **kwargs):
        
        # for widget in self.task_input_frame.winfo_children():
        #     widget.destroy()
        int_frame = frame(self.task_input_frame, *args, **kwargs)
        int_frame.grid(row=0, column=0, sticky ='NSEW')
        int_frame.tkraise()

        return int_frame


    def _bind_event_callbacks(self):
        """binds events and specific callback functions"""
        event_callbacks = {
            actions.GET_MOLECULE : self.project_controller._on_get_geometry_file,
            actions.VISUALIZE_MOLECULE: self.project_controller._on_visualize,
            actions.CREATE_PROJECT_WINDOW:self.create_project_window,
            actions.OPEN_PROJECT : self._on_open_project,
            #actions.ON_PROCEED : self.project_controller._on_proceed,
            actions.REFRESH_CONFIG : self._refresh_config,
        }

        for event, callback in event_callbacks.items():
            self.main_window.bind_all(event, callback)                
    
    def _show_workmanager_page(self, *_):

        self.show_frame(v.WorkManagerPage)
        if self.engine:
            self._frames[v.WorkManagerPage].engine.set(self.engine)

        self.show_project_summary()

    def _init_project(self, path):
        
        self.show_project_summary()
        update_proj_list(path)
        # self.navigation.create_project(path.name)
        

    def _on_open_project(self, *_):
        """creates dialog to get project path and opens existing project"""
        project_path = filedialog.askdirectory(title= "Select the existing Litesoph Project")
        if not project_path:
            return

        try:
            self.curent_project_manager = self.ls_manager.open_project(pathlib.Path(project_path))
        except Exception as e:
            messagebox.showerror(title='Error', message = 'Unable open Project', detail =e)
            return
        self._init_project(pathlib.Path(project_path))
        self.show_project(self.curent_project_manager)
        
    def create_project_window(self, *_):
        self.project_window = v.CreateProjectPage(self.main_window)
        self.project_window.button_project.config(command= self._on_create_project)   
        
    def _on_create_project(self, *_):
        """Creates a new litesoph project"""
        
        if not self.project_window:
            return

        project_name = self.project_window.get_value('proj_name')
        
        if not project_name:
            messagebox.showerror(title='Error', message='Please set the project name.')
            return

        project_path = filedialog.askdirectory(title= "Select the directory to create Litesoph Project")
        
        if not project_path:
            return

        project_path = pathlib.Path(project_path) / project_name
        
        try:
            self.curent_project_manager = self.ls_manager.new_project(project_path.name, project_path.parent)
        except PermissionError as e:
            messagebox.showerror(title='Error', message = 'Premission denied', detail = e)
        except FileExistsError as e:
            messagebox.showerror(title='Error', message = 'Project already exists', detail =e)
        except Exception as e:
            messagebox.showerror(title='Error', message = 'Unknown problem', detail =e)
        else:
            self._init_project(project_path)
            self.engine = None
            self.project_window.destroy()
            self.show_project(self.curent_project_manager)
                

    def show_project(self, project_manager: ProjectManager):
        self.project_controller.open_project(project_manager)
        self.set_title(project_manager.label, project_manager.current_workflow_info.label)
    
    def show_project_summary(self):
        summary = self.ls_manager.get_project_summary()
        self.view_panel.insert_text(summary, state='disabled')

    @staticmethod
    def _check_task_run_condition(task, network=False) -> bool:
        
        try:
           task.check_prerequisite(network)           
        except FileNotFoundError as e:
            return False
        else:
            return True

        
def main():
    app = GUIAPP()
    app.run()

#--------------------------------------------------------------------------------        
if __name__ == '__main__':
    main()
