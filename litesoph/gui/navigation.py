from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
import collections
import random

class ProjectList:

    def __init__(self, app):
        
        self.treedata = dict()
        self.current_path_list = []
        self.project_id_logger_dict=dict()
        self.treeview = app.treeview
        self.treeview.heading('#0', text='Project and Workflows', anchor=tk.W)        
        self.treeview.bind('<<TreeviewOpen>>', self.open_node)
        self.treeview.bind("<Double-1>", self.OnDoubleClick)
        
    def populate(self, project_path: Path):
        return self.treedata

    def insert_node(self, parent, text, abspath):
        node = self.treeview.insert(parent, 'end', text=text, open=False)
        if Path.is_dir(abspath):
            self.treedata[node] = abspath
            self.treeview.insert(node, 'end')

    def open_node(self, event):
        node = self.treeview.focus()
        abspath = self.treedata.pop(node, None)
        if abspath:
            self.treeview.delete(self.treeview.get_children(node))
            for p in Path.iterdir(abspath):
                self.insert_node(node, p.name, Path.joinpath(abspath, p))

    def uid_gen(self, id_type:str):
        """generate 3 digit id for project and 4 digit id for workflow"""
            
        if id_type=="pid":
            id = random.randint(111,999)    
        elif id_type=="wid":
            id=random.randint(1111,9999)
        return id

    def create_project(self, project_name:str):
        """function to add project to treeview"""

        if project_name in self.project_id_logger_dict.keys():
            print(f"{project_name} already present")
        else:
            project_id= self.uid_gen('pid')
            self.project_id_logger_dict[project_name]={}
            self.project_id_logger_dict[project_name]["project_id"]=project_id
            self.project_id_logger_dict[project_name]["workflows"]={}                        
            self.treeview.insert('', 'end', text=project_name,iid=project_id, open=False)
    
    def delete_project(self, project_name:str):
        """function to delete project to treeview"""

        if project_name in self.project_id_logger_dict.keys():
            project_id= self.project_id_logger_dict[project_name]["project_id"]
            self.treeview.delete(project_id)
        else:
            print(f"project {project_name}  does not exist ")

    def create_workflow(self, project_name:str, workflow_name:str):
        """adding workflow to under project in treeview"""

        if project_name in self.project_id_logger_dict.keys():

            if workflow_name in self.project_id_logger_dict[project_name]['workflows'].keys():
                print(f"{workflow_name} already present in project {project_name}")        
            else:        
                project_id= self.project_id_logger_dict[project_name]['project_id']
                workflow_id=self.uid_gen('wid')
                workflow_position=workflow_id
                self.project_id_logger_dict[project_name]["workflows"][workflow_name]=workflow_id        
                self.treeview.insert('', 'end', text=workflow_name,iid=workflow_id, open=False)
                self.treeview.move(workflow_id, project_id, workflow_position)
        else:
            print(f"{project_name} does not, please create {project_name} first")


    def delete_workflow(self, project_name:str, workflow_name:str):
        """deleting workflow  under project in treeview"""

        if project_name in self.project_id_logger_dict.keys():
            if workflow_name in self.project_id_logger_dict[project_name]['workflows'].keys():
                workflow_id= self.project_id_logger_dict[project_name]["workflows"][workflow_name]
                self.treeview.delete(workflow_id)
            else: 
                print(f"{workflow_name} doesn't exist in {project_name}")
        else:
            print(f"{project_name} doesn't exist for {workflow_name}")

    def OnDoubleClick(self, event):
        item = self.treeview.selection()[0]
        print("you clicked on", self.treeview.item(item,"text"))

def compare_list(list1,list2):
        if(collections.Counter(list1)==collections.Counter(list2)):
            return True
        else:
            return False
