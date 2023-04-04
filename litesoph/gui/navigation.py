from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
import collections
import random
from litesoph.common.data_sturcture.data_classes import ProjectInfo


class ProjectTreeNavigation:

    def __init__(self, app):
        
        self.app = app
        self.treedata = dict()
        self.current_path_list = []
        self.project_id_logger_dict=dict()
        self.treeview = app.treeview
        self.treeview.heading('#0', text='Project and Workflows', anchor=tk.W)        
        # self.treeview.bind('<<TreeviewOpen>>', self.open_node)
        self.treeview.bind("<Double-1>", self.OnDoubleClick)
        
    def update(self, project_info: ProjectInfo):
        self.project_info = project_info
        self._update_treeview()
    
    def _update_treeview(self):
        project_name = self.project_info.label
        
        if not self.node_exists(self.project_info.uuid):
            self.treeview.insert('', 'end', iid= self.project_info.uuid,
                                        text = project_name, tags = 'project')

        for worfklow in self.project_info.workflows:
            
            if not self.node_exists(worfklow.uuid):
                self.treeview.insert(self.project_info.uuid, 'end', iid= worfklow.uuid,
                                        text= worfklow.label, tags = 'workflow')
            for task in worfklow.tasks.values():
                if self.node_exists(task.uuid):
                    continue
                self.treeview.insert(worfklow.uuid, 'end', iid= task.uuid,
                                        text= task.name, tags= 'task')

    def node_exists(self, node_id):
        try:
            node = self.treeview.item(node_id)
        except tk.TclError:
            return False
        else:
            return True
        
    def OnDoubleClick(self, event):
        item_id = self.treeview.selection()[0]
        item = self.treeview.item(item_id)
        if item['tags'][0] == 'workflow':
            self.app.project_controller.open_workflow(item_id)